#include "matchmaking/matchmaking_coordinator.hpp"

#include <cassert>

using ds2online::matchmaking::CoordinatorResult;
using ds2online::matchmaking::MatchmakingCoordinator;
using ds2online::matchmaking::SessionRegistry;
using ds2online::presence::PresenceRegistry;

int main() {
    PresenceRegistry presence;
    SessionRegistry sessions;
    MatchmakingCoordinator coordinator(presence, sessions, 30);

    assert(coordinator.Create(1, 4, 100).result == CoordinatorResult::PlayerOffline);
    assert(coordinator.Create(0, 4, 100).result == CoordinatorResult::InvalidPlayer);
    assert(coordinator.Create(1, 0, 100).result == CoordinatorResult::InvalidCapacity);

    assert(presence.MarkOnline(1, 100));
    assert(presence.MarkOnline(2, 100));
    assert(presence.MarkOnline(3, 60));

    const auto created = coordinator.Create(1, 2, 100);
    assert(created.result == CoordinatorResult::Ok);
    assert(created.session_id.has_value());

    assert(coordinator.Join(*created.session_id, 2, 100) == CoordinatorResult::Ok);
    assert(coordinator.Join(*created.session_id, 3, 100) == CoordinatorResult::PlayerOffline);
    assert(coordinator.Join(*created.session_id, 4, 100) == CoordinatorResult::PlayerOffline);
    assert(coordinator.Join(*created.session_id, 2, 100) == CoordinatorResult::AlreadyInSession);
    assert(coordinator.Join(999, 2, 100) == CoordinatorResult::SessionNotFound);
    assert(coordinator.Leave(*created.session_id, 2) == CoordinatorResult::Ok);

    assert(presence.MarkOnline(3, 101));
    assert(coordinator.Join(*created.session_id, 3, 101) == CoordinatorResult::Ok);
    assert(coordinator.Join(*created.session_id, 4, 101) == CoordinatorResult::PlayerOffline);
    assert(coordinator.Leave(*created.session_id, 1) == CoordinatorResult::Ok);
    assert(!sessions.Find(*created.session_id).has_value());
    assert(!sessions.FindPlayerSession(3).has_value());
    return 0;
}

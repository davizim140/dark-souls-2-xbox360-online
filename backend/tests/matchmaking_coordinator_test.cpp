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

    // A normal member disconnect is removed from both registries.
    const auto second = coordinator.Create(1, 3, 102);
    assert(second.result == CoordinatorResult::Ok);
    assert(coordinator.Join(*second.session_id, 2, 102) == CoordinatorResult::Ok);
    const auto member_disconnect = coordinator.Disconnect(2);
    assert(member_disconnect.presence_removed);
    assert(member_disconnect.session_result == CoordinatorResult::Ok);
    assert(!presence.FindActive(2, 102, 30).has_value());
    const auto remaining = sessions.Find(*second.session_id);
    assert(remaining.has_value());
    assert(remaining->members.size() == 1);

    // Host disconnect closes the session and removes every membership.
    const auto host_disconnect = coordinator.Disconnect(1);
    assert(host_disconnect.presence_removed);
    assert(host_disconnect.session_result == CoordinatorResult::Ok);
    assert(!sessions.Find(*second.session_id).has_value());
    assert(!sessions.FindPlayerSession(1).has_value());
    assert(!sessions.FindPlayerSession(2).has_value());

    const auto repeated = coordinator.Disconnect(1);
    assert(!repeated.presence_removed);
    assert(!repeated.session_result.has_value());
    assert(!coordinator.Disconnect(0).presence_removed);
    return 0;
}

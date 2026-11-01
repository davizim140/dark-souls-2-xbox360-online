#include "matchmaking/session_registry.hpp"

#include <cassert>

using ds2online::matchmaking::SessionRegistry;
using ds2online::matchmaking::SessionResult;

int main() {
    SessionRegistry registry;

    assert(!registry.Create(0).has_value());
    assert(!registry.Create(10, 0).has_value());
    assert(!registry.Create(10, 17).has_value());

    const auto session = registry.Create(10, 2);
    assert(session.has_value());
    assert(registry.FindPlayerSession(10) == session);

    assert(registry.Join(*session, 0) == SessionResult::InvalidPlayer);
    assert(registry.Join(*session, 10) == SessionResult::AlreadyInSession);
    assert(registry.Join(*session, 20) == SessionResult::Ok);
    assert(registry.Join(*session, 30) == SessionResult::SessionFull);
    assert(registry.FindPlayerSession(20) == session);

    const auto snapshot = registry.Find(*session);
    assert(snapshot.has_value());
    assert(snapshot->host == 10);
    assert(snapshot->capacity == 2);
    assert(snapshot->members.size() == 2);
    assert(snapshot->members[0] == 10);
    assert(snapshot->members[1] == 20);

    assert(registry.Leave(*session, 99) == SessionResult::NotMember);
    assert(registry.Leave(*session, 20) == SessionResult::Ok);
    assert(!registry.FindPlayerSession(20).has_value());

    assert(registry.Join(*session, 30) == SessionResult::Ok);
    assert(registry.Leave(*session, 10) == SessionResult::Ok);
    assert(!registry.Find(*session).has_value());
    assert(!registry.FindPlayerSession(30).has_value());

    assert(registry.Join(*session, 40) == SessionResult::SessionNotFound);
    return 0;
}

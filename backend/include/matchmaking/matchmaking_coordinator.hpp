#pragma once

#include "matchmaking/session_registry.hpp"
#include "presence/presence_registry.hpp"

#include <cstddef>
#include <optional>

namespace ds2online::matchmaking {

enum class CoordinatorResult {
    Ok,
    PlayerOffline,
    InvalidPlayer,
    InvalidCapacity,
    SessionNotFound,
    AlreadyInSession,
    SessionFull,
    NotMember
};

struct CreateSessionOutcome {
    CoordinatorResult result = CoordinatorResult::InvalidPlayer;
    std::optional<SessionId> session_id;
};

// Coordinates in-memory presence and session primitives. Presence is checked
// at operation time; this is not an atomic distributed transaction.
class MatchmakingCoordinator {
public:
    MatchmakingCoordinator(presence::PresenceRegistry& presence,
                           SessionRegistry& sessions,
                           presence::UnixSeconds presence_timeout)
        : presence_(presence), sessions_(sessions),
          presence_timeout_(presence_timeout) {}

    CreateSessionOutcome Create(PlayerId host, std::size_t capacity,
                                presence::UnixSeconds now) {
        if (host == 0) return {CoordinatorResult::InvalidPlayer, std::nullopt};
        if (capacity == 0 || capacity > 16) {
            return {CoordinatorResult::InvalidCapacity, std::nullopt};
        }
        if (!IsOnline(host, now)) {
            return {CoordinatorResult::PlayerOffline, std::nullopt};
        }
        const auto id = sessions_.Create(host, capacity);
        if (!id) return {CoordinatorResult::AlreadyInSession, std::nullopt};
        return {CoordinatorResult::Ok, id};
    }

    CoordinatorResult Join(SessionId session, PlayerId player,
                           presence::UnixSeconds now) {
        if (player == 0) return CoordinatorResult::InvalidPlayer;
        if (!IsOnline(player, now)) return CoordinatorResult::PlayerOffline;
        switch (sessions_.Join(session, player)) {
            case SessionResult::Ok: return CoordinatorResult::Ok;
            case SessionResult::InvalidPlayer: return CoordinatorResult::InvalidPlayer;
            case SessionResult::SessionNotFound: return CoordinatorResult::SessionNotFound;
            case SessionResult::AlreadyInSession: return CoordinatorResult::AlreadyInSession;
            case SessionResult::SessionFull: return CoordinatorResult::SessionFull;
            case SessionResult::InvalidCapacity: return CoordinatorResult::InvalidCapacity;
            case SessionResult::NotMember: return CoordinatorResult::NotMember;
        }
        return CoordinatorResult::SessionNotFound;
    }

    CoordinatorResult Leave(SessionId session, PlayerId player) {
        switch (sessions_.Leave(session, player)) {
            case SessionResult::Ok: return CoordinatorResult::Ok;
            case SessionResult::InvalidPlayer: return CoordinatorResult::InvalidPlayer;
            case SessionResult::SessionNotFound: return CoordinatorResult::SessionNotFound;
            case SessionResult::AlreadyInSession: return CoordinatorResult::AlreadyInSession;
            case SessionResult::SessionFull: return CoordinatorResult::SessionFull;
            case SessionResult::InvalidCapacity: return CoordinatorResult::InvalidCapacity;
            case SessionResult::NotMember: return CoordinatorResult::NotMember;
        }
        return CoordinatorResult::SessionNotFound;
    }

private:
    bool IsOnline(PlayerId player, presence::UnixSeconds now) const {
        return presence_timeout_ > 0 &&
               presence_.FindActive(player, now, presence_timeout_).has_value();
    }

    presence::PresenceRegistry& presence_;
    SessionRegistry& sessions_;
    presence::UnixSeconds presence_timeout_;
};

} // namespace ds2online::matchmaking

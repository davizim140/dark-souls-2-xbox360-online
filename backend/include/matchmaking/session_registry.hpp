#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <optional>
#include <unordered_map>
#include <vector>

namespace ds2online::matchmaking {

using PlayerId = std::uint64_t;
using SessionId = std::uint64_t;

struct SessionSnapshot {
    SessionId id = 0;
    PlayerId host = 0;
    std::size_t capacity = 0;
    std::vector<PlayerId> members;
};

enum class SessionResult {
    Ok,
    InvalidPlayer,
    InvalidCapacity,
    SessionNotFound,
    AlreadyInSession,
    SessionFull,
    NotMember
};

// Protocol-neutral in-memory session primitive. Not Xbox Live, DS2 matchmaking,
// or a network transport implementation.
class SessionRegistry {
public:
    std::optional<SessionId> Create(PlayerId host, std::size_t capacity = 4) {
        if (host == 0 || capacity == 0 || capacity > 16) return std::nullopt;
        std::lock_guard<std::mutex> lock(mutex_);
        if (player_sessions_.count(host) != 0 || next_id_ == 0) return std::nullopt;

        const SessionId id = next_id_++;
        SessionSnapshot session;
        session.id = id;
        session.host = host;
        session.capacity = capacity;
        session.members.push_back(host);
        sessions_.emplace(id, session);
        player_sessions_.emplace(host, id);
        return id;
    }

    SessionResult Join(SessionId session_id, PlayerId player) {
        if (player == 0) return SessionResult::InvalidPlayer;
        std::lock_guard<std::mutex> lock(mutex_);
        auto session_it = sessions_.find(session_id);
        if (session_it == sessions_.end()) return SessionResult::SessionNotFound;
        if (player_sessions_.count(player) != 0) return SessionResult::AlreadyInSession;
        auto& session = session_it->second;
        if (session.members.size() >= session.capacity) return SessionResult::SessionFull;
        session.members.push_back(player);
        player_sessions_.emplace(player, session_id);
        return SessionResult::Ok;
    }

    SessionResult Leave(SessionId session_id, PlayerId player) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto session_it = sessions_.find(session_id);
        if (session_it == sessions_.end()) return SessionResult::SessionNotFound;
        auto& session = session_it->second;
        auto member_it = std::find(session.members.begin(), session.members.end(), player);
        if (member_it == session.members.end()) return SessionResult::NotMember;

        player_sessions_.erase(player);
        if (player == session.host) {
            for (PlayerId member : session.members) player_sessions_.erase(member);
            sessions_.erase(session_it);
            return SessionResult::Ok;
        }

        session.members.erase(member_it);
        return SessionResult::Ok;
    }

    std::optional<SessionSnapshot> Find(SessionId session_id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = sessions_.find(session_id);
        if (it == sessions_.end()) return std::nullopt;
        return it->second;
    }

    std::optional<SessionId> FindPlayerSession(PlayerId player) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = player_sessions_.find(player);
        if (it == player_sessions_.end()) return std::nullopt;
        return it->second;
    }

private:
    mutable std::mutex mutex_;
    SessionId next_id_ = 1;
    std::unordered_map<SessionId, SessionSnapshot> sessions_;
    std::unordered_map<PlayerId, SessionId> player_sessions_;
};

} // namespace ds2online::matchmaking

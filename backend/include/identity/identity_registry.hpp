#pragma once

#include "identity/external_identity.hpp"
#include <cstdint>
#include <map>
#include <mutex>
#include <optional>

namespace ds2online::identity {

// Process-local mapping from opaque provider identity to an internal player key.
// This is deliberately not persistence or authentication.
class IdentityRegistry {
public:
    using PlayerId = std::uint64_t;

    std::optional<PlayerId> ResolveOrCreate(const ExternalIdentity& identity) {
        if (!identity.IsValid()) return std::nullopt;
        std::lock_guard<std::mutex> lock(mutex_);
        const auto found = identities_.find(identity);
        if (found != identities_.end()) return found->second;
        if (next_player_id_ == 0) return std::nullopt;

        const PlayerId assigned = next_player_id_;
        if (next_player_id_ == UINT64_MAX) next_player_id_ = 0;
        else ++next_player_id_;

        identities_.emplace(identity, assigned);
        return assigned;
    }

    std::optional<PlayerId> Find(const ExternalIdentity& identity) const {
        if (!identity.IsValid()) return std::nullopt;
        std::lock_guard<std::mutex> lock(mutex_);
        const auto found = identities_.find(identity);
        if (found == identities_.end()) return std::nullopt;
        return found->second;
    }

private:
    struct Less {
        bool operator()(const ExternalIdentity& left, const ExternalIdentity& right) const {
            if (left.provider != right.provider) return left.provider < right.provider;
            return left.value < right.value;
        }
    };

    mutable std::mutex mutex_;
    std::map<ExternalIdentity, PlayerId, Less> identities_;
    PlayerId next_player_id_ = 1;
};

} // namespace ds2online::identity

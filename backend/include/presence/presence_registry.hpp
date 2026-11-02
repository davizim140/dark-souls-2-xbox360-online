#pragma once

#include <algorithm>
#include <cstdint>
#include <mutex>
#include <optional>
#include <unordered_map>
#include <vector>

namespace ds2online::presence {

using PlayerId = std::uint64_t;
using UnixSeconds = std::int64_t;

struct PresenceSnapshot {
    PlayerId player = 0;
    UnixSeconds last_seen = 0;
};

class PresenceRegistry {
public:
    // Timestamps are supplied by the caller so expiration is deterministic in tests.
    bool MarkOnline(PlayerId player, UnixSeconds now) {
        if (player == 0 || now < 0) return false;
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = entries_.find(player);
        if (it != entries_.end() && now < it->second.last_seen) return false;
        entries_[player] = PresenceSnapshot{player, now};
        return true;
    }

    bool MarkOffline(PlayerId player) {
        if (player == 0) return false;
        std::lock_guard<std::mutex> lock(mutex_);
        return entries_.erase(player) != 0;
    }

    std::optional<PresenceSnapshot> FindActive(
        PlayerId player, UnixSeconds now, UnixSeconds timeout) const {
        if (player == 0 || now < 0 || timeout <= 0) return std::nullopt;
        std::lock_guard<std::mutex> lock(mutex_);
        const auto it = entries_.find(player);
        if (it == entries_.end() || !IsFresh(it->second, now, timeout)) {
            return std::nullopt;
        }
        return it->second;
    }

    std::vector<PresenceSnapshot> ListActive(UnixSeconds now, UnixSeconds timeout) const {
        std::vector<PresenceSnapshot> active;
        if (now < 0 || timeout <= 0) return active;
        std::lock_guard<std::mutex> lock(mutex_);
        for (const auto& item : entries_) {
            if (IsFresh(item.second, now, timeout)) active.push_back(item.second);
        }
        std::sort(active.begin(), active.end(),
                  [](const PresenceSnapshot& a, const PresenceSnapshot& b) {
                      return a.player < b.player;
                  });
        return active;
    }

    std::size_t Expire(UnixSeconds now, UnixSeconds timeout) {
        if (now < 0 || timeout <= 0) return 0;
        std::lock_guard<std::mutex> lock(mutex_);
        std::size_t removed = 0;
        for (auto it = entries_.begin(); it != entries_.end();) {
            if (!IsFresh(it->second, now, timeout)) {
                it = entries_.erase(it);
                ++removed;
            } else {
                ++it;
            }
        }
        return removed;
    }

private:
    static bool IsFresh(const PresenceSnapshot& entry, UnixSeconds now,
                        UnixSeconds timeout) {
        return entry.last_seen <= now && now - entry.last_seen < timeout;
    }

    mutable std::mutex mutex_;
    std::unordered_map<PlayerId, PresenceSnapshot> entries_;
};

} // namespace ds2online::presence

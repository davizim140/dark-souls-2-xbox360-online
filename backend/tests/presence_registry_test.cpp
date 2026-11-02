#include "presence/presence_registry.hpp"

#include <cassert>
#include <thread>
#include <vector>

using ds2online::presence::PresenceRegistry;

int main() {
    PresenceRegistry registry;

    assert(!registry.MarkOnline(0, 100));
    assert(!registry.MarkOnline(1, -1));
    assert(registry.MarkOnline(20, 100));
    assert(registry.MarkOnline(10, 100));
    assert(registry.FindActive(20, 109, 10).has_value());
    assert(!registry.FindActive(20, 110, 10).has_value());
    assert(!registry.FindActive(20, 99, 10).has_value());
    assert(!registry.FindActive(0, 100, 10).has_value());
    assert(!registry.FindActive(10, 100, 0).has_value());

    // An older heartbeat must not overwrite a newer timestamp.
    assert(registry.MarkOnline(20, 105));
    assert(!registry.MarkOnline(20, 104));
    assert(registry.FindActive(20, 114, 10)->last_seen == 105);

    const auto active = registry.ListActive(109, 10);
    assert(active.size() == 2);
    assert(active[0].player == 10);
    assert(active[1].player == 20);

    assert(registry.MarkOffline(10));
    assert(!registry.MarkOffline(10));
    assert(!registry.FindActive(10, 109, 10).has_value());

    assert(registry.MarkOnline(30, 100));
    assert(registry.MarkOnline(40, 108));
    assert(registry.Expire(110, 10) == 2);
    assert(!registry.FindActive(30, 110, 10).has_value());
    assert(registry.FindActive(40, 110, 10).has_value());

    // Concurrent updates for distinct players remain independently addressable.
    std::vector<std::thread> workers;
    for (std::uint64_t player = 100; player < 116; ++player) {
        workers.emplace_back([&registry, player]() {
            for (int i = 0; i < 100; ++i) {
                assert(registry.MarkOnline(player, 200 + i));
            }
        });
    }
    for (auto& worker : workers) worker.join();
    assert(registry.ListActive(299, 200).size() == 16);
    return 0;
}

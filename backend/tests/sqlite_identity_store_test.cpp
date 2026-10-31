#include "identity/sqlite_identity_store.hpp"

#include <cassert>
#include <cstdio>
#include <filesystem>
#include <string>
#include <thread>
#include <vector>

using ds2online::identity::ExternalIdentity;
using ds2online::identity::SqliteIdentityStore;

int main() {
    const auto database_path =
        (std::filesystem::temp_directory_path() / "ds2online_identity_persistence_test.sqlite").string();

    // Two independent SQLite connections must resolve a concurrent identity
    // to one stable player ID, not create duplicate rows.
    const ExternalIdentity concurrent_identity{"test-provider", {0xAA, 0xBB, 0xCC}};
    {
        SqliteIdentityStore first_connection(database_path);
        SqliteIdentityStore second_connection(database_path);
        std::vector<SqliteIdentityStore::PlayerId> observed(16, 0);
        std::vector<std::thread> workers;
        for (std::size_t i = 0; i < observed.size(); ++i) {
            workers.emplace_back([&, i]() {
                auto& connection = (i % 2 == 0) ? first_connection : second_connection;
                for (int attempt = 0; attempt < 20; ++attempt) {
                    const auto id = connection.ResolveOrCreate(concurrent_identity);
                    assert(id.has_value());
                    observed[i] = *id;
                }
            });
        }
        for (auto& worker : workers) worker.join();
        for (const auto id : observed) {
            assert(id == observed.front());
        }
        assert(first_connection.Find(concurrent_identity) == observed.front());
    }

    std::remove(database_path.c_str());
    std::remove((database_path + "-wal").c_str());
    std::remove((database_path + "-shm").c_str());

    const ExternalIdentity first{"steam", {0x10, 0x20, 0x30}};
    const ExternalIdentity same_bytes_other_provider{"unverified", {0x10, 0x20, 0x30}};
    SqliteIdentityStore::PlayerId first_id = 0;
    SqliteIdentityStore::PlayerId other_id = 0;

    {
        SqliteIdentityStore store(database_path);
        assert(!store.Find(first).has_value());
        const auto created = store.ResolveOrCreate(first);
        assert(created.has_value());
        first_id = *created;
        assert(first_id > 0);
        assert(store.ResolveOrCreate(first) == created);

        const auto other = store.ResolveOrCreate(same_bytes_other_provider);
        assert(other.has_value());
        other_id = *other;
        assert(other_id != first_id);
    }

    // A new store instance simulates a process restart.
    {
        SqliteIdentityStore reopened(database_path);
        assert(reopened.Find(first).has_value());
        assert(*reopened.Find(first) == first_id);
        assert(reopened.ResolveOrCreate(first) == first_id);
        assert(reopened.Find(same_bytes_other_provider) == other_id);
    }

    std::remove(database_path.c_str());
    std::remove((database_path + "-wal").c_str());
    std::remove((database_path + "-shm").c_str());
    return 0;
}

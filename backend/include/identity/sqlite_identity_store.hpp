#pragma once

#include "identity/external_identity.hpp"

#include <cstdint>
#include <mutex>
#include <optional>
#include <string>

struct sqlite3;

namespace ds2online::identity {

// SQLite-backed identity mapping. This persists opaque identities to stable
// internal player IDs; it does not authenticate identities or identify Xbox IDs.
class SqliteIdentityStore {
public:
    using PlayerId = std::uint64_t;

    explicit SqliteIdentityStore(const std::string& database_path);
    ~SqliteIdentityStore();

    SqliteIdentityStore(const SqliteIdentityStore&) = delete;
    SqliteIdentityStore& operator=(const SqliteIdentityStore&) = delete;

    std::optional<PlayerId> ResolveOrCreate(const ExternalIdentity& identity);
    std::optional<PlayerId> Find(const ExternalIdentity& identity);

private:
    sqlite3* database_ = nullptr;
    std::mutex mutex_;
};

} // namespace ds2online::identity

#include "identity/sqlite_identity_store.hpp"

#include <sqlite3.h>

#include <limits>
#include <stdexcept>
#include <string>

namespace ds2online::identity {
namespace {

void CheckSqlite(int result, sqlite3* database, const char* operation) {
    if (result != SQLITE_OK) {
        const std::string detail = database ? sqlite3_errmsg(database) : "SQLite error";
        throw std::runtime_error(std::string(operation) + ": " + detail);
    }
}

class Statement {
public:
    Statement(sqlite3* database, const char* sql) : database_(database) {
        CheckSqlite(sqlite3_prepare_v2(database_, sql, -1, &statement_, nullptr),
                    database_, "prepare statement");
    }
    ~Statement() { sqlite3_finalize(statement_); }
    Statement(const Statement&) = delete;
    Statement& operator=(const Statement&) = delete;
    sqlite3_stmt* get() const { return statement_; }

private:
    sqlite3* database_;
    sqlite3_stmt* statement_ = nullptr;
};

void BindIdentity(sqlite3_stmt* statement, const ExternalIdentity& identity) {
    CheckSqlite(sqlite3_bind_text(statement, 1, identity.provider.c_str(),
                                  static_cast<int>(identity.provider.size()), SQLITE_TRANSIENT),
                nullptr, "bind identity provider");
    CheckSqlite(sqlite3_bind_blob(statement, 2, identity.value.data(),
                                  static_cast<int>(identity.value.size()), SQLITE_TRANSIENT),
                nullptr, "bind identity value");
}

std::optional<SqliteIdentityStore::PlayerId> ReadPlayerId(sqlite3_stmt* statement) {
    const int result = sqlite3_step(statement);
    if (result == SQLITE_DONE) return std::nullopt;
    if (result != SQLITE_ROW) {
        throw std::runtime_error("read player ID: SQLite statement failed");
    }

    const sqlite3_int64 id = sqlite3_column_int64(statement, 0);
    if (id <= 0) throw std::runtime_error("database contains an invalid player ID");
    return static_cast<SqliteIdentityStore::PlayerId>(id);
}

} // namespace

SqliteIdentityStore::SqliteIdentityStore(const std::string& database_path) {
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
    const int result = sqlite3_open_v2(database_path.c_str(), &database_, flags, nullptr);
    if (result != SQLITE_OK) {
        const std::string detail = database_ ? sqlite3_errmsg(database_) : "unable to allocate SQLite handle";
        if (database_) sqlite3_close_v2(database_);
        database_ = nullptr;
        throw std::runtime_error("open identity database: " + detail);
    }

    try {
        CheckSqlite(sqlite3_busy_timeout(database_, 5000), database_, "set SQLite busy timeout");
        CheckSqlite(sqlite3_exec(database_, "PRAGMA journal_mode=WAL;", nullptr, nullptr, nullptr),
                    database_, "enable SQLite WAL");
        CheckSqlite(sqlite3_exec(database_, "PRAGMA synchronous=FULL;", nullptr, nullptr, nullptr),
                    database_, "set SQLite durability");

        const char* schema =
            "CREATE TABLE IF NOT EXISTS external_identities ("
            "player_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "provider TEXT NOT NULL,"
            "identity_value BLOB NOT NULL,"
            "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "UNIQUE(provider, identity_value)"
            ");";
        CheckSqlite(sqlite3_exec(database_, schema, nullptr, nullptr, nullptr),
                    database_, "create identity schema");
    } catch (...) {
        sqlite3_close_v2(database_);
        database_ = nullptr;
        throw;
    }
}

SqliteIdentityStore::~SqliteIdentityStore() {
    if (database_) sqlite3_close_v2(database_);
}

std::optional<SqliteIdentityStore::PlayerId>
SqliteIdentityStore::ResolveOrCreate(const ExternalIdentity& identity) {
    if (!identity.IsValid()) return std::nullopt;
    std::lock_guard<std::mutex> lock(mutex_);

    Statement insert(database_,
        "INSERT OR IGNORE INTO external_identities(provider, identity_value) VALUES(?1, ?2);");
    BindIdentity(insert.get(), identity);
    const int insert_result = sqlite3_step(insert.get());
    if (insert_result != SQLITE_DONE) {
        throw std::runtime_error(std::string("insert identity: ") + sqlite3_errmsg(database_));
    }

    Statement select(database_,
        "SELECT player_id FROM external_identities WHERE provider = ?1 AND identity_value = ?2;");
    BindIdentity(select.get(), identity);
    return ReadPlayerId(select.get());
}

std::optional<SqliteIdentityStore::PlayerId>
SqliteIdentityStore::Find(const ExternalIdentity& identity) {
    if (!identity.IsValid()) return std::nullopt;
    std::lock_guard<std::mutex> lock(mutex_);

    Statement select(database_,
        "SELECT player_id FROM external_identities WHERE provider = ?1 AND identity_value = ?2;");
    BindIdentity(select.get(), identity);
    return ReadPlayerId(select.get());
}

} // namespace ds2online::identity

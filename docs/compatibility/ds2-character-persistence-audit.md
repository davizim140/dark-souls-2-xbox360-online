# DS2 character persistence audit

## Scope and source pin

Static audit of the DS2 server implementation in upstream `TLeonardUK/ds3os`, pinned to commit `56406879a31505a71bea8c6290da370067f43659`. This documents the upstream server's storage model only; it is not evidence that an Xbox 360 retail client sends the same messages or binary payloads.

## Confirmed persistence model

### SQLite schema

`ServerDatabase::CreateTables()` creates a `Characters` table with:
- `Id`: SQLite auto-increment primary key;
- `PlayerId`: owner key used by the server;
- `CharacterId`: character slot/identifier under that player;
- `Data`: BLOB containing opaque character bytes;
- `QuickMatchDuelRank`, `QuickMatchDuelXp`, `QuickMatchBrawlRank`, `QuickMatchBrawlXp`: separate quick-match values;
- `CreatedTime`: creation timestamp.

The table definition does not declare a composite unique constraint on `PlayerId, CharacterId`. The application queries with that pair and uses it as the logical lookup key.

### Character selection and upload

In `DS2_PlayerDataManager::Handle_RequestUpdateLoginPlayerCharacter`:
1. The request's `character_id` is used when nonzero.
2. When zero, the server scans candidate IDs from 1 upward, excluding IDs supplied in `local_character_ids` and IDs already found for that player.
3. If no database record exists, it creates one with an empty byte vector.
4. The selected ID is stored in the connected player's transient `PlayerState` and returned to the client.

In `Handle_RequestUpdatePlayerCharacter`, the request's `character_data` bytes are copied into a byte vector and passed to `CreateOrUpdateCharacter(PlayerId, CharacterId, Data)`.

### Database write/read behavior

- `CreateOrUpdateCharacter` first updates `Data` for the matching `PlayerId` and `CharacterId`; if SQLite reports no changed rows, it inserts a new row with `CreatedTime`.
- `FindCharacter` reads the BLOB and the four quick-match rank/XP fields.
- `Handle_RequestGetPlayerCharacter` looks up the requested player/character pair and returns the stored blob (or an empty byte string if no record is found).
- `Handle_RequestGetLoginPlayerCharacter` finds the currently connected client for the requested player, reads that client's selected character from the database, and returns its ID and blob. If no such connected client or character is found, the response uses character ID 0 and empty data.

## Persistent versus transient state

| Data | Upstream behavior |
|---|---|
| Character blob | Persisted in SQLite `Characters.Data` |
| Character ownership/slot | Persisted as `PlayerId` + `CharacterId` |
| Quick-match ranks/XP | Separate columns in `Characters` |
| Current selected character ID | Held in connected client's `PlayerState`; selected ID also maps to persisted row |
| Parsed `AllStatus` snapshot | Merged into in-memory `DS2_PlayerState`; this handler does not write it to the Characters table |
| Current area, activity area, invadability, soul level, visitor pool, lit bonfires | Derived/maintained in the in-memory player state by status handling |

The `DS2_PlayerDataManager.h` comment says the character-data manager appears mainly related to cheat detection, while explicitly noting uncertainty about how much other managers use it. Treat that as the upstream author's comment, not a proven complete purpose statement.

## Evidence boundaries

- The upstream database identity is `PlayerId`, and the Players table is keyed by `PlayerSteamId` in this implementation. This does not establish that Xbox 360 uses Steam identity; Xbox may use XUID or another identity flow.
- The character blob is opaque here. This audit does not decode its internal format, establish a retail Xbox save format, or show that Xbox uploads the same blob.
- The upstream DS2 protobuf schema and handlers do not prove Xbox protocol compatibility.
- This is a static source audit. No Xbox client, compatible service, patch, XEX, or console test was created or validated.

## Pinned upstream source files

- [DS2_PlayerDataManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/PlayerData/DS2_PlayerDataManager.cpp)
- [DS2_PlayerDataManager.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/PlayerData/DS2_PlayerDataManager.h)
- [ServerDatabase.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/Database/ServerDatabase.cpp)
- [ServerDatabase.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/Database/ServerDatabase.h)

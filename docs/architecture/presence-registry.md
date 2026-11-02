# Presence registry foundation

## Implemented

The C++ PresenceRegistry is a thread-safe, in-memory primitive for recording player heartbeat timestamps. The caller supplies Unix timestamps, which keeps expiration deterministic and avoids hiding a clock policy inside the library.

- Mark a nonzero player online and refresh its last-seen timestamp.
- Reject negative timestamps and out-of-order heartbeats.
- Mark a player offline.
- Find one active player or list active players using a caller-supplied positive timeout.
- Expire stale entries explicitly; active means the timestamp is not in the future and its age is strictly less than the timeout.
- Active lists are sorted by player ID for deterministic output.
- Concurrent access is protected by a mutex.

## Boundaries

This is not a network service, heartbeat endpoint, authentication mechanism, persistent presence store, or Xbox Live/XONLINE implementation. No Xbox 360 endpoint, packet format, timeout value, identity mapping, or retail-game behavior is inferred here. The timeout and trusted clock must be selected by a future, evidence-based service layer.

The registry is not connected to the session registry or the game. It cannot restore online play by itself.

# Session registry foundation

## Purpose

The C++ SessionRegistry is a small, thread-safe, protocol-neutral backend primitive. It provides in-memory session creation, joining, leaving, capacity enforcement, one-session-per-player tracking, and snapshots.

## Implemented behavior

- A nonzero player can create a session with capacity 1–16 (default 4).
- A player may belong to at most one session in this registry.
- Join rejects unknown sessions, duplicate membership, zero player IDs, and full sessions.
- A non-host member can leave without affecting other members.
- When the host leaves, the session closes and all memberships are cleared.
- IDs are monotonic for the lifetime of this process; state is not persisted.
- Public operations are protected by a mutex.

## Explicit non-goals

This is not yet a network server or a DS2 matchmaking implementation. It has no socket listener, authentication, persistence, cross-process coordination, DS2 matching filters, summon-sign semantics, invasion rules, NAT traversal, or Xbox Live/XONLINE integration. It does not establish that the retail Xbox 360 game uses this session model.

The registry can become an internal primitive after the Xbox client protocol and matchmaking semantics are established. Do not connect the console to it or advertise it as online compatibility.

# Matchmaking coordinator foundation

## Implemented behavior

The protocol-neutral C++ MatchmakingCoordinator composes the in-memory presence and session registries:

- Session creation requires the host to have a fresh presence record.
- Joining requires a fresh presence record for the joining player.
- Capacity, duplicate membership, unknown sessions, and host-close behavior are delegated to SessionRegistry.
- Leave is exposed through the coordinator.
- The presence timeout is supplied by the embedding service; tests use a deterministic timestamp.

## Consistency and security boundaries

Presence is checked immediately before the session operation, but the two registries do not share a transaction or lock. A player may go offline between the check and the membership update. A production service must define disconnect cleanup and atomicity before relying on this primitive.

This is not DS2 matchmaking, Soul Memory matching, summon or invasion logic, Xbox Live/XONLINE authentication, NAT traversal, a socket server, or a retail Xbox 360 protocol implementation. It does not connect to the game and must not be described as restored online functionality.

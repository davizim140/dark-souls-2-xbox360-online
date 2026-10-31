# DS2 matchmaking implementation audit (upstream DSOS)

## Scope and source

Static inspection of the upstream files:

- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Signs/DS2_SignManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/QuickMatch/DS2_QuickMatchManager.cpp`
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`

This is an audit of server-side source code only. It is not a runtime test,
and it is not evidence that the Xbox 360 client can connect to this server.

## Summon signs

The sign manager dispatches handlers for:
- retrieving sign lists;
- creating, updating and removing signs;
- requesting a summon and rejecting a sign;
- retrieving the right matching area.

The implementation stores active signs in a live cache, filters candidates
using area/cell and matching parameters, and tracks which players are aware
of each sign. When a sign is removed, it sends a push notification to clients
that were marked as aware. On player disconnect, it removes that player's
active signs.

The matching code applies separate configured matching rules for red,
white, small white and dragon-eye sign types, and respects global coop or
invasion disable settings.

**Observed limitation:** `DS2_SignManager::Poll()` is empty in the inspected
source. This means this method itself does not perform periodic maintenance.
Do not infer from this alone that signs never expire; expiry may be handled
elsewhere or by cache behavior. The exact lifetime policy requires further
inspection.

## Quick matches (Undead Match)

The quick-match manager dispatches handlers for:
- searching and registering matches;
- unregistering and updating matches;
- joining and rejecting join requests.

The code stores match entries in an in-memory collection. Search filters by
game mode, cell, online area and configured Soul Memory matching. Join
requests are forwarded to the host through a push message; a rejection push
is sent when the host or match cannot be found. Hosted matches are removed
when the host disconnects or explicitly unregisters.

**Observed limitations:**
- `DS2_QuickMatchManager::Poll()` is empty in the inspected source.
- The update handler replies successfully but its comment says it is unclear
  whether anything beyond keeping the match alive is required.
- The inspected manager stores matches in process memory; this source alone
  does not establish persistence across server restarts.
- Some alternative matching logic is inside a disabled `#if 0` block and is
  not active in this implementation.

These are source-level observations, not proof that quick match is broken.
They identify behaviors that should be tested before describing the service
as production-ready.

## Project implications

1. The upstream DS2 server has meaningful implementations for summon-sign
   matchmaking and Undead Match; they are not merely message-ID declarations.
2. Presence of handlers does not prove full service completeness, reliable
   lifecycle handling, or compatibility with Xbox 360.
3. The Xbox 360 client protocol, authentication, identity, endpoint discovery
   and transport remain unverified.
4. Do not build an Xbox client patch, redirect endpoints, or test an XEX on
   the console from this audit.

## Source links

- [DS2 sign manager](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Signs/DS2_SignManager.cpp)
- [DS2 quick-match manager](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/QuickMatch/DS2_QuickMatchManager.cpp)
- [DS2 game adapter](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/DS2_Game.cpp)

# DSOS compatibility assessment — Xbox 360 target

## Upstream project

Reference: https://github.com/TLeonardUK/ds3os

The upstream README explicitly describes an open-source server implementation for Dark Souls II: Scholar of the First Sin and Dark Souls III. It lists Dark Souls II support as **experimental / under development**, while listing transport, messages, bloodstains, ghosts, summoning, invasions, matchmaking and other functions as implemented in that project's supported environment.

The repository contains:
- `Source/Server.DarkSouls2` — game-specific server code;
- `DarkSouls2.Dockerfile` — a Linux server image build;
- shared server and protobuf code.

## Important compatibility boundary

The upstream README states that its server requires Steam client initialization and authenticates Steam tickets. Its documented client workflow uses a Windows loader/injector that patches the PC game's memory to connect to the custom server.

Therefore:
- This is a real DS2 SOTFS server implementation and a valuable protocol/code reference.
- It is **not** a ready-to-use Xbox 360 server package.
- Steam ticket authentication and the PC memory-injection workflow cannot be assumed to work on Xbox 360.
- The Xbox 360 client may use different platform authentication, transport setup, endpoints, or message behavior. None of those differences have been confirmed yet.
- The upstream feature table does not prove Xbox 360 compatibility.

## Decision for this project

Do not port the PC loader/injector to Xbox 360 and do not point the console at DSOS yet.

First inspect the DS2-specific server/protobuf implementation to understand its protocol, then compare it against evidence from the Xbox 360 client. Reuse server-side logic only where protocol and authentication compatibility are demonstrated.

## Current Xbox 360 evidence

Target reported by user:
- Title ID: `465307E4`
- Media ID: `458B3E06`
- Region: NTSC
- Title Update: none (base version)

Online attempt:
- Message: `Falha ao se conectar ao servidor do jogo Dark Souls 2.`
- Timing: after in-game calibrations, with a delay of a few seconds.

This timing does not identify the destination server or prove which stage failed.

## Next technical task

Map the DS2-specific protocol surface in the upstream source (message definitions, server handlers, authentication/session entry points) and create a comparison checklist for the Xbox 360 client. Do not claim parity until Xbox-side evidence exists.


## Source-level protocol map (upstream DS2 implementation)

Inspection of the upstream DS2-specific source identifies these concrete components:

- `DS2_Game.cpp` maps typed protobuf request objects to `DS2_Frpg2ReliableUdpMessageType` values and maps incoming message types back to protobuf request/response classes.
- The transport wrapper is named `DS2_Frpg2ReliableUdpMessage`; the message-type mapping is listed in `DS2_Frpg2ReliableUdpMessageTypes.inc`.
- The protobuf header imports `DS2_Frpg2PlayerData.pb.h` and `DS2_Frpg2RequestMessage.pb.h`.
- The game registers separate managers for boot, player data, ghosts, blood messages, bloodstains, break-ins, logging, misc, visitors, rankings, Mirror Knight, summon signs and quick matches.
- The server exposes live counters for blood messages, bloodstains, undead matches, summon signs and ghosts.

This establishes that the upstream DS2 implementation uses a reliable-UDP message layer with protobuf message classes and feature-specific managers. It does **not** establish that the Xbox 360 client uses the same framing, opcodes, protobuf schema, authentication or endpoints.

### Best comparison targets

1. Identify whether Xbox 360 traffic uses UDP during the post-calibration connection attempt.
2. If UDP is observed, compare packet timing and message framing only after capturing sanitized evidence.
3. Compare the Xbox client's first request/response sequence against the upstream DS2 boot/session handlers.
4. Treat authentication separately; the upstream PC workflow depends on Steam tickets and a PC injector.

Useful upstream source references:
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessage.h`
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessageTypes.inc`
- `Source/Server.DarkSouls2/Protobuf/DS2_Protobufs.h`


## Boot/login handshake inspection

The upstream `DS2_BootManager.cpp` provides a concrete first-session sequence:

1. It waits for `RequestWaitForUserLogin`.
2. The handler reads `steam_id()` from that request.
3. The server resolves or creates a player record using that Steam ID.
4. It responds with `RequestWaitForUserLoginResponse`, including the Steam ID and assigned player ID.
5. It then sends `PlayerInfoUploadConfigPushMessage`, configuring player-status upload fields and intervals.
6. A separate request, `RequestGetAnnounceMessageList`, returns announcement data.

### Why this matters for Xbox 360

This is a major compatibility checkpoint: the reference server's login handler explicitly expects a Steam ID and uses it as the player identity key. The Xbox 360 build may instead rely on Xbox Live/XUID or another platform identity. That is not yet proven for this title/build, but it means we cannot assume the existing DSOS login flow will accept an Xbox 360 client unchanged.

The Xbox-side first connection attempt must be observed before designing an authentication adapter. Do not fabricate a Steam ID, bypass authentication, or redirect the console to this server as a test.

### Protocol checkpoints for the Xbox comparison

- Does the console attempt UDP during the post-calibration phase?
- Does the first application-level request resemble `RequestWaitForUserLogin`?
- What identity field, if any, is sent by the Xbox client?
- Does the client then request announcements?
- Does the server-side message framing match the upstream FRPG2 reliable-UDP implementation?

No Xbox packet capture has been supplied, so all Xbox-side answers remain unknown.

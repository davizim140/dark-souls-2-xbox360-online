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

# DS2 upstream boundary: game managers vs. PC client flow

## Finding

The DS2 server adapter in `Source/Server.DarkSouls2/Server/DS2_Game.cpp`
implements the game-facing protocol adapter:

- maps DS2 protobuf classes to FRPG2 reliable-UDP message types;
- maps incoming message types back to DS2 protobuf classes;
- determines which message types expect replies;
- registers DS2 game managers for boot, player data, ghosts, blood messages,
  bloodstains, break-ins, logging, miscellaneous services, visitors, rankings,
  Mirror Knight, summon signs and quick matches;
- creates a DS2-specific player state.

This is direct evidence that the upstream repository contains a DS2 game
service implementation, but it does not establish that every service around
it is complete or compatible with the Xbox 360 client.

## Important correction to the authentication-flow interpretation

The previously documented detailed client sequence was read from
`Source/Server/Client/Client.cpp`. That file constructs a
`DS3_Game()`, includes DS3 protobufs, sends DS3 login requests, and obtains a
Steam auth ticket through the Steam client API.

Therefore, that concrete PC-emulator sequence is **not a verified DS2 retail
client trace**. It is useful as an example of how the shared DS3OS client
emulator talks to its server stack, but it must not be treated as proof that
the DS2 client uses the same login requests, ticket acquisition, endpoint
discovery, or identity fields.

The DS2 server adapter and the DS3-oriented PC client emulator are separate
pieces of evidence. Their coexistence in one repository does not prove the
retail DS2 Xbox 360 client follows the PC emulator's flow.

## What is established vs. unknown

| Topic | Evidence status |
|---|---|
| DS2 protobuf-to-message mapping exists upstream | Confirmed in `DS2_Game.cpp` |
| DS2 game managers are registered upstream | Confirmed in `DS2_Game.cpp` |
| DS2 has its own player-state class | Confirmed in `DS2_Game.cpp` |
| The Xbox 360 client uses DSOS's FRPG2 transport unchanged | Unknown |
| The Xbox 360 client uses Steam ID as its identity | Unknown |
| The Xbox 360 client requests a Steam auth ticket | Unknown |
| The Xbox 360 client uses the PC emulator's TCP login/auth sequence | Unknown |
| The observed console connection failure identifies a specific stage | Not established |

## Consequence for this project

Do not implement or configure an Xbox client shim from the PC
`Client.cpp` sequence. Keep the DS2 game-protocol mapping as a reference for
server-side research, and keep Xbox authentication and endpoint discovery
marked unknown until there is Xbox-specific evidence.

No console, game files, DNS, router, or network configuration was changed for
this investigation.

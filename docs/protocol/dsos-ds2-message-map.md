# DSOS DS2 message map — reference only

## Scope

This document records message identifiers declared by the upstream
`TLeonardUK/ds3os` Dark Souls II implementation. It is a **PC/upstream
reference map**, not a verified description of the Xbox 360 wire protocol.

Upstream source:
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessageTypes.inc`
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessage.h`
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`

## Important distinction: request opcode vs push identifier

The upstream source declares request/response message types with the supplied
numeric opcode. The transport enum assigns the common push header type
`0x0320` to push messages; the comment in the message-types file says push
messages are distinguished by the first field in their protobuf.

Consequently:
- A `DEFINE_REQUEST_RESPONSE` entry such as `0x0386` is a request/response
  message type in the upstream DSOS mapping.
- A `DEFINE_PUSH_MESSAGE` entry such as `0x038C` is **not** a distinct
  transport header type in that enum. Its value is associated with the
  protobuf push message identity.
- Do not copy these values into an Xbox packet parser or patch without
  independent Xbox-side evidence.

## Selected upstream message map

| Feature | Upstream identifier | Message |
|---|---:|---|
| Login | `0x0386` | `RequestWaitForUserLogin` |
| Announcements | `0x03EC` | `RequestGetAnnounceMessageList` |
| Player character | `0x03B3` | `RequestGetLoginPlayerCharacter` |
| Player status | `0x03B8` | `RequestUpdatePlayerStatus` |
| Blood messages | `0x03AB` | `RequestCreateBloodMessage` |
| Blood messages | `0x03AE` | `RequestGetBloodMessageList` |
| Blood messages | `0x03AF` | `RequestEvaluateBloodMessage` |
| Area blood messages | `0x03FF` | `RequestGetAreaBloodMessageList` |
| Bloodstains | `0x0392` | `RequestGetBloodstainList` |
| Area bloodstains | `0x0400` | `RequestGetAreaBloodstainList` |
| Summon signs | `0x0394` | `RequestCreateSign` |
| Summon signs | `0x0397` | `RequestGetSignList` |
| Summon signs | `0x0398` | `RequestSummonSign` |
| Ghosts | `0x03B1` | `RequestCreateGhostData` |
| Ghosts | `0x03B2` | `RequestGetGhostDataList` |
| Invasions | `0x03D2` | `RequestGetBreakInTargetList` |
| Invasions | `0x03D3` | `RequestBreakInTarget` |
| Quick match | `0x03DC` | `RequestSearchQuickMatch` |
| Quick match | `0x03D9` | `RequestRegisterQuickMatch` |
| Quick match | `0x03DD` | `RequestJoinQuickMatch` |

This is a selected index, not a complete implementation checklist. The
upstream file also declares player-data updates, visitor/covenant operations,
Mirror Knight matchmaking, rankings, logging and additional push messages.

## Login sequence confirmed in upstream source

The upstream `DS2_BootManager.cpp` handles this sequence:

1. Receives `RequestWaitForUserLogin`.
2. Reads the request's `steam_id()` field.
3. Uses that Steam ID to find or create a player record.
4. Replies with `RequestWaitForUserLoginResponse`, including Steam ID and
   assigned player ID.
5. Sends `PlayerInfoUploadConfigPushMessage` to configure status uploads.
6. Handles `RequestGetAnnounceMessageList` separately.

The DSOS login path is therefore Steam-ID-based in this implementation. It
does not prove what identity the Xbox 360 retail client sends.

## Xbox 360 comparison status

| Question | Status |
|---|---|
| Does this Xbox build use FRPG2 reliable UDP? | Unknown |
| Does it use the same request identifiers? | Unknown |
| Does it serialize the same protobuf schemas? | Unknown |
| Does its login request contain a Steam ID, XUID, or another identity? | Unknown |
| Does it contact the same service endpoints? | Unknown |
| Is DSOS directly compatible with Xbox 360? | Not demonstrated |

The user's reported connection error occurs after in-game calibrations and a
short delay. That observation does not identify the transport, destination,
message type, or authentication failure.

## Safe project decision

Do not redirect the console to DSOS, spoof a Steam ID, patch the game, or
test an experimental server against the console yet. The next evidence needed
is Xbox-side network/protocol behavior. Until that exists, this map is useful
for planning and source comparison only.

## Reproducibility

The message names and values above are transcribed from the upstream
`DS2_Frpg2ReliableUdpMessageTypes.inc`; the push-header distinction is
documented in comments in that same file and reflected in
`DS2_Frpg2ReliableUdpMessage.h` and `DS2_Game.cpp`.

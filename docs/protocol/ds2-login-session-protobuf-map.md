# DS2 login and session protobuf field map (DSOS reference)

## Evidence boundary

Source: upstream `TLeonardUK/ds3os`, file
`Protobuf/DarkSouls2/DS2_Frpg2RequestMessage.proto`.

This is a transcription/interpretation of the upstream DS2 schema. It is
not evidence that the Xbox 360 retail build uses this schema. The upstream
file itself labels several fields as unknown or speculative. No Xbox packet
capture or Xbox executable analysis has confirmed these fields.

## Login request

Upstream message: `RequestWaitForUserLogin` (request identifier `0x0386`).

| Protobuf field | Type | Required? | Upstream annotation |
|---:|---|---|---|
| 1 | string `steam_id` | Yes | Identity consumed by DSOS login manager |
| 2 | uint32 `unknown_1` | Yes | Comment suggests profile index; sample value 1 |
| 3 | uint32 `unknown_2` | Yes | Sample value 0 |
| 4 | uint32 `unknown_3` | Yes | Sample value 1 |
| 5 | uint32 `unknown_4` | Yes | Sample value 2 |
| 6 | uint32 `unknown_5` | No | Meaning not established |
| 7 | uint32 `unknown_6` | No | Meaning not established |

Upstream response: `RequestWaitForUserLoginResponse`.

| Protobuf field | Type | Required? |
|---:|---|---|
| 1 | string `steam_id` | Yes |
| 2 | uint32 `player_id` | Yes |

### What this establishes

- The DSOS schema requires a string Steam ID in field 1.
- Four additional uint32 fields are required by this schema.
- Two optional uint32 fields exist, but their meanings are not documented.
- The response echoes the Steam ID and supplies a server-side player ID.

It does **not** establish that Xbox 360 sends a Steam ID, XUID, profile index,
or any equivalent field. Do not substitute a guessed XUID or fabricated
Steam ID into this protocol.

## Post-login status upload configuration

Upstream push: `PlayerInfoUploadConfigPushMessage`. Its push discriminator is
field 1 (`push_message_id = 0x038C)); the reliable-UDP push transport header
is the common `0x0320` described in the upstream source.

| Protobuf field | Type | Required? | Meaning in upstream schema |
|---:|---|---|---|
| 1 | PushMessageId | Yes | Push discriminator |
| 2 | PlayerStatusUploadConfig | Yes | Upload configuration |
| 3 | uint32 | Yes | Character-update send delay, seconds |
| 4 | uint32 | Yes | Player-status send delay, seconds |

Nested `PlayerStatusUploadConfig`:

| Protobuf field | Type | Required? |
|---:|---|---|
| 1 | repeated uint32 `player_data_mask` | No (repeated) |
| 2 | uint32 `upload_interval` | Yes |

The DSOS boot manager populates the character-update and status-upload delays
from server configuration. The schema comments describe default delays of
600 seconds and 300 seconds respectively, with a documented clamp range of
60 to 50000 seconds.

## Matching parameters relevant to signs and matchmaking

The schema defines `MatchingParameter`, reused by summon-sign and quick-match
requests. Its declared fields are:

| Field | Type | Name | Upstream notes |
|---:|---|---|---|
| 1 | uint32 | calibration_version | Example 20200 |
| 2 | uint32 | soul_level | — |
| 3 | uint32 | clear_count | — |
| 4 | uint32 | unknown_4 | Comment says it changes with clear_count |
| 6 | uint32 | covenant | Example values documented |
| 7 | uint32 | unknown_7 | Comment speculates NAT type |
| 8 | uint32 | disable_cross_region_play | — |
| 9 | uint32 | unknown_9 | Comment speculates region |
| 10 | uint32 | unknown_10 | — |
| 11 | uint32 | name_engraved_ring | — |
| 12 | uint32 | soul_memory | — |

Field number 5 is not declared in this message. The comments explicitly mark
some interpretations as guesses. These values must not be used to emulate
Xbox matchmaking without Xbox-side confirmation.

## Identity appears beyond the login request

The same upstream schema also includes Steam-ID strings in several social
payloads, including blood-message data, sign data, invasion targets, visitor
data, and quick-match records. This indicates that Steam identity is woven
through the DSOS PC-oriented data model, not isolated to one login field.

It remains unknown whether an Xbox-specific server implementation would
need an XUID-based identity model, a translation layer, a separate Xbox
service protocol, or something else entirely.

## Xbox compatibility checklist

| Question | Current evidence |
|---|---|
| Xbox login field layout matches this protobuf? | Unverified |
| Xbox sends Steam ID? | Unknown |
| Xbox sends XUID or another account identifier? | Unknown |
| Xbox uses the same push configuration message? | Unverified |
| Xbox matchmaking uses these matching fields? | Unverified |
| Can this schema be implemented directly for Xbox? | No basis to claim that yet |

## Safe next action

Continue source-level analysis only. Do not patch the game, redirect its
network destination, inject an identity, or run an experimental server on the
console based on this PC/upstream schema. A real Xbox-side protocol observation
is required before designing an adapter or server implementation.

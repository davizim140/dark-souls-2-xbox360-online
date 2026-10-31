# DSOS FRPG2 transport stack — source-level map

## Scope and warning

This document maps the transport implementation in upstream
`TLeonardUK/ds3os`. It is a PC/upstream reference only. No Xbox 360 packet
capture or executable analysis has established that the retail Xbox 360 build
uses this transport. Do not use these values to redirect, spoof, patch, or
construct packets for the console.

Primary upstream sources:
- `Source/Server/Server/Streams/README`
- `Frpg2ReliableUdpPacket.h/.cpp`
- `Frpg2ReliableUdpPacketStream.h/.cpp`
- `Frpg2ReliableUdpFragment.h/.cpp`
- `Frpg2ReliableUdpFragmentStream.h/.cpp`
- `Frpg2ReliableUdpMessage.h/.cpp`
- `Frpg2ReliableUdpMessageStream.h/.cpp`

## Layer stack

The upstream stream README describes the DS2/DS3 server-side stack as:

1. UDP packet stream — raw datagrams.
2. Reliable UDP packet stream — SYN/SYN_ACK, sequence tracking,
   acknowledgements, retransmission and connection state.
3. Fragment stream — splits large payloads and reassembles received fragments;
   optionally compresses payloads.
4. Message stream — wraps serialized Protocol Buffers with a message header.

The README contrasts this with a separate TCP packet/message path. This
project's DS2 implementation instantiates the reliable-UDP message stream.

## Reliable UDP packet layer

The upstream packet header is packed to **7 bytes**:

| Field | Size | Upstream definition |
|---|---:|---|
| magic number | 2 bytes | `0x02F5` (wire bytes checked as `F5 02`) |
| ACK counters | 3 bytes | two packed 12-bit counters |
| opcode | 1 byte | operation code |
| unknown | 1 byte | default `0xFF`; comment speculates congestion control |

Declared operation codes:

| Opcode | Value | Meaning in source |
|---|---:|---|
| SYN | `0x02` | connection setup / sequence synchronization |
| RACK | `0x03` | marked seemingly unused |
| DAT | `0x04` | data fragment |
| HBT | `0x05` | heartbeat |
| FIN | `0x06` | connection termination |
| RST | `0x07` | reset |
| PT_DAT_FRAG | `0x08` | marked seemingly unused |
| ACK | `0x31` | acknowledge highest received packet |
| SYN_ACK | `0x32` | acknowledge SYN and sequence information |
| DAT_ACK | `0x34` | data acknowledgement with payload |
| FIN_ACK | `0x36` | acknowledge termination |
| PT_DAT_FRAG_ACK | `0x38` | marked seemingly unused |

The source tracks 12-bit sequence values (0–4095), allows up to 32 packets in
flight, and has retransmission/heartbeat logic. Its constants include a
1-second retransmit interval, a 0.2-second retransmit cycle, a 0.5-second
SYN resend interval and a 5-second client heartbeat interval. These are
implementation details of this upstream code, not proven Xbox settings.

### SYN identity field

The upstream SYN setup prepends a 35-byte structure before the packet header:
- 17-byte `steam_id` character array;
- one unknown byte;
- a second 17-byte copy of `steam_id`.

The code's `Connect` method takes a `ClientSteamId`, stores it, and sends SYN.
The source comments say the other values are not understood.

This is a significant compatibility issue: the DSOS reference uses Steam ID
not only in the protobuf login request, but also in its reliable-UDP initial
connection data. It does **not** establish the Xbox 360 identity or handshake.

## Fragment layer

The fragment header fields are:

| Field | Size | Description |
|---|---:|---|
| packet counter | 2 bytes | fragment group counter |
| compression flag | 1 byte | indicates compressed payload |
| unknown 1–3 | 3 bytes | undocumented |
| total payload length | 2 bytes | full payload length |
| unknown 4 | 1 byte | undocumented |
| fragment index | 1 byte | fragment position |
| fragment length | 2 bytes | payload bytes in this fragment |

The upstream code:
- uses a maximum fragment payload of 900 bytes;
- enables compression for payloads of at least 512 bytes;
- includes the uncompressed length (4 bytes, big-endian) in the first
  compressed fragment;
- reassembles fragments and decompresses before passing data upward.

The source itself includes a TODO questioning whether fragments from different
packets can be interleaved; do not assume this implementation is a complete
formal protocol specification.

## Message layer

The message header is packed to **12 bytes**:

| Field | Size | Description |
|---|---:|---|
| header_size | 4 bytes | default `0x0C` |
| msg_type | 4 bytes | request type, Reply (`0`) or Push (`0x0320`) |
| msg_index | 4 bytes | request/response correlation index |

The code converts the first two header fields from big-endian and keeps
`msg_index` little-endian. A Reply message carries an additional **16-byte**
response header (four uint32 fields, currently undocumented in the source).

The message payload is a serialized protobuf. A request is tracked by its
message index; a Reply is mapped back to the outstanding request type using
that index. Push messages use `msg_type = 0x0320` and set
`msg_index = 0xFFFFFFFF`; their protobuf field 1 identifies the push subtype.

## What this tells us — and what it does not

Confirmed from the upstream source:
- DSOS DS2 uses a layered reliable-UDP transport.
- It has a SYN handshake, ACK counters, retransmission and heartbeat behavior.
- The initial SYN data contains a Steam ID twice.
- Messages wrap protobuf payloads and use message indices for responses.
- Fragmentation and optional compression occur below the message layer.

Not established for Xbox 360:
- Whether the console uses UDP or this protocol at all.
- Whether its packet magic, opcodes, ACK packing, endian rules or fragment
  layout match.
- Whether Xbox sends an XUID, another identity, or a different initial
  handshake.
- Whether its service uses the same endpoints, keys, authentication, or
  message schemas.

## Project decision

Do not implement an Xbox parser from these PC constants yet, and do not
redirect the console to DSOS. The next meaningful compatibility milestone is
an Xbox-side observation that identifies the transport and first handshake
without exposing account credentials. Until then, this document remains a
reference map, not an Xbox protocol specification.

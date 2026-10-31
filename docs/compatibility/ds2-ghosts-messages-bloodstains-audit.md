# DS2 ghosts, blood messages and bloodstains: upstream audit

## Scope

This document records static source inspection of the DS2 server implementation
in the upstream DSOS repository. It does not establish that the Xbox 360
retail client uses the same protocol or can authenticate/connect to DSOS.

## Ghost data

Source:
`Source/Server.DarkSouls2/Server/GameService/GameManagers/Ghosts/DS2_GhostManager.cpp`

The manager dispatches two request families:
- `RequestCreateGhostData`: accepts uploaded ghost data and processes it
  through the server's database/configuration path.
- `RequestGetGhostDataList`: retrieves ghost data for a requested online
  area and returns a response.

This is evidence that the upstream DS2 server has explicit ghost-data
handlers. It does not, by itself, prove the returned ghost format is accepted
by an Xbox 360 client or that the server's identity/authentication model fits
Xbox Live identities.

## Blood messages

Source:
`Source/Server.DarkSouls2/Server/GameService/GameManagers/BloodMessage/DS2_BloodMessageManager.cpp`

The manager dispatches handlers for:
- re-entry of a blood message;
- retrieving message evaluation;
- creating and removing messages;
- retrieving message lists by cell or area;
- evaluating a message.

The source includes database trimming and a live cache. List retrieval uses
random selection from matching cell/area entries and returns message metadata
and content.

**Known unresolved protocol detail:** both cell-list and area-list handlers
sum `max_type_1` and `max_type_2`. The source contains TODO comments saying
the difference between these two message types still needs to be understood.
The implementation therefore does not preserve a separately understood
quota/meaning for each type in those list limits.

**Maintenance observation:** `DS2_BloodMessageManager::Poll()` is empty.
The file separately defines `TrimDatabase()`; do not assume from the empty
Poll method alone when or how trimming is scheduled. The call site/lifecycle
needs separate verification.

## Bloodstains and death ghosts

Source:
`Source/Server.DarkSouls2/Server/GameService/GameManagers/Bloodstain/DS2_BloodstainManager.cpp`

The manager dispatches:
- creating a bloodstain;
- retrieving bloodstains by local list or area list;
- retrieving a `DeadingGhost` associated with a bloodstain.

This indicates that the upstream DS2 server models bloodstains and the
associated death-ghost data as distinct request paths. The create handler
receives both bloodstain data and ghost data. The retrieval handlers return
the matching records for the requested area/cell, subject to request limits
and server-side configuration.

Do not collapse this feature into the ordinary roaming-ghost feature:
the code has a separate bloodstain manager and a dedicated
`RequestGetDeadingGhost` handler.

## Xbox 360 compatibility boundary

The inspected code demonstrates server-side feature coverage in DSOS for
ghost data, blood messages and bloodstains. It does not confirm:

- Xbox 360 endpoint discovery or service authentication;
- Xbox 360 identity format (XUID versus Steam ID or another identifier);
- Xbox 360 packet encryption/key negotiation;
- compatibility of the binary player/ghost payloads with the retail Xbox build;
- that the Xbox 360 retail client sends the same message IDs or protobuf
  structures as the upstream DS2 implementation.

No console configuration, game file, network setting or executable was
changed as part of this audit.

## Source links

- [DS2 ghost manager](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Ghosts/DS2_GhostManager.cpp)
- [DS2 blood message manager](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/BloodMessage/DS2_BloodMessageManager.cpp)
- [DS2 bloodstain manager](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Bloodstain/DS2_BloodstainManager.cpp)

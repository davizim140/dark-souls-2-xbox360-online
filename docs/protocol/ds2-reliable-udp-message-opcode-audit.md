# Auditoria do mapa de mensagens FRPG2 Reliable UDP do DS2

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`  
Arquivo: `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessageTypes.inc`

O mapa abaixo foi extraído das declarações ativas do arquivo fixado. Foram encontrados **82 registros ativos**. Linhas comentadas não foram tratadas como mensagens implementadas.

## Como interpretar

- **Request/reply:** `DS2_Game::Protobuf_To_ReliableUdpMessageType` associa o protobuf de request ao tipo interno; `ReliableUdpMessageType_To_Protobuf` seleciona request ou response conforme o cabeçalho recebido.
- **Mensagem sem resposta:** `DEFINE_MESSAGE` cria protobuf apenas para recepção; o servidor não cria response para esse tipo.
- **Push:** no `DS2_Game.cpp`, o protobuf de push enviado pelo servidor é convertido para o tipo genérico `Push`. A macro de recepção de push não cria um protobuf no servidor: esses tipos são descritos como mensagens que o servidor envia ao cliente.
- O arquivo comenta que pushes usam `msg_type = 0x0320` no cabeçalho e são diferenciados pelo primeiro campo do protobuf. Portanto, não confunda o opcode listado para a classe push com o `msg_type` genérico do cabeçalho de push.
- `RequestSendMessageToPlayers` também possui opcode `0x0320`; a coincidência numérica não torna esse request um push.

## Mapa ativo

### Boot

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X038C` | `PlayerInfoUploadConfigPushMessage` | `PlayerInfoUploadConfigPushMessage` | `—` | Servidor → cliente (push) |
| `0X0386` | `RequestWaitForUserLogin` | `RequestWaitForUserLogin` | `RequestWaitForUserLoginResponse` | Cliente → servidor (request/reply) |
| `0X03EC` | `RequestGetAnnounceMessageList` | `RequestGetAnnounceMessageList` | `RequestGetAnnounceMessageListResponse` | Cliente → servidor (request/reply) |

### Player Data

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03B3` | `RequestGetLoginPlayerCharacter` | `RequestGetLoginPlayerCharacter` | `RequestGetLoginPlayerCharacterResponse` | Cliente → servidor (request/reply) |
| `0X03B6` | `RequestUpdateLoginPlayerCharacter` | `RequestUpdateLoginPlayerCharacter` | `RequestUpdateLoginPlayerCharacterResponse` | Cliente → servidor (request/reply) |
| `0X03B8` | `RequestUpdatePlayerStatus` | `RequestUpdatePlayerStatus` | `RequestUpdatePlayerStatusResponse` | Cliente → servidor (request/reply) |
| `0X03A8` | `RequestUpdatePlayerCharacter` | `RequestUpdatePlayerCharacter` | `RequestUpdatePlayerCharacterResponse` | Cliente → servidor (request/reply) |
| `0X03A9` | `RequestGetPlayerCharacter` | `RequestGetPlayerCharacter` | `RequestGetPlayerCharacterList` | Cliente → servidor (request/reply) |

### Blood Messages (user left messages)

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03AA` | `PushRequestEvaluateBloodMessage` | `PushRequestEvaluateBloodMessage` | `—` | Servidor → cliente (push) |
| `0X03AD` | `RequestReentryBloodMessage` | `RequestReentryBloodMessage` | `RequestReentryBloodMessageResponse` | Cliente → servidor (request/reply) |
| `0X03AB` | `RequestCreateBloodMessage` | `RequestCreateBloodMessage` | `RequestCreateBloodMessageResponse` | Cliente → servidor (request/reply) |
| `0X03AC` | `RequestRemoveBloodMessage` | `RequestRemoveBloodMessage` | `RequestRemoveBloodMessageResponse` | Cliente → servidor (request/reply) |
| `0X03AE` | `RequestGetBloodMessageList` | `RequestGetBloodMessageList` | `RequestGetBloodMessageListResponse` | Cliente → servidor (request/reply) |
| `0X03AF` | `RequestEvaluateBloodMessage` | `RequestEvaluateBloodMessage` | `RequestEvaluateBloodMessageResponse` | Cliente → servidor (request/reply) |
| `0X03B0` | `RequestGetBloodMessageEvaluation` | `RequestGetBloodMessageEvaluation` | `RequestGetBloodMessageEvaluationResponse` | Cliente → servidor (request/reply) |
| `0X03FF` | `RequestGetAreaBloodMessageList` | `RequestGetAreaBloodMessageList` | `RequestGetBloodMessageListResponse` | Cliente → servidor (request/reply) |

### Blood stains (blood puddles with ghosts)

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X0391` | `RequestCreateBloodstain` | `RequestCreateBloodstain` | `—` | Cliente → servidor (sem resposta) |
| `0X0392` | `RequestGetBloodstainList` | `RequestGetBloodstainList` | `RequestGetBloodstainListResponse` | Cliente → servidor (request/reply) |
| `0X0400` | `RequestGetAreaBloodstainList` | `RequestGetAreaBloodstainList` | `RequestGetBloodstainListResponse` | Cliente → servidor (request/reply) |

### Summon Signs

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X039B` | `PushRequestSummonSign` | `PushRequestSummonSign` | `—` | Servidor → cliente (push) |
| `0X039C` | `PushRequestRejectSign` | `PushRequestRejectSign` | `—` | Servidor → cliente (push) |
| `0X039D` | `PushRequestRemoveSign` | `PushRequestRemoveSign` | `—` | Servidor → cliente (push) |
| `0X0398` | `RequestSummonSign` | `RequestSummonSign` | `RequestSummonSignResponse` | Cliente → servidor (request/reply) |
| `0X0394` | `RequestCreateSign` | `RequestCreateSign` | `RequestCreateSignResponse` | Cliente → servidor (request/reply) |
| `0X0397` | `RequestGetSignList` | `RequestGetSignList` | `RequestGetSignListResponse` | Cliente → servidor (request/reply) |
| `0X039A` | `RequestRejectSign` | `RequestRejectSign` | `RequestRejectSignResponse` | Cliente → servidor (request/reply) |
| `0X0396` | `RequestRemoveSign` | `RequestRemoveSign` | `RequestRemoveSignResponse` | Cliente → servidor (request/reply) |
| `0X0395` | `RequestUpdateSign` | `RequestUpdateSign` | `RequestUpdateSignResponse` | Cliente → servidor (request/reply) |
| `0X03FA` | `RequestGetRightMatchingArea` | `RequestGetRightMatchingArea` | `RequestGetRightMatchingAreaResponse` | Cliente → servidor (request/reply) |

### Ghosts

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X0393` | `RequestGetDeadingGhost` | `RequestGetDeadingGhost` | `RequestGetDeadingGhostResponse` | Cliente → servidor (request/reply) |
| `0X03B1` | `RequestCreateGhostData` | `RequestCreateGhostData` | `RequestCreateGhostDataResponse` | Cliente → servidor (request/reply) |
| `0X03B2` | `RequestGetGhostDataList` | `RequestGetGhostDataList` | `RequestGetGhostDataListResponse` | Cliente → servidor (request/reply) |

### Logging

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03F7` | `RequestNotifyBuyItem` | `RequestNotifyBuyItem` | `RequestNotifyBuyItemResponse` | Cliente → servidor (request/reply) |
| `0X03F1` | `RequestNotifyDeath` | `RequestNotifyDeath` | `RequestNotifyDeathResponse` | Cliente → servidor (request/reply) |
| `0X03F9` | `RequestNotifyDisconnectSession` | `RequestNotifyDisconnectSession` | `RequestNotifyDisconnectSessionResponse` | Cliente → servidor (request/reply) |
| `0X03E8` | `RequestNotifyJoinGuestPlayer` | `RequestNotifyJoinGuestPlayer` | `RequestNotifyJoinGuestPlayerResponse` | Cliente → servidor (request/reply) |
| `0X03EA` | `RequestNotifyJoinSession` | `RequestNotifyJoinSession` | `RequestNotifyJoinSessionResponse` | Cliente → servidor (request/reply) |
| `0X03F6` | `RequestNotifyKillEnemy` | `RequestNotifyKillEnemy` | `RequestNotifyKillEnemyResponse` | Cliente → servidor (request/reply) |
| `0X03ED` | `RequestNotifyKillPlayer` | `RequestNotifyKillPlayer` | `RequestNotifyKillPlayerResponse` | Cliente → servidor (request/reply) |
| `0X03E9` | `RequestNotifyLeaveGuestPlayer` | `RequestNotifyLeaveGuestPlayer` | `RequestNotifyLeaveGuestPlayerResponse` | Cliente → servidor (request/reply) |
| `0X03EB` | `RequestNotifyLeaveSession` | `RequestNotifyLeaveSession` | `RequestNotifyLeaveSessionResponse` | Cliente → servidor (request/reply) |
| `0X03D8` | `RequestNotifyMirrorKnight` | `RequestNotifyMirrorKnight` | `RequestNotifyMirrorKnightResponse` | Cliente → servidor (request/reply) |
| `0X03F2` | `RequestNotifyOfflineDeathCount` | `RequestNotifyOfflineDeathCount` | `RequestNotifyOfflineDeathCountResponse` | Cliente → servidor (request/reply) |

### Ranking

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03F5` | `RequestGetPowerStoneMyRanking` | `RequestGetPowerStoneMyRanking` | `RequestGetPowerStoneMyRankingResponse` | Cliente → servidor (request/reply) |
| `0X03F4` | `RequestGetPowerStoneRanking` | `RequestGetPowerStoneRanking` | `RequestGetPowerStoneRankingResponse` | Cliente → servidor (request/reply) |
| `0X03F8` | `RequestGetPowerStoneRankingRecordCount` | `RequestGetPowerStoneRankingRecordCount` | `RequestGetPowerStoneRankingRecordCountResponse` | Cliente → servidor (request/reply) |
| `0X03F3` | `RequestRegisterPowerStoneData` | `RequestRegisterPowerStoneData` | `RequestRegisterPowerStoneDataResponse` | Cliente → servidor (request/reply) |

### Mirror Knight

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03A6` | `PushRequestRejectMirrorKnightSign` | `PushRequestRejectMirrorKnightSign` | `—` | Servidor → cliente (push) |
| `0X03A7` | `PushRequestRemoveMirrorKnightSign` | `PushRequestRemoveMirrorKnightSign` | `—` | Servidor → cliente (push) |
| `0X03A5` | `PushRequestSummonMirrorKnightSign` | `PushRequestSummonMirrorKnightSign` | `—` | Servidor → cliente (push) |
| `0X039E` | `RequestCreateMirrorKnightSign` | `RequestCreateMirrorKnightSign` | `RequestCreateMirrorKnightSignResponse` | Cliente → servidor (request/reply) |
| `0X03A1` | `RequestGetMirrorKnightSignList` | `RequestGetMirrorKnightSignList` | `RequestGetMirrorKnightSignListResponse` | Cliente → servidor (request/reply) |
| `0X03A4` | `RequestRejectMirrorKnightSign` | `RequestRejectMirrorKnightSign` | `RequestRejectMirrorKnightSignResponse` | Cliente → servidor (request/reply) |
| `0X03A0` | `RequestRemoveMirrorKnightSign` | `RequestRemoveMirrorKnightSign` | `RequestRemoveMirrorKnightSignResponse` | Cliente → servidor (request/reply) |
| `0X03A2` | `RequestSummonMirrorKnightSign` | `RequestSummonMirrorKnightSign` | `RequestSummonMirrorKnightSignResponse` | Cliente → servidor (request/reply) |
| `0X039F` | `RequestUpdateMirrorKnightSign` | `RequestUpdateMirrorKnightSign` | `RequestUpdateMirrorKnightSignResponse` | Cliente → servidor (request/reply) |

### Break In (Invaders)

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03FD` | `PushRequestAllowBreakInTarget` | `PushRequestAllowBreakInTarget` | `—` | Servidor → cliente (push) |
| `0X03FB` | `PushRequestBreakInTarget` | `PushRequestBreakInTarget` | `—` | Servidor → cliente (push) |
| `0X03FC` | `PushRequestRejectBreakInTarget` | `PushRequestRejectBreakInTarget` | `—` | Servidor → cliente (push) |
| `0X03D3` | `RequestBreakInTarget` | `RequestBreakInTarget` | `RequestBreakInTargetResponse` | Cliente → servidor (request/reply) |
| `0X03D2` | `RequestGetBreakInTargetList` | `RequestGetBreakInTargetList` | `RequestGetBreakInTargetListResponse` | Cliente → servidor (request/reply) |
| `0X03D4` | `RequestRejectBreakInTarget` | `RequestRejectBreakInTarget` | `RequestRejectBreakInTargetResponse` | Cliente → servidor (request/reply) |

### Vistors (Join via covenenant I think)

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03D1` | `PushRequestRemoveVisitor` | `PushRequestRemoveVisitor` | `—` | Servidor → cliente (push) |
| `0X03D0` | `PushRequestRejectVisit` | `PushRequestRejectVisit` | `—` | Servidor → cliente (push) |
| `0X03CF` | `PushRequestVisit` | `PushRequestVisit` | `—` | Servidor → cliente (push) |
| `0X03D5` | `RequestGetVisitorList` | `RequestGetVisitorList` | `RequestGetVisitorListResponse` | Cliente → servidor (request/reply) |
| `0X03D6` | `RequestVisit` | `RequestVisit` | `RequestVisitResponse` | Cliente → servidor (request/reply) |
| `0X03D7` | `RequestRejectVisit` | `RequestRejectVisit` | `RequestRejectVisitResponse` | Cliente → servidor (request/reply) |

### Can't find registration in code

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03EE` | `RequestNotifyRingBell` | `RequestNotifyRingBell` | `RequestNotifyRingBellResponse` | Cliente → servidor (request/reply) |

### Quick Match

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03E5` | `PushRequestAllowQuickMatch` | `PushRequestAllowQuickMatch` | `—` | Servidor → cliente (push) |
| `0X03E1` | `PushRequestJoinQuickMatch` | `PushRequestJoinQuickMatch` | `—` | Servidor → cliente (push) |
| `0X03E3` | `PushRequestRejectQuickMatch` | `PushRequestRejectQuickMatch` | `—` | Servidor → cliente (push) |
| `0X03E7` | `PushRequestRemoveQuickMatch` | `PushRequestRemoveQuickMatch` | `—` | Servidor → cliente (push) |
| `0X03DD` | `RequestJoinQuickMatch` | `RequestJoinQuickMatch` | `RequestJoinQuickMatchResponse` | Cliente → servidor (request/reply) |
| `0X03D9` | `RequestRegisterQuickMatch` | `RequestRegisterQuickMatch` | `RequestRegisterQuickMatchResponse` | Cliente → servidor (request/reply) |
| `0X03DE` | `RequestRejectQuickMatch` | `RequestRejectQuickMatch` | `RequestRejectQuickMatchResponse` | Cliente → servidor (request/reply) |
| `0X03DC` | `RequestSearchQuickMatch` | `RequestSearchQuickMatch` | `RequestSearchQuickMatchResponse` | Cliente → servidor (request/reply) |
| `0X03DA` | `RequestUnregisterQuickMatch` | `RequestUnregisterQuickMatch` | `RequestUnregisterQuickMatchResponse` | Cliente → servidor (request/reply) |
| `0X03DB` | `RequestUpdateQuickMatch` | `RequestUpdateQuickMatch` | `RequestUpdateQuickMatchResponse` | Cliente → servidor (request/reply) |

### Death Count

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X03F0` | `RequestGetTotalDeathCount` | `RequestGetTotalDeathCount` | `RequestGetTotalDeathCountResponse` | Cliente → servidor (request/reply) |

### Misc

| Opcode | Tipo interno | Protobuf | Resposta | Direção no DS2_Game |
|---|---|---|---|---|
| `0X0320` | `RequestSendMessageToPlayers` | `RequestSendMessageToPlayers` | `RequestSendMessageToPlayersResponse` | Cliente → servidor (request/reply) |
| `0X0389` | `ManagementTextMessage` | `ManagementTextMessage` | `—` | Servidor → cliente (push) |

## Entradas comentadas ou ressalvas do upstream

- `PushRequestEvaluateBloodMessage` está ativo no mapa, mas o próprio comentário diz que não foi encontrada utilização no código.
- `PushRequestRemoveBreakInTarget` está comentado porque não foi encontrada registration.
- `PushRequestNotifyRingBell` está comentado porque não foi encontrada registration.
- `RequestGetRegulationFile` está comentado porque não foi encontrada registration.
- `RequestCreateBloodstain` é `DEFINE_MESSAGE`, não request/reply.
- O mapeamento descreve o servidor DSOS para DS2 SOTFS, não um trace capturado do executável Xbox 360.

## Limite de compatibilidade

Este mapa não identifica o protocolo do Xbox 360, seu hostname, porta, identidade, autenticação, chave criptográfica ou payload. Não autoriza enviar pacotes ao console nem alterar rede, jogo ou memória. A implementação DSOS documentada é PC/Steam e não comprova que o Xbox 360 use os mesmos opcodes.

Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

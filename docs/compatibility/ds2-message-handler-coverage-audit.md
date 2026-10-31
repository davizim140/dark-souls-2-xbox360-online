# Auditoria de cobertura dos handlers de mensagens DS2

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Arquivos comparados:
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessageTypes.inc`
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`
- Os 13 arquivos `DS2_*Manager.cpp` que implementam `OnMessageReceived`, listados na matriz abaixo.

## Resultado da comparação estática

| Grupo | Entradas de request/mensagem no mapa | Casos roteados por `OnMessageReceived` |
|---|---:|---:|
| Mapa total | 82 | — |
| Push do servidor | 19 | Não entram como requests recebidos pelo servidor |
| Request/reply ou mensagem de entrada | 63 | 62 |
| Entrada sem handler encontrado | 1 | 0 |

**Única entrada não coberta:** `RequestNotifyRingBell`, opcode `0x03EE`. Ela está declarada como `DEFINE_REQUEST_RESPONSE` no mapa, mas não aparece em nenhum dos 13 blocos `OnMessageReceived` e `DS2_Game::RegisterGameManagers` não registra um manager de sino. Isto indica ausência de rota de handler nesta implementação fixada; não prova que o jogo Xbox envie essa mensagem nem explica se a função foi abandonada, omitida ou implementada por outro caminho.

## Handlers encontrados por manager

| Manager | Casos roteados |
|---|---|
| Boot | `RequestWaitForUserLogin`, `RequestGetAnnounceMessageList` |
| Player Data | `RequestUpdateLoginPlayerCharacter`, `RequestUpdatePlayerStatus`, `RequestUpdatePlayerCharacter`, `RequestGetLoginPlayerCharacter`, `RequestGetPlayerCharacter` |
| Ghosts | `RequestCreateGhostData`, `RequestGetGhostDataList` |
| Blood Message | `RequestReentryBloodMessage`, `RequestGetBloodMessageEvaluation`, `RequestCreateBloodMessage`, `RequestRemoveBloodMessage`, `RequestGetBloodMessageList`, `RequestGetAreaBloodMessageList`, `RequestEvaluateBloodMessage` |
| Bloodstain | `RequestCreateBloodstain`, `RequestGetBloodstainList`, `RequestGetAreaBloodstainList`, `RequestGetDeadingGhost` |
| Break In | `RequestGetBreakInTargetList`, `RequestBreakInTarget`, `RequestRejectBreakInTarget` |
| Logging | `RequestNotifyBuyItem`, `RequestNotifyDeath`, `RequestNotifyDisconnectSession`, `RequestNotifyJoinGuestPlayer`, `RequestNotifyJoinSession`, `RequestNotifyKillEnemy`, `RequestNotifyKillPlayer`, `RequestNotifyLeaveGuestPlayer`, `RequestNotifyLeaveSession`, `RequestNotifyMirrorKnight`, `RequestNotifyOfflineDeathCount` |
| Misc | `RequestSendMessageToPlayers`, `RequestGetTotalDeathCount` |
| Visitor | `RequestGetVisitorList`, `RequestVisit`, `RequestRejectVisit` |
| Ranking | `RequestRegisterPowerStoneData`, `RequestGetPowerStoneRanking`, `RequestGetPowerStoneMyRanking`, `RequestGetPowerStoneRankingRecordCount` |
| Mirror Knight | `RequestGetMirrorKnightSignList`, `RequestCreateMirrorKnightSign`, `RequestRemoveMirrorKnightSign`, `RequestUpdateMirrorKnightSign`, `RequestSummonMirrorKnightSign`, `RequestRejectMirrorKnightSign` |
| Signs | `RequestGetSignList`, `RequestCreateSign`, `RequestRemoveSign`, `RequestUpdateSign`, `RequestSummonSign`, `RequestRejectSign`, `RequestGetRightMatchingArea` |
| Quick Match | `RequestSearchQuickMatch`, `RequestUnregisterQuickMatch`, `RequestUpdateQuickMatch`, `RequestJoinQuickMatch`, `RequestRejectQuickMatch`, `RequestRegisterQuickMatch` |

## O que a auditoria não afirma

- A comparação é entre o mapa de mensagens e os blocos de roteamento do servidor DSOS para DS2 SOTFS.
- Encontrar um caso em `OnMessageReceived` só prova que existe uma rota para um método handler; não prova que toda a lógica está completa, que o comportamento replica o retail ou que o payload é compatível com Xbox 360.
- As 19 entradas push são mensagens enviadas pelo servidor e não foram contadas como requests de entrada.
- A entrada de sino sem handler não é uma instrução para criar um handler sem conhecer o comportamento e os dados esperados.
- O protocolo, a identidade, autenticação, endpoints e payloads do Xbox 360 continuam não identificados.

Nenhum código upstream foi alterado. Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

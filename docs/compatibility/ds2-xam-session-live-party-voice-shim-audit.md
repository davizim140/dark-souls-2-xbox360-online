# Auditoria XAM: sessões, Xbox Live, grupos e voz no MajulaRecomp

## Escopo e fonte

Esta auditoria complementa `ds2-xbox360-scholar-recomp-reference-audit.md`. Examina apenas a implementação pública do ambiente ReXGlue no repositório externo `hazevauks/MajulaRecomp`, fixada no commit:

`42872ca089736170442ca8724e3e728a93537acb`

Arquivos consultados:
- `sdk/src/kernel/xam/xam_party.cpp`
- `sdk/src/kernel/xam/xam_voice.cpp`
- `sdk/src/kernel/xam/apps/xlivebase_app.cpp`
- `sdk/src/kernel/xam/export_table.inc`
- `sdk/src/kernel/xam/xam_net.cpp`

**Limite essencial:** esses arquivos descrevem como o recompiler responde a imports XAM/XNet. Eles não provam quais imports o XEX retail de Scholar chama durante uma conexão, nem documentam o protocolo de rede original do console.

## Evidência de sessões e grupos

O arquivo `export_table.inc` lista os nomes e ordinais:
- `XamSessionCreateHandle` — ordinal `0x00000316`
- `XamSessionRefObjByHandle` — ordinal `0x00000317`
- `XamShowJoinSessionInProgressUI` — ordinal `0x00000301`
- `XamShowJoinSessionByIdInProgressUI` — ordinal `0x00000313`
- `XamShowPartyUI` — ordinal `0x00000305`
- `XamShowPartyInviteUI` — ordinal `0x00000306`
- `XamShowCommunitySessionsUI` — ordinal `0x0000030B`

A presença na tabela de exports é uma referência de nomenclatura/ordinal. Isoladamente, não prova que o jogo importe ou execute cada função.

## Grupos/convites: implementação ReXGlue

Em `xam_party.cpp`:
- `XamPartyGetUserList` retorna `0x807D0003`; o comentário diz que um título específico espera esse código para pular o carregamento dos dados de party.
- `XamPartySendGameInvites`, `XamPartySetCustomData` e `XamPartyGetBandwidth` retornam `X_ERROR_FUNCTION_FAILED`.
- Diversas funções são exportadas como `REX_EXPORT_STUB`, incluindo `XamPartyCreate`, `XamPartyJoin`, `XamPartyJoinEx`, `XamPartyLeave`, `XamPartySendInvite`, `XamPartyGetState`, `XamPartyGetInfo` e `XamPartySetConnectivityGraph`.

Isso não implementa party matchmaking ou convites online.

## Xbox Live base: serviços, amigos e convites

Em `xlivebase_app.cpp`, o dispatcher do app XLiveBase (app id `0xFC`) apresenta:
- Mensagem `0x00058004`: escreve o valor 1 no buffer, descrito pelo código como um provável indicador booleano de logon.
- Mensagem `0x00058006`: escreve 1, identificado no comentário como `XONLINE_NAT_OPEN`.
- Mensagem `0x00058007`: caminho associado a `XOnlineGetServiceInfo`; retorna `0x80151802` (`ERROR_CONNECTION_INVALID`).
- Mensagem `0x00058020`: enumeração de amigos não implementada; retorna `X_E_FAIL`.
- Mensagem `0x00058023`: consulta de informações de convite de jogo aceito não implementada; retorna `X_E_FAIL`.
- Mensagem `0x00058037`: inicialização de presença retorna sucesso.
- Mensagem `0x00058046`: retorna sucesso, mas o comentário marca a operação como não implementada.

O retorno de sucesso em algumas mensagens não equivale a autenticação Live, consulta de serviço, presença remota ou matchmaking funcional. O próprio código retorna falha para enumeração de amigos e informações de convite e erro de conexão para serviço.

## Voz

Em `xam_voice.cpp`:
- `XamVoiceIsActiveProcess` retorna 0; comentário diz que isso interrompe boa parte do caminho de voz.
- `XamVoiceCreate` zera o ponteiro de saída e retorna `X_ERROR_ACCESS_DENIED`.
- `XamVoiceClose` e `XamVoiceHeadsetPresent` retornam 0.
- `XamVoiceSubmitPacket`, `XamVoiceGetBatteryStatus` e várias outras funções são exports stub.

Portanto, não existe implementação de transporte de voz demonstrada por esse código.

## Implicações para o projeto

1. As funções de sessão/party/voz e os serviços XLiveBase são superfícies relevantes para análise estática futura do XEX.
2. A camada ReXGlue atual não oferece uma implementação Xbox Live reutilizável: várias operações retornam falha, sucesso simplificado ou stubs.
3. A lista de exports não pode ser tratada como lista de imports efetivamente usados pelo jogo.
4. Não se deve substituir esses stubs por respostas inventadas: primeiro é necessário provar quais chamadas o jogo faz e quais estruturas/estados espera.
5. Essa auditoria não estabelece endpoint, porta, formato de pacote, autenticação, identidade ou protocolo comunitário Xbox 360.

## Segurança e limites

- Somente código-fonte público do recompiler foi consultado.
- Nenhum binário do jogo foi baixado, alterado ou executado.
- Nenhuma chamada de rede foi feita ao console.
- Nenhuma configuração de rede ou do Xbox foi alterada.
- Nenhum XEX foi criado ou executado neste projeto.

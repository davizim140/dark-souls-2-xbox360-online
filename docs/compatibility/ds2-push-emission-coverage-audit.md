# Auditoria de emissão das mensagens push DS2

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Fontes examinadas:
- `Source/Server.DarkSouls2/Server/Streams/DS2_Frpg2ReliableUdpMessageTypes.inc`
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`
- Os 13 arquivos `DS2_*Manager.cpp` registrados em `DS2_Game::RegisterGameManagers`
- Definições protobuf DS2 e usos encontrados no código-fonte do commit fixado.

## Resultado

O mapa declara **19 tipos de push**. A busca por construção e envio direto pelo servidor encontrou emissão explícita para **17**. Os outros dois não são construídos pelo Quick Match Manager, mas há um caminho separado que impede classificá-los como totalmente não transmitidos:

| Push | ID | Evidência no commit |
|---|---:|---|
| `PushRequestAllowQuickMatch` | `0x03E5` | Declaração no mapa/protobuf e validação no NRSSR sanitizer; sem emissão encontrada |
| `PushRequestRemoveQuickMatch` | `0x03E7` | Declaração no mapa/protobuf e validação no NRSSR sanitizer; sem emissão encontrada |

Os outros 17 tipos têm pelo menos um caminho de emissão direta identificado nos managers DS2 ou em `DS2_Game::SendManagementMessage`. Entre os exemplos estão:
- `PlayerInfoUploadConfigPushMessage`, enviado pelo Boot Manager;
- pushes de sinais, visitantes, break-in e Quick Match;
- `PushRequestEvaluateBloodMessage`, enviado pelo Blood Message Manager;
- `ManagementTextMessage`, construído e enviado por `DS2_Game::SendManagementMessage`.

## Caminho indireto: retransmissão de push enviado pelo cliente

O handler `DS2_MiscManager::Handle_RequestSendMessageToPlayers` lê `Request->message()` como bytes, chama `DS2_NRSSRSanitizer::ValidatePushMessages` quando as verificações estão ativas e, se aprovado, retransmite o protobuf bruto aos destinatários com `SendRawProtobuf`.

Isso muda a interpretação dos dois casos acima:
- `PushRequestAllowQuickMatch` é explicitamente reconhecido pelo sanitizer, mas o ramo ainda tem TODO de validação e retorna `Valid`. Portanto pode passar pelo relay genérico; não foi encontrada construção própria pelo servidor.
- `PushRequestRemoveQuickMatch` está na lista de tipos aceitos pelo sanitizer sem validação específica e também pode passar pelo relay genérico; não foi encontrada construção própria pelo servidor.
- O código comenta que `RequestSendMessageToPlayers` é usado também em Quick Match e outros IDs ainda não identificados. Isso torna plausível a retransmissão de pushes Quick Match pelo relay, mas não comprova quais eventos retail enviam esses dois tipos, nem o formato exato usado pelo Xbox 360.

Assim, a conclusão correta é: **17 pushes com emissão direta encontrada; 2 sem emissão direta encontrada, mas com caminho de retransmissão genérico possível**.

## Interpretação cuidadosa

- “Sem emissão direta encontrada” significa que a busca estática não encontrou construção/envio pelo código do servidor. Não significa que o tipo não possa ser encaminhado pelo relay genérico.
- A presença no sanitizer não significa emissão direta: o sanitizer valida payloads de entrada para o relay genérico.
- `ManagementTextMessage` não está num manager; é enviado pelo método `DS2_Game::SendManagementMessage`.
- Não confundir o identificador de push dentro do protobuf com o `msg_type = 0x0320` genérico do cabeçalho de mensagem.
- O relay genérico aumenta a superfície de mensagens que o servidor pode encaminhar, mas não equivale a lógica server-side específica de Quick Match.
- A comparação é DSOS DS2/PC e não confirma que o Xbox 360 use esses IDs, protobufs, conteúdo ou fluxo.

Nenhum código upstream foi alterado. Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

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

O mapa declara **19 tipos de push**. A busca por construção e envio no código DS2 encontrou emissão explícita para **17**. Dois tipos aparecem no mapa/protobuf e no sanitizer, mas não foi encontrado código DS2 que os construa e envie:

| Push | ID | Evidência no commit |
|---|---:|---|
| `PushRequestAllowQuickMatch` | `0x03E5` | Declaração no mapa/protobuf e validação no NRSSR sanitizer; sem emissão encontrada |
| `PushRequestRemoveQuickMatch` | `0x03E7` | Declaração no mapa/protobuf e validação no NRSSR sanitizer; sem emissão encontrada |

Os outros 17 tipos têm pelo menos um caminho de emissão identificado nos managers DS2 ou em `DS2_Game::SendManagementMessage`. Entre os exemplos estão:
- `PlayerInfoUploadConfigPushMessage`, enviado pelo Boot Manager;
- pushes de sinais, visitantes, break-in e Quick Match;
- `PushRequestEvaluateBloodMessage`, enviado pelo Blood Message Manager;
- `ManagementTextMessage`, construído e enviado por `DS2_Game::SendManagementMessage`.

## Interpretação cuidadosa

- “Sem emissão encontrada” significa que a busca estática no código DS2 do commit fixado não encontrou uma construção/envio desses dois tipos. Não prova que eles sejam impossíveis no servidor retail, que estejam ausentes do cliente ou que não possam ser enviados por outro mecanismo externo.
- A presença no sanitizer não significa emissão: o sanitizer valida payloads de entrada.
- `ManagementTextMessage` não está num manager; é enviado pelo método `DS2_Game::SendManagementMessage`.
- Não confundir o identificador de push dentro do protobuf com o `msg_type = 0x0320` genérico do cabeçalho de mensagem.
- A comparação é DSOS DS2/PC e não confirma que o Xbox 360 use esses IDs, protobufs, conteúdo ou fluxo.

Nenhum código upstream foi alterado. Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

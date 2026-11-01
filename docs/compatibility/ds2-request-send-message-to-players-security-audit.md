# Auditoria de segurança do relay RequestSendMessageToPlayers (DS2)

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Arquivos examinados:
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Misc/DS2_MiscManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/Utils/DS2_NRSSRSanitizer.h`
- `Source/Server/Config/BuildConfig.h`
- `Source/Server/Server/Server.cpp`
- `Protobuf/DarkSouls2/DS2_Frpg2RequestMessage.proto`

## Formato do pedido

`RequestSendMessageToPlayers` contém:
- `player_ids`: lista repetida de IDs inteiros de jogadores;
- `message`: bytes obrigatórios, normalmente um protobuf push cujo primeiro campo identifica o tipo.

O handler copia os bytes recebidos e, quando aceita o pedido, encaminha os mesmos bytes por `SendRawProtobuf` a cada cliente localizado por `FindClientByPlayerId`. Não há reconstrução da mensagem pelo manager.

## Controles efetivamente ativados no commit

`BuildConfig.h` define ambos como `true`:
- `SEND_MESSAGE_TO_PLAYERS_SANITY_CHECKS`
- `NRSSR_SANITY_CHECKS`

O primeiro ativa o limite de destinatários e a chamada ao sanitizer. O servidor também desativa a publicação na lista pública se `SEND_MESSAGE_TO_PLAYERS_SANITY_CHECKS` estiver desligado. Portanto, no commit fixado, os controles não estão apenas comentados: estão habilitados por configuração de compilação.

## O que o handler verifica

1. Rejeita o encaminhamento se a lista contiver mais de **6 entradas**. O código conta entradas de `player_ids`, não IDs distintos.
2. Com os controles NRSSR ativos, tenta interpretar o cabeçalho protobuf e rejeita dados que o sanitizer classifica como inválidos.
3. Para cada ID, procura um cliente conectado. Se não existir, registra aviso e continua com os demais.
4. Para cada cliente encontrado, encaminha os bytes originais com `SendRawProtobuf`.
5. Envia uma resposta protobuf vazia ao remetente mesmo quando o encaminhamento foi recusado pelo controle de segurança. Se não conseguir enviar essa resposta, retorna erro.

## Limites da validação do conteúdo

O sanitizer não oferece validação estrutural completa para DS2 neste commit:

- `ValidateEntryList` retorna imediatamente `Valid`; o comentário diz que o formato DS2 é diferente e ainda precisa ser decifrado.
- `PushRequestAllowBreakInTarget` é desserializado, mas a validação da lista interna termina nessa função que sempre retorna `Valid`.
- `PushRequestVisit` e `PushRequestAllowQuickMatch` têm TODO de validação e retornam `Valid`.
- `ManagementTextMessage` é rejeitado como tipo de entrada.
- Vários outros tipos permitidos passam pelo switch sem validação específica do corpo; o comentário diz que não parecem conter dados que precisem de validação, mas isso não equivale a uma verificação de esquema completa.
- Tipos não reconhecidos são rejeitados.

Assim, a configuração habilita os controles, mas isso não significa que todos os corpos protobuf encaminhados tenham validação profunda. A proteção específica de NRSSR DS2 está incompleta no código auditado.

## Limites de autorização observáveis no handler

No corpo de `Handle_RequestSendMessageToPlayers` não foi encontrada uma verificação explícita que relacione:
- o remetente aos destinatários pedidos;
- os destinatários a uma mesma sessão, arena ou atividade;
- a permissão do remetente para enviar aquele tipo específico ao destinatário.

O handler verifica se o destinatário está conectado e aplica o limite de seis entradas. Isso é uma observação limitada a esta função; não prova que inexista qualquer controle em outra camada ou no cliente retail.

A lista pode conter IDs repetidos: o limite é aplicado ao número de entradas e o loop processa cada entrada. Não foi encontrada deduplicação neste handler.

## Implicações para uma implementação independente

Uma implementação nova não deve copiar o relay de forma permissiva. Antes de encaminhar mensagens entre jogadores, precisaria de:
- identidade autenticada e vinculada à sessão;
- autorização explícita por tipo de mensagem e contexto de jogo;
- limite de tamanho e quantidade de destinatários;
- deduplicação e validação dos destinatários;
- validação completa, específica de cada esquema protobuf;
- testes negativos para IDs arbitrários, destinatários desconectados, payload truncado, tipo desconhecido e tentativas de envio fora da sessão.

Esses são requisitos de projeto derivados dos limites observados, não afirmações sobre o protocolo oficial do Xbox.

## Fronteira de compatibilidade

Esta auditoria descreve somente a implementação DSOS DS2/PC no commit fixado. Não prova que o jogo Xbox 360 envie `RequestSendMessageToPlayers`, use esses campos, compartilhe o mesmo conjunto de IDs ou aceite esse mecanismo de relay. O protocolo Xbox 360 permanece não identificado.

Nenhum código upstream foi alterado. Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

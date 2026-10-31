# Auditoria DS2: configuração de upload de status

- Upstream: `TLeonardUK/ds3os`
- Commit de referência: `56406879a31505a71bea8c6290da370067f43659`
- Código principal: [DS2_BootManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Boot/DS2_BootManager.cpp)
- Configuração: [RuntimeConfig.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Config/RuntimeConfig.h)
- Schema: [DS2_Frpg2RequestMessage.proto](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Protobuf/DarkSouls2/DS2_Frpg2RequestMessage.proto)

## 1. Quando a configuração é enviada

No handler `Handle_RequestWaitForUserLogin`, após resolver/criar o jogador e enviar a resposta de login, o DSOS cria `PlayerInfoUploadConfigPushMessage`. Esse push contém:
- `player_character_update_send_delay`
- `player_status_send_delay`
- uma lista `config.player_data_mask`
- `config.upload_interval`

Se o envio do push falhar, o handler retorna erro. O código mostra a ordem de envio no DSOS; não comprova que o cliente Xbox use o mesmo fluxo.

## 2. Máscara estática configurada pelo DSOS

O código declara 93 valores na máscara:

```text
0–4
100–115
200–206
300–315
400–408
500–523
600–605
700–703
800–805
```

A contagem acima é 5 + 16 + 7 + 16 + 9 + 24 + 6 + 4 + 6 = 93 valores, não 101. O total correto da lista literal é **93**.

O schema apenas declara `player_data_mask` como uma lista de flags. Não documenta o significado de cada flag nem liga cada número a um campo específico de `AllStatus`. Portanto, não é correto inferir que, por exemplo, o grupo 100–115 corresponda diretamente ao campo protobuf 1 ou a um bloco de atributos.

## 3. Intervalos e delays do RuntimeConfig upstream

| Configuração | Valor padrão no código | Observação do comentário |
|---|---:|---|
| `PlayerStatusUploadInterval` | 15 s | Frequência dos updates periódicos; comentário diz que cliente limita mínimo a 5 s |
| `PlayerStatusUploadSendDelay` | 300 s | Delay adicional; comentário diz clamp de 60 a 50000 |
| `PlayerCharacterUpdateSendDelay` | 600 s | Delay adicional; comentário diz clamp de 60 a 50000 |

São defaults do servidor DSOS, não valores medidos do Xbox. O comentário sobre clamp descreve comportamento observado pelo autor no cliente investigado, sem demonstrar que o executável Xbox compartilhe esse comportamento.

## 4. O que ainda não sabemos

- O significado individual dos 93 números da máscara.
- Se a máscara é interpretada como flags de campo interno do jogo, grupos de dados ou outra tabela.
- Se o Xbox 360 recebe/aceita esse push e se usa os mesmos intervalos.
- Se o Xbox envia `RequestUpdatePlayerStatus` com protobuf `AllStatus` idêntico.
- Se os campos de identidade usados pelo Xbox são Steam ID, XUID ou outro identificador.

## 5. Conclusão de compatibilidade

O código confirma que o DSOS envia uma máscara fixa e três parâmetros temporais após login no seu caminho DS2. Isso documenta a configuração do servidor upstream, não o comportamento de um servidor oficial nem a compatibilidade do cliente Xbox 360.

Não alterar o jogo, identidade, rede ou console com base nesses números. Nenhum cliente Xbox, servidor funcional ou XEX foi produzido ou validado por esta auditoria.

## 6. Próxima investigação estática

Seguir o caminho de armazenamento do character blob e do status no DSOS: identificar o que é persistido no banco, o que permanece apenas em memória e quais managers consultam cada estrutura. Isso ajuda a separar estado persistente de presença online sem pressupor equivalência com o Xbox.

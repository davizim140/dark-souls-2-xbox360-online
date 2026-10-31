# DSOS: auditoria do caminho servidor de login, autenticação e jogo

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Esta auditoria descreve o que o servidor DSOS implementa. Ela não descreve um cliente Xbox 360 e não prova que o jogo de console use o mesmo protocolo.

Fontes upstream:

- [LoginClient.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/LoginService/LoginClient.cpp)
- [LoginService.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/LoginService/LoginService.cpp)
- [AuthClient.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/AuthService/AuthClient.cpp)
- [GameService.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/GameService/GameService.cpp)
- [GameClient.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/GameService/GameClient.cpp)
- [Frpg2ReliableUdpMessageStream.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/Streams/Frpg2ReliableUdpMessageStream.cpp)
- [DS2_Game.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/DS2_Game.cpp)

## 1. Login TCP

`LoginService::Init()` cria um `NetConnectionTCP` e escuta `LoginServerPort`.

O `LoginClient` recebe mensagens FRPG2 e aceita somente `RequestQueryLoginServerInfo`. O payload é interpretado como protobuf compartilhado Steam; a resposta contém o IP escolhido pelo servidor e `AuthServerPort`.

O código escolhe IP privado quando o endereço remoto está numa rede privada; caso contrário usa o IP público configurado/detectado. O login não cria sessão de jogador nem valida um ticket: ele apenas encaminha o cliente ao serviço de autenticação.

## 2. Autenticação TCP

`AuthService::Init()` cria outro `NetConnectionTCP` em `AuthServerPort`. O `AuthClient` implementa uma máquina de estados com a sequência:

1. `RequestHandshake`: recebe `aes_cwc_key`; envia uma resposta de 27 bytes sem cifra (11 bytes aleatórios e 16 zeros, conforme o código); ativa CWC com a chave recebida.
2. `GetServiceStatus`: lê `steam_id` e `app_version`; confere a versão contra `GameConfig`.
3. `KeyMaterial`: exige payload de 8 bytes e devolve 16 bytes; os primeiros 8 são copiados do cliente e os outros 8 são aleatórios. O resultado vira `GameCwcKey`.
4. `SteamTicket`: exige essa mensagem e interpreta os bytes 0–15 como `GameCwcKey`; os bytes restantes são o ticket Steam. Com `AUTH_ENABLED`, valida usando `SteamGameServer()->BeginAuthSession`.
5. Após autenticar, envia informações do servidor de jogo e um `auth_token` aleatório; registra o par token/chave CWC no `GameService`.

O próprio código comenta que parte do handshake/chave é pouco compreendida. Não tratar os comentários como especificação formal.

## 3. Entrada no serviço de jogo UDP

`GameService::Init()` abre `NetConnectionUDP` na `GameServerPort`.

Quando chega um datagrama/conexão UDP, `HandleClientConnection()` tenta ler os primeiros 8 bytes como `uint64_t AuthToken`. Se não houver 8 bytes ou se o token não existir no mapa de estados de autenticação, a conexão é ignorada. Se existir, o servidor cria `GameClient` com a chave CWC e o token correspondentes.

O `GameClient` cria `Frpg2ReliableUdpMessageStream`, que usa a camada reliable-UDP/fragmentação e a interface de jogo selecionada. A cada mensagem válida, os managers registrados recebem a mensagem em ordem até um deles declarar que a tratou. O token é atualizado enquanto o cliente permanece ativo; o estado de autenticação expira após o timeout configurado.

## 4. Despacho específico de Dark Souls II

`DS2_Game` mapeia tipos protobuf DS2 para tipos de mensagem reliable-UDP e faz o mapeamento inverso para instanciar o protobuf apropriado. A tabela de tipos está em `DS2_Frpg2ReliableUdpMessageTypes.inc`.

Na inicialização, registra managers DS2 de boot, dados de jogador, ghosts, mensagens de sangue, bloodstains, invasões, logging, misc, visitantes, rankings, Mirror Knight, sinais e Quick Match. Esses managers processam as mensagens depois que a conexão já passou pela validação do token e pelo transporte reliable-UDP.

## 5. O que essa cadeia prova — e o que não prova

| Evidência no servidor DSOS | Limite |
|---|---|
| Login TCP e resposta com endereço/porta de autenticação | Não identifica o primeiro pacote do Xbox 360 |
| Autenticação TCP com handshake CWC, status e ticket Steam | Não prova que o console use Steam ou a mesma sequência |
| Token de 8 bytes lido no início da entrada UDP | Não prova tamanho/formato do token enviado pelo Xbox 360 |
| Reliable UDP + protobuf DS2 | Não prova que o console tenha o mesmo transporte ou codificação |
| Managers DS2 registrados | Prova que o backend tem lógica de jogo DS2, não que aceite cliente Xbox |

A implementação do emulador de cliente em `Source/Server/Client/Client.cpp` também é uma referência PC/Steam; não é uma captura nem implementação de cliente Xbox 360.

## 6. Próxima evidência necessária

Para avançar de forma responsável no Xbox 360, ainda falta uma fonte específica do cliente Xbox: documentação/protocolo publicado para a versão de console, ou uma especificação independente verificável. Sem isso, não devemos codificar um adaptador que suponha login TCP, Steam ID/ticket, CWC, token de 8 bytes ou reliable UDP idênticos.

## Escopo de segurança

Somente leitura de código público upstream e documentação no repositório deste projeto. Nenhuma alteração no jogo, roteador, DNS ou memória; nenhum XEX criado ou executado.

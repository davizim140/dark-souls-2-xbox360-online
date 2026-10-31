# Auditoria das mensagens Xbox One encontradas no DSOS

## Fonte e versão

Auditoria do upstream `TLeonardUK/ds3os`, commit fixado
`56406879a31505a71bea8c6290da370067f43659`.

Arquivos examinados:

- `Protobuf/Shared/Shared_Frpg2RequestMessage.proto`
- `Source/Server/Server/LoginService/LoginClient.cpp`
- `Source/Server/Server/AuthService/AuthClient.cpp`
- `Protobuf/DarkSouls2/DS2_Frpg2RequestMessage.proto`

Links para o código original:

- [Shared_Frpg2RequestMessage.proto](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Protobuf/Shared/Shared_Frpg2RequestMessage.proto)
- [LoginClient.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/LoginService/LoginClient.cpp)
- [AuthClient.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server/Server/AuthService/AuthClient.cpp)
- [DS2_Frpg2RequestMessage.proto](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Protobuf/DarkSouls2/DS2_Frpg2RequestMessage.proto)

## Descoberta: existem stubs Xbox One

O arquivo compartilhado declara duas mensagens separadas:

- `RequestQueryLoginServerInfoForXboxOne`
- `GetServiceStatusForXboxOne`

Os comentários do próprio upstream dizem que a primeira presumivelmente substitui a consulta de login Steam no Xbox e talvez carregue um identificador específico da plataforma. Para a segunda, o comentário presume um identificador Xbox One em vez de `steam_id`.

Esses comentários são hipóteses do autor, não uma especificação confirmada. Os corpos protobuf contêm somente comentários de tags observadas; não há nomes ou semântica de campos documentados.

O arquivo de protocolo específico de DS2 também declara `LoginClientInfo` e `LoginForXboxOne`, mas ambos estão vazios no schema auditado.

## O que o servidor realmente aceita

O caminho de login implementado em `LoginClient.cpp` verifica se o tipo da mensagem recebida é exatamente `RequestQueryLoginServerInfo`. Em seguida, tenta decodificar o payload como essa mensagem Steam, e responde com IP e porta do serviço de autenticação.

O mesmo arquivo não apresenta um ramo para `RequestQueryLoginServerInfoForXboxOne`.

No caminho de autenticação, `AuthClient.cpp` espera a sequência PC:

1. `RequestHandshake` com uma chave AES-CWC;
2. `GetServiceStatus`, cujo parser lê `steam_id` e `app_version`;
3. `KeyMaterial`;
4. `SteamTicket`, validado por `SteamGameServer()->BeginAuthSession`.

O fluxo implementado não apresenta tratamento para `GetServiceStatusForXboxOne` nem autenticação Xbox. Portanto, a mera existência das classes protobuf geradas não significa que o servidor implemente o fluxo Xbox One.

## Limite de compatibilidade para Xbox 360

| Evidência no DSOS | O que podemos concluir |
|---|---|
| Mensagens nomeadas Xbox One no schema compartilhado | Alguém identificou ou inferiu mensagens de uma plataforma Xbox One |
| Comentários com tags, sem semântica completa | O formato ainda não está documentado de forma suficiente |
| Stubs vazios no schema DS2 | Não há estrutura de payload DS2 detalhada nesses tipos |
| LoginClient aceita somente a consulta Steam | O login server auditado não implementa essa variante Xbox |
| AuthClient exige Steam ID e ticket Steam | O caminho de autenticação auditado continua sendo Steam/PC |

**Não é evidência de Xbox 360.** O nome explícito é Xbox One. Não se deve transferir os campos, IDs ou fluxo para Xbox 360 sem identificar a build do console e obter evidência independente.

## Próxima fronteira técnica

Antes de implementar compatibilidade de console, ainda precisamos identificar, por evidência específica do Xbox 360:

- tipo e conteúdo da primeira mensagem de login;
- identificador de conta usado pelo jogo;
- serviço e método de autenticação;
- negociação de chaves e formato de transporte;
- sequência de conexão entre login, autenticação e serviço de jogo.

O erro de conexão relatado pelo usuário não fornece esses dados.

## Segurança e escopo

Esta auditoria é somente leitura do código upstream. Não altera o jogo, não modifica DNS/roteador/memória, não injeta código, não cria XEX e não executa nada no console.

**Conclusão:** o DSOS contém vestígios de mensagens Xbox One, mas o servidor implementado continua aceitando o caminho Steam descrito acima. Isso não fornece um protocolo Xbox 360 nem um plugin pronto.

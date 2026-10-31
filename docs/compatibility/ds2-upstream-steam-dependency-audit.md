# Auditoria de dependências do DSOS DS2: loader, identidade e serviços

## Escopo

Auditoria estática do DSOS no commit upstream
`56406879a31505a71bea8c6290da370067f43659`. O objetivo é separar o servidor DS2
existente das dependências do cliente/infraestrutura PC e identificar o que
não pode ser reaproveitado diretamente no Xbox 360.

## Evidências no código

### 1. Configuração de cliente DS2 no loader upstream

Em `Source/Loader/Config/BuildConfig.cs` existe uma entrada ativa para:

- versão declarada: `Dark Souls II - 1.0.3.0 (Steam)`;
- tamanho de executável registrado: `28200992` bytes;
- Steam App ID: `335300`;
- `UseInjector = true`;
- `UsesASLR = false`;
- `ServerInfoAddress = 0` e chave TEA vazia nessa entrada.

A entrada anterior `1.0.2.0` está comentada. O próprio comentário diz que a
versão antiga não é suportada por falta de mitigações RCE.

**Limite:** essa é uma configuração de executável Steam para PC. Não identifica
nem valida o executável Xbox 360, não é um patch Xbox e não fornece offsets,
chaves ou método aplicável ao console.

### 2. O processo de servidor tem dependência Steam

Em `Source/Server/Server/Server.cpp`, o servidor padrão:

- cria os serviços Login, Auth, Game e WebUI;
- inicializa Steam Game Server API com `SteamGameServer_Init`;
- usa o Steam App ID da configuração de jogo;
- cria ou carrega par de chaves RSA e configura banco SQLite;
- resolve hostname/IP público e privado antes de inicializar os serviços.

A inicialização Steam é explícita no caminho do servidor padrão. Portanto,
compilar o DSOS não equivale a obter um backend independente de Steam pronto
para clientes Xbox.

### 3. Portas padrão configuradas no upstream

Em `Source/Server/Config/RuntimeConfig.h`, os defaults incluem:

| Serviço | Porta |
|---|---:|
| Auth | 50000 |
| WebUI | 50005 |
| Game | 50010 |
| Login | 50050 |
| Master server | 50020 |
| Faixa inicial para servidores de jogo adicionais | 50060 |

Esses números descrevem defaults do DSOS upstream, não endpoints do jogo Xbox.
Não devem ser configurados no console ou roteador como tentativa de conexão.

### 4. O adaptador DS2 não remove a dependência de autenticação

O servidor escolhe `DS2_Game` quando `GameType` é DS2, mas essa seleção acontece
dentro do mesmo processo que inicializa os serviços comuns. O adaptador de
mensagens DS2 e os managers multiplayer são apenas a camada de jogo; eles não
demonstram que login, autenticação, descoberta de servidor e identidade estejam
compatíveis com o Xbox.

## Consequências para o projeto Xbox 360

1. Reutilizar o código dos managers DS2 é uma possibilidade de backend, não uma
   prova de compatibilidade ponta a ponta.
2. A autenticação Steam do DSOS PC não deve ser copiada para o Xbox nem
   substituída por XUID sem evidência do protocolo real do jogo.
3. As portas default DSOS não são evidência de portas usadas pelo cliente Xbox.
4. Não há justificativa técnica para criar agora um XEX ou alterar o console.
5. A próxima implementação útil deve ser isolada no backend: desacoplar a
   inicialização Steam por interface/configuração e testar a camada DS2 sem
   alegar compatibilidade Xbox. A identidade e o handshake Xbox permanecem
   bloqueados até existir evidência específica do cliente Xbox.

## Fontes upstream fixadas

- `Source/Loader/Config/BuildConfig.cs`
- `Source/Server/Config/RuntimeConfig.h`
- `Source/Server/Server/Server.cpp`
- `Source/Server/Server/ServerManager.cpp`

Todas as referências acima foram lidas no commit
`56406879a31505a71bea8c6290da370067f43659`.

## Conclusão

O DSOS contém um adaptador de jogo DS2 e uma configuração de loader para uma
versão Steam de PC, mas a infraestrutura comum ainda tem dependência explícita
de Steam. O projeto Xbox precisa de uma camada de autenticação/descoberta
compatível, cuja especificação não pode ser deduzida das portas ou da entrada
Steam do loader. Nenhum cliente Xbox, servidor Xbox compatível ou XEX foi
produzido ou validado por esta auditoria.

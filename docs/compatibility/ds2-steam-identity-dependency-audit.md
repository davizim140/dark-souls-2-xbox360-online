# Auditoria de identidade Steam no caminho multiplayer DS2

## Escopo

Leitura estática do DSOS no commit upstream
`56406879a31505a71bea8c6290da370067f43659`. Esta auditoria identifica onde a
identidade Steam entra no backend DS2 e por que não basta trocar o login para
tornar o servidor compatível com Xbox 360.

## Evidências

### Login e associação de cliente

`Source/Server.DarkSouls2/Server/GameService/GameManagers/Boot/DS2_BootManager.cpp`:

- o pedido `RequestWaitForUserLogin` fornece `steam_id`;
- o manager resolve/cria o jogador usando esse identificador;
- a resposta devolve `steam_id` e `player_id`;
- o estado conectado e o nome da conexão são associados ao Steam ID.

Isso estabelece Steam ID como chave de identidade no fluxo DSOS implementado.
Não estabelece qual campo, formato ou processo de autenticação o executável
Xbox usa.

### Identidade propagada pelos recursos multiplayer

A pesquisa no código DS2 encontrou uso de `Player.GetSteamId()` ou campos
`player_steam_id` / `steam_id` em:

- visitantes e pedidos de visita;
- invasões e pedidos de break-in;
- sinais de invocação e rejeições;
- Quick Match;
- Mirror Knight;
- criação de mensagens de sangue;
- criação de fantasmas;
- criação de manchas de sangue.

A identidade não fica confinada ao login. Ela aparece em mensagens push,
respostas e registros persistentes dos recursos multiplayer. Uma adaptação
Xbox exigiria definir uma identidade canônica e revisar cada contrato de
mensagem e persistência que transporta Steam ID.

### Persistência

As auditorias de player data e character persistence já registram que o DSOS
usa Steam ID para resolver o jogador e associa os dados persistentes ao
PlayerId interno. O PlayerId interno é atribuído pelo servidor; não é prova de
que o cliente Xbox envie um Steam ID nem de que um XUID possa ser usado no mesmo
campo sem incompatibilidade.

## Implicações de implementação

1. **Não fazer substituição textual Steam ID → XUID.** Tamanhos, codificação,
   autenticação, unicidade e semântica do campo no protocolo Xbox são
   desconhecidos.
2. **Não alterar agora os protobufs upstream.** Os campos observados pertencem
   ao protocolo DSOS/PC e não foram comparados com payloads Xbox.
3. **Separar identidade externa da chave interna do jogador** seria uma
   refatoração de backend plausível, mas só deve ser implementada com testes de
   migração e uma especificação de identidade Xbox comprovada.
4. A prova mínima necessária continua sendo uma captura/documentação legítima
   do fluxo de login Xbox ou uma especificação pública confiável. O erro de
   conexão relatado não revela o identificador utilizado.

## Limites

- A pesquisa demonstra dependência Steam no código upstream analisado, não o
  formato do protocolo Xbox.
- Nenhum XUID foi observado no tráfego ou código do cliente Xbox.
- Não há handshake Xbox implementado, cliente conectado, servidor Xbox
  compatível ou XEX produzido/validado.
- Esta auditoria não recomenda patch do jogo, spoof de identidade, alteração
  de DNS/roteador ou execução de XEX.

## Fontes upstream fixadas

- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Boot/DS2_BootManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Visitor/DS2_VisitorManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/BreakIn/DS2_BreakInManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Signs/DS2_SignManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/QuickMatch/DS2_QuickMatchManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/MirrorKnight/DS2_MirrorKnightManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/BloodMessage/DS2_BloodMessageManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Ghosts/DS2_GhostManager.cpp`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Bloodstain/DS2_BloodstainManager.cpp`

## Conclusão

A identidade Steam é uma dependência transversal do DSOS DS2, não apenas um
detalhe do serviço de login. O backend pode ser reutilizado como referência,
mas a compatibilidade Xbox depende de descobrir e validar o protocolo real de
identidade/autenticação do cliente Xbox antes de qualquer adaptação.

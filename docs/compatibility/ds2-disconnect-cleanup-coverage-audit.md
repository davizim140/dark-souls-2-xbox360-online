# Auditoria de limpeza de estado quando um cliente DS2 desconecta

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Arquivos principais:
- `Source/Server/Server/GameService/GameService.cpp`
- `Source/Server/Server/GameService/GameManager.h`
- `Source/Server/Server/GameService/GameClient.cpp`
- `Source/Server.DarkSouls2/Server/DS2_Game.cpp`
- os 13 managers DS2 registrados por `DS2_Game::RegisterGameManagers`.

## Ciclo de desconexão no serviço compartilhado

Quando `GameClient::Poll()` sinaliza que o cliente deve sair, `GameService::Poll()`:

1. move o cliente para a lista `DisconnectingClients`;
2. chama `MessageStream->Disconnect()`;
3. percorre todos os managers registrados e chama `OnLostPlayer(Client)`;
4. remove o cliente da lista ativa `Clients`;
5. continua bombeando conexão/stream até o estado reliable-UDP ficar `Closed`, quando remove a referência da lista de desconexão.

O contrato de `GameManager::OnLostPlayer` diz que ele é chamado quando um jogador previamente registrado é perdido. A implementação padrão é vazia. Portanto, chamar o callback em todos os managers não significa que todos executem limpeza.

## Cobertura observada nos 13 managers DS2

| Manager | Implementa OnLostPlayer? | Ação observada |
|---|---|---|
| Boot | Não | Herda callback vazio |
| PlayerData | Não | Herda callback vazio |
| Ghosts | Não | Herda callback vazio |
| BloodMessage | Não | Herda callback vazio |
| Bloodstain | Não | Herda callback vazio |
| BreakIn | Sim | Override existe, mas corpo vazio |
| Logging | Não | Herda callback vazio |
| Misc | Não | Herda callback vazio |
| Visitor | Não | Herda callback vazio |
| Ranking | Não | Herda callback vazio |
| MirrorKnight | Sim | Remove sinais ativos do jogador do cache e notifica jogadores que estavam cientes |
| Signs | Sim | Remove sinais ativos do jogador do cache e notifica jogadores que estavam cientes |
| QuickMatch | Sim | Remove partidas hospedadas pelo jogador desconectado |

A lista acima corresponde aos managers registrados por `DS2_Game::RegisterGameManagers`, não a todos os managers do projeto para outros jogos.

## Detalhes confirmados

- `DS2_SignManager::OnLostPlayer` percorre `Client->ActiveSummonSigns`, remove cada sinal com `RemoveSignAndNotifyAware` e limpa o vetor.
- `DS2_MirrorKnightManager::OnLostPlayer` faz o equivalente para `ActiveMirrorKnightSummonSigns`.
- Ambos notificam os jogadores que estavam marcados como cientes, usando pushes de remoção, e limpam `BeingSummonedByPlayerId` e `AwarePlayerIds` no objeto de sinal.
- `DS2_QuickMatchManager::OnLostPlayer` remove da lista `Matches` as partidas cujo `HostPlayerId` é o PlayerId do cliente desconectado. A função não percorre partidas em que ele apareça apenas como participante.
- `DS2_BreakInManager::OnLostPlayer` existe, mas está vazio.
- O restante dos managers não declara override de `OnLostPlayer` nos arquivos examinados e, portanto, usa o callback vazio da classe base.

## O que esta auditoria não demonstra

A ausência de override não prova, por si só, vazamento ou estado órfão: algumas operações podem ser transitórias, armazenadas em outro objeto ou limpas por outro caminho. Em particular, esta auditoria não conclui que visitantes, invasões ou mensagens persistidas ficam necessariamente presos após desconexão.

O que fica demonstrado é uma diferença de cobertura: a limpeza explícita por callback está concentrada em sinais normais, sinais Mirror Knight e partidas hospedadas. A rotina de desconexão chama todos os managers, mas BreakIn não faz nada nesse callback.

## Requisitos para uma implementação independente

Antes de reproduzir matchmaking/sessões:
- definir proprietário e ciclo de vida para cada sinal, invasão, visita e partida;
- limpar tanto estado hospedado quanto participações de clientes que saem;
- notificar participantes restantes sem enviar eventos duplicados;
- tornar limpeza idempotente para desconexão abrupta, timeout e encerramento normal;
- testar saída do host, saída do participante, perda simultânea de participantes e repetição do callback.

Esses itens são recomendações de engenharia derivadas da cobertura observada, não afirmações sobre o protocolo retail.

## Fronteira Xbox 360

Esta auditoria descreve o código DSOS DS2/PC no commit fixado. Não prova que o Xbox 360 use os mesmos callbacks, estruturas, PlayerId, protocolo ou regras de desconexão. O protocolo Xbox 360 continua não identificado.

Nenhum código upstream foi alterado. Nenhum XEX foi criado ou executado. Nenhum teste foi feito no console.

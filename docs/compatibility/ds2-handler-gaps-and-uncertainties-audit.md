# Auditoria de lacunas e incertezas nos handlers DS2

## Fonte fixada

Upstream: `TLeonardUK/ds3os`  
Commit: `56406879a31505a71bea8c6290da370067f43659`

Arquivos examinados: os 13 `DS2_*Manager.cpp` registrados por `DS2_Game::RegisterGameManagers`.

## Achados explícitos no código

| Área | Evidência no código | Leitura segura |
|---|---|---|
| Visitantes | `DS2_VisitorManager.cpp`: TODO para ordenar alvos potenciais por prioridade/quantidade de summons | A seleção de alvos existe, mas a ordenação prioritária está explicitamente pendente |
| Logging de morte | `DS2_LoggingManager.cpp`: TODO para implementar o restante do comportamento do DS3 em `Handle_RequestNotifyDeath` | O handler registra estatísticas de morte e responde; outras ações planejadas não foram implementadas nesse trecho |
| Mensagens de sangue | `DS2_BloodMessageManager.cpp`: TODO sobre diferença entre `max_type_1` e `max_type_2`, tanto por célula quanto por área | O servidor soma os limites; a semântica separada dos dois campos permanece desconhecida |
| Sinais de invocação | `DS2_SignManager.cpp`: TODO de validação em `Handle_RequestRejectSign` | O próprio autor marcou como não validado o payload push de rejeição |
| Mirror Knight | `DS2_MirrorKnightManager.cpp`: TODO de validação em `Handle_RequestRejectMirrorKnightSign` | Mesmo tipo de incerteza no payload push de rejeição do Mirror Knight |
| Quick Match | `DS2_QuickMatchManager.cpp`: comentário questiona se `RequestUpdateQuickMatch` apenas mantém a partida viva | O handler responde com sucesso, mas o propósito completo do update não está confirmado |
| Matching area | `DS2_SignManager.cpp`: comentário diz que o algoritmo de seleção não replica necessariamente o servidor oficial | A implementação estima áreas possíveis pela população de jogadores; a regra retail permanece incerta |
| Logging | `DS2_LoggingManager.cpp`: TODO “rest of things from ds3” | Não se deve presumir paridade de todos os efeitos de logging do DS3 no DS2 |

## Respostas vazias: não classificar automaticamente como stub

Há handlers que enviam uma resposta protobuf vazia. Em alguns casos o próprio código registra que o cliente não funciona sem essa resposta, por exemplo `Handle_RequestRejectSign` e `Handle_RequestRejectMirrorKnightSign`. Portanto, resposta vazia pode ser parte necessária do contrato de protocolo; não é prova isolada de handler incompleto.

Outros handlers também enviam respostas vazias enquanto registram estatísticas ou encaminham eventos. A auditoria não os marca como ausentes apenas por isso.

## Prioridade para pesquisa futura

1. Identificar os campos e regras de `max_type_1` / `max_type_2` por evidência do cliente retail, sem inferir valores.
2. Verificar o payload de rejeição de sinais e Mirror Knight contra uma especificação ou trace autorizado do cliente.
3. Esclarecer a semântica de `RequestUpdateQuickMatch` e a regra retail de matching area.
4. Separar os efeitos DS2 realmente usados dos comportamentos herdados ou apenas planejados no logging.

## Limites

- São lacunas e comentários do código DSOS para DS2 Scholar of the First Sin, não uma especificação oficial do jogo.
- Não provam que qualquer um desses campos, mensagens ou algoritmos seja igual no Xbox 360.
- Não foram alterados arquivos do upstream.
- Não houve captura de tráfego, alteração de jogo/console/rede ou teste em console.
- Nenhum XEX foi criado ou executado.

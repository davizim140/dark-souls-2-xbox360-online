# Auditoria upstream: invasões e visitas por pactos (DS2)

- Referência upstream: `TLeonardUK/ds3os`
- Commit auditado: `56406879a31505a71bea8c6290da370067f43659`
- Arquivos:
  - [DS2_BreakInManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/BreakIn/DS2_BreakInManager.cpp)
  - [DS2_BreakInManager.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/BreakIn/DS2_BreakInManager.h)
  - [DS2_VisitorManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Visitor/DS2_VisitorManager.cpp)
  - [DS2_VisitorManager.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Visitor/DS2_VisitorManager.h)

## 1. Invasões (Break In)

O manager registra três pedidos: obter lista de alvos, iniciar invasão contra um jogador e rejeitar uma invasão.

- A busca exclui o próprio solicitante e filtra jogadores por área, salvo quando `IgnoreInvasionAreaFilter` está ativo; nesse caminho alternativo, compara a área atual do alvo com as áreas jogadas registradas no estado do solicitante.
- A elegibilidade depende de invasões não estarem globalmente desativadas e do alvo estar marcado como invadível.
- Blue Eye Orb exige dados de status e pelo menos 10 sinner points.
- Red Eye Orb e Blue Eye Orb aplicam regras configuráveis de Soul Memory.
- A lista de alvos respeita `max_targets` e retorna player ID e Steam ID no modelo DSOS.
- Ao solicitar a invasão, o servidor procura o alvo pelo player ID e envia um push ao alvo. Se não encontrar o jogador ou falhar o envio, envia um push de rejeição ao invasor.
- A rejeição do alvo é encaminhada ao invasor original.

## 2. Visitas por pactos (Visitor)

O manager registra busca de visitantes, pedido de visita e rejeição.

- A busca filtra por tipo de visitante/pacto e por elegibilidade configurada.
- Blue Sentinels, Bell Keepers e Rat usam parâmetros específicos de Soul Memory.
- O código declara um ponteiro para parâmetros gerais de covenant/invasão, mas esse ponteiro não é usado no restante da função auditada.
- Há um TODO explícito para ordenar os alvos por prioridade (por exemplo, quantidade de invocações).
- O pedido de visita pode transportar `player_struct`. Quando `NRSSR_SANITY_CHECKS` está habilitado, o payload é validado por `DS2_NRSSRSanitizer`.
- Se o alvo existe e o push é enviado, o servidor envia ao solicitante uma notificação de remoção do visitante e registra estatísticas.
- Se a validação falha, o alvo não existe ou o envio falha, o solicitante recebe um push de rejeição.
- A rejeição é encaminhada ao iniciador original.

## 3. Limites e pontos que exigem investigação

- Estes handlers são código do servidor DS2 no projeto DSOS; não demonstram que o cliente retail de Xbox 360 use o mesmo protocolo, campos, identidade ou sequência de mensagens.
- O código usa Steam ID e player ID do modelo DSOS. Não há evidência aqui de que o Xbox use Steam ID; XUID ou outro identificador permanecem hipóteses não confirmadas.
- A auditoria do handler de busca não prova que o cliente Xbox envie os mesmos campos nem que o servidor consiga autenticar uma sessão Xbox.
- O comportamento de `IgnoreInvasionAreaFilter` merece teste e leitura de configuração antes de reproduzir a regra; seu nome pode sugerir um efeito diferente do caminho observado.
- A função `CanMatchWith` de visitantes seleciona uma configuração geral que não é consumida depois; não inferir que esses parâmetros gerais efetivamente filtrem os alvos.
- A transferência de `player_struct` depende de validação e compatibilidade do formato NRSSR. Não copiar ou aceitar payloads sem compreender o formato e as proteções.
- Não há evidência nesta auditoria de conexão direta entre consoles, relay, autenticação Xbox ou compatibilidade com TU/build específica.

## 4. Conclusão

O upstream contém lógica server-side para descoberta e encaminhamento de invasões e visitas por pactos. Isso é material útil para mapear funcionalidades, mas ainda não é uma implementação pronta para Xbox 360. Nenhum cliente Xbox, servidor compatível, patch ou XEX foi produzido ou validado por esta auditoria.

## 5. Próxima investigação estática

Auditar player data/status e os pontos de integração do GameService: como o estado de jogador é criado, atualizado, persistido e disponibilizado aos managers. Manter separadas as evidências do servidor DSOS e as hipóteses sobre o cliente Xbox retail.

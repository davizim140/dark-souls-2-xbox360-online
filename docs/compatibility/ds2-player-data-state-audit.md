# Auditoria upstream: dados e estado do jogador (DS2)

- Referência upstream: `TLeonardUK/ds3os`
- Commit auditado: `56406879a31505a71bea8c6290da370067f43659`
- Arquivos:
  - [DS2_PlayerDataManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/PlayerData/DS2_PlayerDataManager.cpp)
  - [DS2_PlayerDataManager.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/PlayerData/DS2_PlayerDataManager.h)
  - [DS2_PlayerState.h](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/DS2_PlayerState.h)
  - [DS2_BootManager.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/GameService/GameManagers/Boot/DS2_BootManager.cpp)
  - [DS2_Game.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Server.DarkSouls2/Server/DS2_Game.cpp)

## 1. Estado de sessão e login

No handler de login auditado, o DSOS:
- Lê o campo `steam_id` da requisição.
- Resolve ou cria um registro de jogador no banco usando essa identidade.
- Associa um player ID interno à sessão e devolve Steam ID e player ID.
- Envia um push de configuração que define máscara de campos de status e intervalos de upload.

Isso descreve a implementação DSOS para PC. Não prova que a versão retail Xbox envie Steam ID ou use a mesma identidade. XUID ou outro identificador continuam desconhecidos.

## 2. Upload de status do jogador

O handler `RequestUpdatePlayerStatus`:
- Faz parse de um objeto protobuf `AllStatus` recebido dentro do campo `status`.
- Mescla os dados recebidos ao estado mantido no servidor.
- Limpa arrays específicos antes do merge para evitar acumulação indevida de elementos repetidos.
- Atualiza nome do personagem, área online e área de atividade.
- Extrai dados usados no matchmaking, como Soul Memory e Soul Level.
- Calcula se o jogador está invadível: no código observado, deixa de estar invadível se estiver sentado em uma bonfire, se uma Human Effigy estiver queimada ou se a área de atividade online for zero.
- Calcula o visitor pool com base em pacto, itens ativos e áreas específicas: Blue Sentinels, Bell Keepers e Rat.
- Marca o primeiro estado recebido para distinguir a inicialização de atualizações posteriores.
- Registra bonfires recém-desbloqueadas e pode emitir notificações do servidor.

Se o protobuf não puder ser parseado, o handler registra aviso e retorna como tratado, aguardando novo envio em vez de encerrar a sessão.

## 3. Personagem e persistência

O manager também trata:
- Seleção/criação do personagem de login quando o ID recebido é zero, evitando IDs locais e IDs já existentes no banco.
- Atualização dos bytes de dados do personagem no banco.
- Consulta de dados de personagem por player ID e character ID.
- Consulta do personagem de login de um jogador conectado.

O cabeçalho do manager comenta que esses dados parecem ser usados principalmente para detecção de trapaça; o próprio comentário reconhece incerteza sobre o quanto outros managers os utilizam. Portanto, não afirmar que todos os recursos online dependem do blob completo de personagem.

## 4. Estrutura DS2_PlayerState

O estado especializado DS2 mantém, entre outros:
- Área online atual.
- Área de atividade online mais específica.
- Tipo de visitor pool.
- Objeto completo `AllStatus`.

O código expõe Soul Memory e tempo de jogo a partir do status. Algumas estatísticas genéricas retornam zero ou descrição vazia, portanto não são implementações completas de todas as métricas possíveis.

## 5. Integração dos managers

`DS2_Game::RegisterGameManagers` registra Boot, PlayerData e os managers de fantasmas, mensagens, manchas de sangue, invasões, visitantes, sinais, rankings, Mirror Knight e Quick Match. O jogo cria um `DS2_PlayerState` para cada jogador.

Isso confirma a integração desses módulos no servidor DSOS, não que um cliente Xbox retail consiga estabelecer sessão ou fornecer os mesmos dados.

## 6. Riscos e lacunas para Xbox 360

- Não temos captura nem especificação confirmada das mensagens enviadas pela versão Xbox 360.
- Os nomes e campos protobuf do DSOS não demonstram compatibilidade binária com a versão Xbox.
- A identidade Steam usada pelo upstream não pode ser substituída por XUID sem evidência de como o cliente Xbox autentica e identifica a sessão.
- A máscara de upload e os intervalos configurados são valores do servidor DSOS; não são parâmetros confirmados para Xbox.
- O formato binário do personagem e os campos de status ainda precisam de confirmação independente para o build Xbox identificado no projeto.
- A falha de conexão reportada no Xbox não permite concluir que o problema esteja no login, no upload de status ou em qualquer manager específico.

## 7. Conclusão

O upstream mostra que o estado de jogador é a base compartilhada para localização, elegibilidade de invasão, pactos, Soul Memory, Soul Level e persistência de personagem. É uma referência técnica útil para projetar um servidor, mas ainda não fornece o protocolo retail Xbox nem uma implementação compatível.

Nenhum patch, cliente modificado, servidor Xbox funcional ou XEX foi criado ou validado por esta auditoria.

## 8. Próxima investigação estática

Auditar os campos protobuf de `AllStatus`, os tipos de dados de personagem e o caminho de armazenamento no banco, separando campos conhecidos de campos ainda sem significado confirmado. Não assumir que os campos observados no upstream correspondem ao payload do Xbox 360.

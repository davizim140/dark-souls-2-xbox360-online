# Análise da falha de conexão — Xbox 360

## Evidência observada

Relato de teste do proprietário do console:

- Jogo: Dark Souls II: Scholar of the First Sin.
- Title ID: `465307E4`.
- Media ID: `458B3E06`.
- Região: NTSC.
- Title Update: nenhum.
- O jogo inicia e chega ao menu principal.
- Ao tentar usar o recurso online, aguarda alguns segundos durante a calibração e exibe: `Falha ao se conectar ao servidor do jogo dark souls 2`.

Esta é uma observação relatada pelo usuário, não uma captura de rede nem uma reprodução independente.

## O que a mensagem permite concluir

1. O executável inicia e a falha ocorre depois de selecionar a função online.
2. O cliente não conclui o fluxo que ele considera necessário para entrar no serviço online.
3. O texto exibido não identifica qual etapa falhou.
4. A palavra “calibração” na interface não prova que houve conexão com um servidor de calibração específico.
5. Não é possível inferir hostname, endereço IP, porta, protocolo, identidade usada ou formato de autenticação a partir dessa mensagem.

## Etapas candidatas — ainda não confirmadas no Xbox

| Etapa | Referência DSOS para PC | Xbox 360 |
|---|---|---|
| Descoberta de serviço | Login TCP retorna endereço do serviço de autenticação | Desconhecida |
| Autenticação | Handshake TCP, CWC e ticket Steam | Desconhecida |
| Obtenção de sessão | Serviço retorna token, chave e endpoint de jogo | Desconhecida |
| Transporte do jogo | UDP, token, CWC e FRPG2 Reliable UDP | Desconhecido |
| Login do jogador | Protobuf `RequestWaitForUserLogin` com Steam ID | Desconhecido |
| Estado do jogador | Upload de AllStatus | Desconhecido |

A coluna DSOS descreve o cliente emulado de PC e não deve ser tratada como protocolo do Xbox.

## Próxima evidência que realmente discrimina as hipóteses

Sem alterar o console, o roteador, DNS ou a instalação do jogo, precisamos de pelo menos uma das seguintes evidências:

- **Análise estática autorizada do executável exato:** identificação de imports, bibliotecas e referências a APIs de rede, sem publicar o binário.
- **Registro de conexão produzido por ferramenta já disponível no ambiente:** horário, protocolo, destino e porta, com IPs públicos, identificadores e tokens sanitizados antes de compartilhar.
- **Documentação técnica específica da edição Xbox 360:** fonte que associe explicitamente a versão do jogo a um serviço ou protocolo.

Um print da mensagem de erro pode confirmar o texto e o momento, mas não revela sozinho a etapa de rede.

## Registro de observação reproduzível

Ao relatar uma nova tentativa, anote apenas:

- se o console estava conectado à Xbox Live;
- se o erro ocorreu antes ou depois de escolher o modo online;
- tempo aproximado até o erro;
- texto exato exibido;
- se o jogo continuou utilizável offline.

Não envie perfil, senha, token, endereço residencial, captura integral de tráfego ou arquivos do jogo.

## Decisão técnica atual

**Status: protocolo Xbox 360 não identificado.**

Não implementar ainda um endpoint de login, porta UDP, ticket substituto ou conversor de XUID. O backend DSOS não pode aceitar o cliente Xbox apenas porque parte do protocolo de jogo do PC já foi documentada. A próxima implementação de rede depende de evidência Xbox específica.

# Auditoria de migração: identidade DSOS para identidade externa

## Escopo e fonte

Auditoria estática do DSOS upstream no commit
`56406879a31505a71bea8c6290da370067f43659`, especialmente:

- `Source/Server/Server/Database/ServerDatabase.cpp`
- `Source/Server/Server/Database/ServerDatabase.h`
- `Source/Server.DarkSouls2/Server/GameService/GameManagers/Boot/DS2_BootManager.cpp`
- Managers DS2 que gravam ou consultam dados de jogador.

Esta é uma análise do modelo de dados upstream. Não é uma migração executada nem uma prova de compatibilidade Xbox.

## Estrutura confirmada

A tabela `Players` contém `PlayerId INTEGER PRIMARY KEY AUTOINCREMENT` e `PlayerSteamId CHAR(50)`. O método `FindOrCreatePlayer` procura por `PlayerSteamId` e cria um novo registro quando não encontra.

O identificador Steam também aparece diretamente em tabelas relacionadas:
- `BloodMessages.PlayerSteamId`
- `Bloodstains.PlayerSteamId`
- `Ghosts.PlayerSteamId`
- `Bans.PlayerSteamId`
- `AntiCheatStates.PlayerSteamId`
- `AntiCheatLogs.PlayerSteamId`

Outras tabelas guardam `PlayerId` como referência, incluindo `Characters`, `Rankings` e registros de mensagens/fantasmas/manchas de sangue. Os dados de personagens são persistidos em BLOBs.

No boot DS2, o pedido de login fornece `steam_id`; o servidor usa esse valor para localizar/criar o jogador e devolve `steam_id` e `player_id`. O identificador é propagado para vários managers de jogo.

## Consequências para a migração

1. Não renomear simplesmente `PlayerSteamId` para `ExternalIdentity`: as tabelas de conteúdo e moderação também dependem do valor.
2. Preservar os `PlayerId` existentes é essencial para manter a associação com personagens, rankings e conteúdo persistido.
3. Criar uma tabela de identidades externas com chave única `(provider, identity_value)` é uma direção possível, mas não basta alterar o login. Todos os pontos de leitura/escrita e os dados históricos precisam de uma estratégia coerente.
4. Valores Steam legados não devem ser interpretados como XUID. A conversão para outro provedor só pode ocorrer quando o protocolo Xbox e a origem/autenticidade desse identificador forem comprovados.
5. A migração deve ser transacional, idempotente, com backup, contagem de linhas antes/depois e validação de órfãos. A base original deve permanecer intocada durante os testes.

## Plano seguro de implementação

- Fase A: manter o DSOS upstream intacto e testar o novo esquema em cópia isolada.
- Fase B: importar os registros legados preservando `PlayerId` e registrar a identidade como provedor `steam` apenas para dados realmente Steam.
- Fase C: atualizar acesso a banimentos, antitrapaça e managers de conteúdo para usar a identidade interna/externa de forma consistente.
- Fase D: testar rollback, repetição da migração, colisões, identidades duplicadas e referências a jogadores inexistentes.
- Fase E: somente após evidência do protocolo Xbox, implementar o adaptador de identidade Xbox e os handlers necessários.

## O que ainda não está comprovado

- O formato do identificador usado pelo cliente Xbox 360.
- Se o Xbox usa XUID, outro identificador ou autenticação proprietária.
- O handshake, autenticação, criptografia e descoberta de serviço no cliente retail Xbox.
- Compatibilidade do protocolo DSOS PC com a versão Xbox 360.

Nenhum código do jogo, protocolo de rede, login DSOS ou banco de produção foi alterado por esta auditoria.

# Contrato da migração de cópia DSOS

## Origem verificada

A definição de tabelas foi conferida em `TLeonardUK/ds3os`, arquivo
`Source/Server/Server/Database/ServerDatabase.cpp`, no commit fixado
`56406879a31505a71bea8c6290da370067f43659`.

O esquema cria:

- `Players(PlayerId, PlayerSteamId)`.
- `BloodMessages`, `Bloodstains` e `Ghosts` com `PlayerId` e
  `PlayerSteamId`.
- `Characters` e `Rankings` com `PlayerId`.
- `Bans`, `AntiCheatStates` e `AntiCheatLogs` com `PlayerSteamId`.

O upstream cria essas tabelas sem declarar constraints SQL de foreign key.
A aplicação relaciona conteúdo e personagens por `PlayerId`, mas isso não
deve ser confundido com integridade referencial garantida pelo SQLite.

## O que o importador faz

`tools/migrate_dsos_identity_copy.py`:

1. Abre a origem em modo SQLite somente leitura.
2. Recusa origem e destino iguais e recusa sobrescrever destino existente.
3. Valida `Players.PlayerId` e `Players.PlayerSteamId`.
4. Aborta diante de ID inválido, identidade vazia/não textual ou duplicada.
5. Usa o backup SQLite para criar uma cópia completa.
6. Adiciona `external_identities` com `provider='steam'` e bytes UTF-8
   exatos do valor antigo.
7. Preserva os `PlayerId` e as tabelas legadas; não reescreve colunas
   `PlayerSteamId` nas tabelas de conteúdo.
8. Confere a contagem, o mapeamento de cada jogador e
   `PRAGMA foreign_key_check`.

A tabela nova tem uma linha por jogador, chave única por
`(provider, identity_value)`, e FK para `Players(PlayerId)`. A tabela
legada e os IDs permanecem intactos.

## O que não faz

- Não executa migração no banco real de produção.
- Não substitui Steam ID por XUID ou outro identificador Xbox.
- Não autentica identidades nem associa contas por semelhança.
- Não altera managers, login, protobufs, rede ou código upstream DSOS.
- Não prova que o protocolo do jogo Xbox 360 é compatível com DSOS.

## Como executar, somente em arquivos copiados

```sh
python tools/inspect_dsos_identity_db.py /caminho/copia-dsos.sqlite
python tools/migrate_dsos_identity_copy.py /caminho/copia-dsos.sqlite /caminho/novo-dsos-migrado.sqlite
```

O destino deve ser um caminho novo. Guarde a origem original separadamente.
O importador é uma ferramenta de preparação de dados, não um servidor online.

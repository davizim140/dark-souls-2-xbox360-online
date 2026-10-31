# Registro de identidade externa — contrato inicial

## Componentes

- `ExternalIdentity`: identificador opaco composto por namespace do provedor e bytes.
- `IdentityRegistry`: associação em memória, útil para testes e não persistente.
- `SqliteIdentityStore`: associação persistente entre identidade externa e `PlayerId` interno.

## Persistência SQLite

A tabela `external_identities` usa:

- `player_id`: chave interna inteira, autoincremental.
- `provider`: namespace textual validado.
- `identity_value`: bytes opacos armazenados como BLOB.
- `created_at`: timestamp gerado pelo SQLite.
- Restrição única em `(provider, identity_value)` para impedir duplicação da mesma identidade.

A criação usa `INSERT OR IGNORE` seguido de consulta pela chave única. Assim, chamadas repetidas recuperam o mesmo ID e identidades em namespaces diferentes permanecem distintas. WAL, sincronização FULL e timeout de espera são configurados na conexão.

## Testes automatizados

O teste SQLite cria uma base temporária, registra duas identidades, fecha a conexão e abre uma nova instância. Depois verifica que os mesmos IDs são recuperados após a reabertura.

## Limites importantes

Esta implementação ainda não está integrada ao banco de dados DSOS. É uma base isolada, com um banco SQLite próprio. Não migra contas ou personagens existentes, não autentica o titular e não comprova que o Xbox usa XUID. Não associe uma identidade real de console até existir evidência verificável do protocolo e da origem do identificador.

O código não altera protobufs, login, rede, jogo ou arquivos do console. A persistência aqui é um passo de arquitetura testado, não uma implementação de servidor Xbox funcional.

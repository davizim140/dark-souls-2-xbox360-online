# Registro de identidade externa — contrato inicial

## O que foi adicionado

O backend possui agora ExternalIdentity, um identificador opaco composto por
um namespace de provedor e bytes. IdentityRegistry associa essa identidade a
um PlayerId interno numérico, sem usar diretamente o identificador externo
como chave dos recursos de jogo.

## Comportamento testado

- A mesma identidade recebe o mesmo PlayerId durante a vida do processo.
- Identidades diferentes recebem IDs internos diferentes.
- O namespace do provedor faz parte da identidade.
- Identificadores inválidos são rejeitados.
- O contador não pode voltar a zero nem reutilizar IDs em caso de esgotamento.
- As operações de consulta e criação são protegidas por mutex.

## Limites importantes

Este registro é somente em memória. Os IDs são perdidos ao reiniciar o
processo. Ainda não existe banco de dados, migração de registros DSOS, vínculo
com contas, autenticação, política de banimento ou prova de identidade Xbox.
Não use o namespace xuid nem outro namespace de plataforma até existir
evidência verificável do formato e da origem do identificador no cliente Xbox.

A implementação não está integrada ao DSOS upstream e não altera protobufs,
login, rede, jogo ou arquivos do console. É uma fundação isolada para testar a
separação entre identidade externa e chave interna antes de desenhar persistência.

# Dark Souls II Online Revival — Xbox 360

Projeto comunitário de pesquisa e desenvolvimento para investigar a possibilidade de restaurar recursos online de **Dark Souls II: Scholar of the First Sin** no Xbox 360 RGH.

> **Estado atual:** fase de levantamento técnico. Ainda não existe servidor compatível, cliente modificado ou XEX funcional. Nenhuma compatibilidade com a rede Xbox Live ou com os serviços originais é presumida.

## Objetivos

- Investigar o executável e o protocolo de rede da versão Xbox 360.
- Documentar autenticação, descoberta de serviços, matchmaking e tráfego multiplayer.
- Desenvolver um servidor comunitário independente quando o protocolo estiver suficientemente compreendido.
- Avaliar uma camada de compatibilidade para Xbox 360 RGH.
- Recuperar, se tecnicamente viável, cooperação, invasões/PvP, mensagens, fantasmas e manchas de sangue.

## Organização

- `docs/architecture.md`: arquitetura proposta e limites conhecidos.
- `docs/research-plan.md`: plano de investigação e evidências necessárias.
- `tests/`: verificações automatizadas da documentação e estrutura.
- `.github/workflows/ci.yml`: validação automática no GitHub Actions.

## Requisitos de desenvolvimento

- Desenvolvimento e CI pelo navegador/GitHub sempre que possível.
- XSDK como toolchain-alvo para componentes Xbox 360, após validar a disponibilidade e o ambiente de build.
- Servidor separado do console; não presumir que o XSDK seja necessário para o backend.
- Não distribuir executáveis do jogo, chaves, conteúdo proprietário ou arquivos protegidos.
- Não testar alterações no console antes de validar em ambiente isolado e manter cópias de segurança.

## Estado das funcionalidades

| Recurso | Estado |
|---|---|
| Pesquisa do protocolo Xbox 360 | Não iniciada |
| Login/autenticação comunitária | Não implementado |
| Matchmaking | Não implementado |
| Cooperação/invocação | Não implementado |
| Invasões/PvP | Não implementado |
| Mensagens | Não implementado |
| Fantasmas | Não implementado |
| Manchas de sangue | Não implementado |
| Cliente XEX | Não implementado |
| Servidor compatível | Não implementado |

## Como contribuir

Consulte [docs/research-plan.md](docs/research-plan.md) antes de propor implementação de protocolo. Toda conclusão sobre compatibilidade deve apontar evidências reproduzíveis e distinguir observação de hipótese.

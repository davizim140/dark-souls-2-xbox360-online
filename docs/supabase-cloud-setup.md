# Supabase + servidor externo gratuito

## Estado

A migração inicial está preparada em `supabase/migrations/20261102000100_initial_online_services.sql`.
Ela cria apenas a base de contas comunitárias, identidades externas opacas, personagens,
presença e pedidos de matchmaking. Não implementa o protocolo Xbox 360 nem afirma
que o cliente do jogo já consegue autenticar.

## Hospedagem proposta

- **Supabase Free:** PostgreSQL e Auth para contas comunitárias.
- **Oracle Cloud Always Free (candidato para o gateway):** VM pública que pode executar
  um processo persistente TCP/UDP. A disponibilidade depende da região e da capacidade
  da Oracle; a criação da conta pode exigir cartão para verificação.
- **GitHub Actions:** testes e publicação automatizada depois que a VM existir.

A VM é uma opção de infraestrutura, não uma garantia de disponibilidade contínua.
É necessário configurar firewall/VCN, regras de entrada TCP/UDP e monitorar limites.
Não abra portas até o protocolo e as portas corretas serem conhecidos.

## Aplicar a migração

1. Crie um projeto Supabase no plano Free.
2. Abra **SQL Editor** no painel do projeto.
3. Cole e execute o conteúdo da migração.
4. Confira se as tabelas foram criadas em **Table Editor**.
5. Não envie chaves ou tokens para o GitHub, issues ou chat.

## Segredos e segurança

O servidor externo pode receber, por variáveis de ambiente:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

A chave `service_role` ignora RLS. Ela deve existir somente no servidor confiável,
nunca no XEX, no repositório, em logs ou em builds distribuídos. O Xbox não deve
acessar o banco diretamente com essa chave.

## Limites deliberados

- `external_subject` é opaco: não assumir que seja XUID.
- Nenhuma porta DSOS/Steam foi copiada como porta Xbox 360.
- Matchmaking no banco é somente persistência/fila; a negociação de sessão exige
  o protocolo real do jogo e um serviço TCP/UDP compatível.
- Cooperação, invasões, fantasmas, mensagens do jogo e manchas de sangue ainda
  dependem da análise do tráfego Xbox 360.
- O Supabase Free pode pausar projetos sem atividade por uma semana e tem quotas
  limitadas. Não é adequado prometer disponibilidade de produção.

## Critério para avançar

Só configurar listener público quando houver evidência reproduzível dos endpoints,
transporte, sequência de autenticação e formato de mensagens do Xbox 360.

# Plano de investigação técnica

## Fase 0 — Identificar precisamente o alvo

Registrar, sem compartilhar arquivos protegidos:

- **Title ID informado:** `465307E4`.
- **Title Update informado:** nenhum (jogo sem TU; versão base).
- Media ID, se disponível.
- região/edição e revisão do disco/GOD, se identificável.
- configuração de rede do console.
- se a cópia inicia offline normalmente.

Não presumir que todas as edições chamadas Scholar of the First Sin usam o mesmo executável ou protocolo. Confirmar o alvo Xbox 360 especificamente.

## Fase 1 — Mapear a rede

Em ambiente controlado e autorizado:

1. Observar DNS e conexões de rede iniciadas pelo console durante a inicialização do jogo.
2. Separar tráfego do jogo, Xbox Live e serviços de terceiros.
3. Registrar hostnames, IPs, portas, protocolos e horários.
4. Determinar quais recursos dependem de cada serviço.
5. Redigir capturas sanitizadas; remover IPs privados, identificadores, tokens e credenciais antes de publicar.

**Saída exigida:** relatório reproduzível com evidências, não uma lista de endpoints presumidos.

## Fase 2 — Analisar o cliente

- Identificar imports e bibliotecas de rede no executável obtido legalmente pelo próprio usuário.
- Comparar comportamento offline e online.
- Identificar formatos de mensagens e estado de sessão.
- Distinguir tráfego criptografado de tráfego em claro; não presumir que seja possível decifrá-lo.
- Não publicar binários proprietários.

## Fase 3 — Prova de conceito do servidor

Começar com um serviço mínimo e isolado somente depois de documentar um fluxo real:

- handshake/sessão;
- resposta a uma consulta não sensível;
- teste automatizado cliente-servidor;
- logs sem credenciais.

Não implementar matchmaking ou PvP com base em suposições.

## Fase 4 — Compatibilidade Xbox 360

- Avaliar se DNS/roteamento configurável é suficiente.
- Se for necessária alteração local, desenvolver um módulo pequeno e reversível.
- Validar primeiro em emulador ou ambiente de teste adequado.
- Usar XSDK somente quando o ambiente e as dependências estiverem confirmados.
- Nunca executar um XEX não verificado no console principal.

## Fase 5 — Recursos

Implementar e testar separadamente presença, mensagens, fantasmas, manchas de sangue, matchmaking, cooperação e invasões. O estado de cada recurso deve ser atualizado apenas após teste real.

## Evidências e critérios

Cada afirmação de compatibilidade deve incluir:

- versão exata do cliente;
- ambiente e configuração;
- passos de reprodução;
- logs sanitizados;
- resultado esperado e observado;
- limitações conhecidas.

## Próximo dado necessário

O alvo inicial registrado é **Title ID `465307E4`, sem Title Update**. Ainda precisamos identificar Media ID/região/revisão e observar o tráfego real para confirmar a build e o protocolo. Não envie ISO, GOD, XEX, perfil, credenciais ou arquivos proprietários.

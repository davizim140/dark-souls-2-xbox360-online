# Arquitetura proposta

## Princípio

A versão Xbox 360 é o alvo. A arquitetura abaixo é uma hipótese de trabalho, não uma descrição confirmada do protocolo real do jogo.

```text
Dark Souls II: Scholar — Xbox 360
              |
              | protocolo a identificar
              v
Camada de compatibilidade no console (se necessária)
              |
              | transporte e mensagens documentados
              v
Servidor comunitário
  |-- autenticação/sessões
  |-- presença e descoberta de jogadores
  |-- matchmaking e salas
  |-- mensagens assíncronas
  |-- fantasmas e manchas de sangue
  |-- cooperação e invasões (dependentes do protocolo)
              |
              v
Persistência / banco de dados
```

## Componentes planejados

### 1. Pesquisa de protocolo

Antes de implementar rede, identificar por evidência:

- Title ID e Media ID exatos da cópia de teste.
- Versão/Title Update ativa.
- Bibliotecas de rede utilizadas pelo executável.
- Endpoints, DNS, portas e transporte observados.
- Formato de mensagens, serialização e sequência de autenticação.
- Dependências de Xbox Live, serviços externos ou certificados.

Não publicar segredos, tokens, dados pessoais ou material proprietário.

### 2. Camada Xbox 360

Uma camada nativa só será criada se a pesquisa provar que o cliente precisa de alteração local. O código será isolado e terá builds de teste separados de qualquer release.

O XSDK será avaliado como toolchain. Não existe ainda configuração de build XEX validada neste repositório.

### 3. Backend comunitário

O backend poderá ser executado em uma máquina ou hospedagem separada. A linguagem e o protocolo serão escolhidos após a captura e documentação do tráfego real, em vez de assumir compatibilidade com implementações de PC.

### 4. Recursos online

Cada recurso será implementado individualmente, com testes de protocolo:

- presença e descoberta;
- mensagens e avaliações;
- fantasmas;
- manchas de sangue;
- matchmaking;
- cooperação e invocação;
- invasões e PvP.

## Segurança e limites

- Não modificar a instalação original do jogo.
- Não substituir arquivos do jogo sem backup verificável.
- Não armazenar credenciais Xbox Live.
- Não contornar autenticação de terceiros sem análise técnica e legal.
- Não afirmar risco zero, compatibilidade ou sucesso sem testes.
- A CI atual valida apenas arquivos e documentação; não compila XEX nem servidor.

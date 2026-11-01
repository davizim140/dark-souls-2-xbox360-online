# Auditoria de referência externa: MajulaRecomp e a versão Xbox 360 de Scholar

## Fonte e versão fixadas

Repositório externo: `hazevauks/MajulaRecomp`  
URL: https://github.com/hazevauks/MajulaRecomp  
Commit examinado: `42872ca089736170442ca8724e3e728a93537acb`  
Licença declarada pelo repositório externo: GPL-3.0.

Arquivos consultados:
- `app/ds2_manifest.toml`
- `docs/ds2-notes.md`
- `sdk/src/kernel/xam/xam_net.cpp`
- `sdk/src/kernel/xam/xam_user.cpp`
- `sdk/src/system/xsocket.cpp`
- `sdk/src/kernel/xam/export_table.inc`
- `README.md`

## Por que esta referência é relevante

O manifesto identifica explicitamente o alvo como **Default.xex do disco 1 de Scholar of the First Sin**, com Title ID `465307E4`, o mesmo Title ID registrado neste projeto. O manifesto registra XEX versão `0.0.0.22`, image base `0x82000000`, entry point `0x829C3DE0` e image size `0x016F0000`.

O mesmo manifesto distingue a versão do disco original de 2014 (`0.0.0.8`) da versão Scholar. Portanto, esta referência é mais próxima do alvo deste projeto do que uma análise genérica de DS2 para PC/Steam.

O repositório externo não distribui os arquivos do jogo: o README diz que os arquivos extraídos ficam fora do Git em `assets/` e que o código C++ gerado fica em `app/generated/`. A auditoria aqui não baixa nem reproduz conteúdo proprietário.

## Evidência de rede no executável

`docs/ds2-notes.md` registra que o XEX importa `xam.xex` (210 registros) e `xboxkrnl.exe` (353 registros), ambos na versão `2.0.21256.0`. Também lista as bibliotecas estáticas do XDK `XNET`, `XONLINE`, `XHV2`, `XPARTY` e `XMIC`, entre outras.

O autor do recompiler interpreta esses componentes como a infraestrutura Xbox Live esperada pelo multiplayer do jogo e informa que o port está sendo executado offline. Isso é uma anotação técnica do projeto externo, não uma captura do protocolo online nem uma prova de que cada API listada é chamada em cada fluxo.

## O que a camada XAM do recompiler faz — e não faz

O código de compatibilidade do ReXGlue contém comportamentos que explicam por que o port pode executar offline sem reproduzir Xbox Live:

| API/caminho | Comportamento observado no recompiler |
|---|---|
| `NetDll_XNetStartup` | Retorna sucesso; a criação/inicialização do objeto XNet está comentada |
| `NetDll_XNetCleanup` | Retorna sucesso, mas a limpeza efetiva está marcada como TODO/comentada |
| `NetDll_XNetGetTitleXnAddr` | Preenche endereço de loopback; zera endereço/porta online e dados de identificação online |
| `NetDll_XNetXnAddrToMachineId` | Retorna valor não zero; comentário diz que isso sinaliza ausência de login Live |
| `NetDll_XNetDnsLookup` | TODO; preenche status de erro para a consulta DNS |
| `NetDll_connect` / sockets | Encaminha a conexão para a implementação nativa de sockets do host |
| `XamUserGetXUID` | Lê o XUID do perfil configurado no ambiente de emulação; isso não autentica uma sessão Xbox Live |

O código de `XSocket::SendTo` também contém caminho de socket nativo e comentários sobre integração com XNet ainda incompleta. Essas rotinas são *stubs/shims do ambiente ReXGlue*, não o comportamento do XAM original do Xbox 360.

## Consequência para o Online Revival

1. Existe agora uma referência pública que declara trabalhar com o XEX de Scholar cujo Title ID coincide com o nosso alvo.
2. Ela confirma a presença de bibliotecas XNET/XONLINE e componentes de sessão/voz no build do jogo, o que direciona futuras análises estáticas para as chamadas XAM/XNet/XOnline relevantes.
3. Ela **não** fornece, nos arquivos públicos examinados, uma implementação de servidor online para Xbox 360, um protocolo de autenticação comunitária, endpoints retail, ou traces de rede do console.
4. Os stubs do ReXGlue não podem ser reutilizados como se fossem uma implementação online: vários retornam ausência de Live, loopback ou erro DNS.
5. O DSOS para PC/Steam continua sendo apenas uma referência de protocolo de outra plataforma; esta nova fonte não demonstra compatibilidade entre os dois protocolos.

## Limites e segurança

- Nenhuma alteração foi feita no repositório MajulaRecomp.
- Nenhum XEX, ISO ou conteúdo do jogo foi baixado ou modificado.
- Nenhuma chamada de rede foi enviada ao console.
- Nenhuma alteração de DNS, roteador, jogo ou memória foi feita.
- Nenhum XEX foi criado ou executado neste projeto.
- O protocolo Xbox 360 continua não identificado; não implementar autenticação, identidade, portas ou mensagens por suposição.

## Próxima evidência técnica necessária

A próxima etapa estática útil é identificar, a partir de uma análise autorizada do XEX exato de Scholar, quais imports XAM e rotinas XNET/XONLINE são efetivamente alcançados pelos fluxos de “Go Online”, login, matchmaking e sessão. A lista de bibliotecas por si só não revela a ordem das chamadas nem os formatos dos dados.

# Auditoria do redirecionamento do cliente DS2 no DSOS para PC

## Fonte e versão

Auditoria do upstream `TLeonardUK/ds3os`, commit fixado
`56406879a31505a71bea8c6290da370067f43659`.

Arquivos examinados:

- `Source/Injector/Hooks/DarkSouls2/DS2_ReplaceServerAddressHook.cpp`
- `Source/Injector/Hooks/Shared/ReplaceServerPortHook.cpp`
- `Source/Injector/Injector/Injector.cpp`
- `Source/Loader/Forms/MainForm.cs`

Links para o código original:

- [DS2_ReplaceServerAddressHook.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Injector/Hooks/DarkSouls2/DS2_ReplaceServerAddressHook.cpp)
- [ReplaceServerPortHook.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Injector/Hooks/Shared/ReplaceServerPortHook.cpp)
- [Injector.cpp](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Injector/Injector/Injector.cpp)
- [MainForm.cs](https://github.com/TLeonardUK/ds3os/blob/56406879a31505a71bea8c6290da370067f43659/Source/Loader/Forms/MainForm.cs)

## O que o cliente de PC realmente altera

### Endereço e chave pública

O hook específico de DS2 procura no espaço de memória do processo a string:

`frpg2-steam64-ope-login.fromsoftware-game.net`

e a substitui pelo hostname configurado no DSOS. O código também procura a chave pública RSA embutida no cliente e substitui esse conteúdo pela chave pública do servidor selecionado.

Isso é um patch de memória do processo Windows. Não é uma configuração de servidor que o jogo Xbox possa simplesmente importar.

### Porta de login

O hook compartilhado intercepta a função Winsock `connect`. Para DS2, reconhece a porta original `50031` e a troca pela porta configurada em `ServerPort`.

Esse número é uma constante do caminho de redirecionamento do cliente PC DSOS. Não é evidência de que a build Xbox 360 use essa porta.

### Inicialização e injeção

O `Injector.cpp` seleciona o módulo `DarkSoulsII.exe`, instala o hook de endereço para DS2 e instala o hook Winsock de porta. O carregador Windows inicia o executável e injeta `Injector.dll` no processo usando APIs de processo do Windows.

O carregador também valida o executável por hash e verifica se Steam está em execução e autenticado antes de habilitar o lançamento. Isso confirma que esse caminho de cliente foi construído em torno de um executável Windows/Steam.

## Consequência para o projeto Xbox 360

| Mecanismo do DSOS PC | Situação Xbox 360 |
|---|---|
| Busca e substituição de hostname em memória | Não demonstrado |
| Substituição de chave RSA em memória | Não demonstrado |
| Hook de `Winsock connect` | Não demonstrado; não presumir Winsock no console |
| Injeção de `Injector.dll` em `DarkSoulsII.exe` | Não aplicável como está ao XEX Xbox |
| Verificação de hash de executável Windows | Não identifica a build Xbox |
| Steam autenticado e ticket Steam | Não há evidência de equivalente Xbox nesse fluxo |

## O que podemos reutilizar

- O conhecimento do protocolo e a lógica do servidor DS2 podem servir como referência para uma futura implementação independente.
- Os números e formatos observados no cliente PC podem orientar perguntas de pesquisa, mas não devem ser copiados como parâmetros Xbox.
- A separação entre autenticação TCP e transporte de jogo UDP continua sendo uma descrição do caminho PC auditado, não uma conclusão sobre o console.

## O que não está provado

Esta auditoria não prova que o Xbox usa o hostname citado, porta 50031, chave RSA, Winsock, Steam ID, ticket Steam, CWC ou a mesma sequência de serviços.

Não recomenda editar DNS, roteador, memória do jogo ou arquivos do console. Não cria XEX, loader Xbox, hook XSDK nem servidor compatível.

**Conclusão:** o redirecionamento do DSOS para DS2 depende de um carregador e de hooks Windows/Steam. Reutilizar o backend DS2 não resolve automaticamente a camada de cliente Xbox. O protocolo Xbox permanece não identificado.

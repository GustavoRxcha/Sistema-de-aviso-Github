# Sistema de Avisos Centralizado - ExecFlow

## Manual de Operações para Equipe de TI/DevOps

### 1. Arquitetura de Implantação (Deployment)

#### Diagrama Técnico

O sistema utiliza uma arquitetura Cliente-Servidor simples e direta. No centro, há o **Servidor Central**, uma aplicação Python rodando em um servidor na rede interna. Esta aplicação abre e escuta a porta de rede **TCP/xxxx**, aguardando conexões.

Nos terminais de balcão de cada filial, roda uma instância do **Cliente Leve**, um script Python. Cada cliente estabelece uma conexão TCP/IP persistente diretamente com o Servidor Central através da porta xxxx.

A comunicação é unidirecional (servidor para clientes). Quando um administrador envia uma mensagem pela interface gráfica do Servidor Central, a aplicação envia o texto puro (raw text) através do socket TCP para todos os clientes conectados. Os clientes recebem o texto e geram um pop-up na tela do usuário. O sistema não utiliza APIs REST ou WebSockets, mas sim sockets TCP puros de baixo nível.

#### Componentes

* **Servidor Central**
    * **Tecnologia:** Aplicação Python.
    * **Descrição:** É o núcleo do sistema. Utiliza a biblioteca `socket` para criar um servidor TCP que gerencia múltiplas conexões simultaneamente com `threading`. Possui uma interface gráfica simples (`tkinter`) para um operador enviar avisos. A aplicação mantém uma lista em memória dos clientes conectados e armazena logs de eventos em arquivos de texto (`.log`) no diretório "Logs".
    * **Porta de Rede:** `TCP/xxxx`.

* **Cliente**
    * **Tecnologia:** Script Python.
    * **Descrição:** Um script leve que roda em segundo plano nos terminais. Sua função é estabelecer e manter uma conexão TCP persistente com o servidor. Ao receber uma mensagem, utiliza `tkinter` para gerar um pop-up "always-on-top", forçando a atenção do usuário. Possui lógica de reconexão automática.

* **Dependências Externas**
    * Não há. O sistema é totalmente autocontido e utiliza apenas bibliotecas padrão do Python.

### 2. Pré-requisitos de Servidor e Cliente

* **Servidor**
    * **Sistema Operacional:** Windows (Windows 10, Windows 11, Windows Server 2016 ou superior).
    * **Dependências:** Uma instalação padrão do Python é suficiente (`tkinter`, `socket`, `threading` são nativos).
    * **Rede:** Requer um endereço IP fixo (ou nome de host resolvível). A porta `TCP/xxxx` deve estar liberada no firewall para conexões de entrada.

* **Máquinas Cliente**
    * **Sistema Operacional:** Windows.
    * **Dependências:** Uma instalação padrão do Python é suficiente.
    * **Rede:** Deve estar na mesma rede/domínio que o servidor e ter acesso de saída para o IP do servidor na porta `TCP/2507`.

### 3. Guia de Instalação e Configuração

A implantação é feita através de dois executáveis: `central.exe` (servidor) e `cliente.exe`. Não há instalador; a operação consiste em posicionar e executar os arquivos.

#### 3.1. Servidor Central

1.  **Obtenção do Arquivo:**
    * Crie uma pasta dedicada no servidor (ex: `C:\SistemaDeAvisos-Central\`).
    * Copie o `central.exe` para esta pasta.

2.  **Configuração de Ambiente:**
    * Não há arquivos de configuração externos (`.env`, `.ini`). As configurações são "hardcoded" no código-fonte antes da compilação.
    * **Variáveis Principais:**
        * `HOST = '0.0.0.0'`: Aceita conexões de qualquer interface de rede. **Não deve ser alterado.**
        * `PORT = xxxx`: Porta de escuta do servidor. Para alterar, é preciso editar o código e gerar um novo `.exe`.

3.  **Execução:**
    * Dê um duplo clique no `central.exe`. A janela da Central de Avisos aparecerá, e o servidor iniciará em segundo plano.

#### 3.2. Cliente (Terminais das Filiais)

1.  **Obtenção do Arquivo:**
    * Em cada máquina cliente, crie uma pasta (ex: `C:\AVISO\`).
    * Copie o `Avisosloja.exe` (o `cliente.exe`) e o atalho correspondente para esta pasta.

2.  **Configuração de Ambiente:**
    * O endereço do servidor é "hardcoded".
    * **Variável Crítica:**
        * `SERVER_HOST = 'xxx.xxx.xxx.xxx'`: **Endereço IP do servidor**. Deve estar correto antes da compilação.
        * **Atenção:** Se o IP do servidor mudar, um novo `cliente.exe` deve ser compilado e redistribuído para todas as filiais.

3.  **Execução Automática na Inicialização:**
    1.  Pressione `Win + R` para abrir a caixa "Executar".
    2.  Digite `shell:startup` e pressione Enter para abrir a pasta de Inicializar.
    3.  Copie o **atalho** do `Avisosloja.exe` para dentro da pasta "Inicializar".

### 4. Monitoramento, Logs e Manutenção

#### Monitoramento

* **Serviço:** Garanta que o processo `central.exe` está em execução no servidor.
* **Clientes:** Monitore o contador de "Clientes conectados" na interface da Central. Quedas súbitas podem indicar problemas de rede.
* **Erros:** Verifique periodicamente o `erros.log` para identificar falhas de comunicação.

#### Logs

Os logs são armazenados na pasta `Logs`, no mesmo diretório do `central.exe`. O formato é `DD-MM-AAAA HH:MM:SS - Mensagem do evento`.                        

#### Manutenção

* **Gestão de Logs:** Arquive ou remova logs antigos periodicamente para gerenciar espaço em disco.
* **Atualização:** Substitua os arquivos `.exe` pelas novas versões. Lembre-se que mudanças de configuração exigem a recompilação e redistribuição dos executáveis.

### 5. Solução de Problemas

* **Problema:** O cliente em uma filial não se conecta ao servidor.
    * **Causa Provável/Solução:**
        1.  Verificar o firewall no servidor e no cliente.
        2.  Confirmar que há rota de rede entre o cliente e o servidor.
        3.  Garantir que o IP do servidor está correto no `cliente.exe`.

* **Problema:** Avisos não são enviados para nenhum cliente.
    * **Causa Provável/Solução:**
        1.  Verificar os logs no servidor em busca de falhas.
        2.  Confirmar que o processo `central.exe` está rodando e não travou.
        3.  Checar a conectividade de rede do próprio servidor.


# BigFS - Sistema de Arquivos Remoto via XML-RPC

BigFS é um sistema cliente-servidor desenvolvido em Python que permite a manipulação remota de arquivos usando o protocolo XML-RPC. O servidor exporta um diretório local e os clientes podem realizar operações como upload, download, listagem e exclusão de arquivos.

## 📁 Estrutura do Projeto

```
BigFS/
├── client.py           # Cliente interativo
├── server.py           # Servidor XML-RPC com suporte a múltiplos clientes
├── README.md           # Instruções de uso e descrição
```

## 📁 Funcionalidades

- 📂 Listar arquivos em diretórios remotos
- ⬆️ Upload de arquivos do cliente para o servidor
- ⬇️ Download de arquivos do servidor para o cliente
- ❌ Exclusão de arquivos remotos
- 🧵 Suporte a múltiplos clientes simultâneos (concorrência)

## ⚙️ Tecnologias Utilizadas

- Python 3.8
- XML-RPC (via `xmlrpc.client` e `xmlrpc.server`)
- Threading (para concorrência no servidor)

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8+ instalado
- Sistema operacional Windows (de preferência)

### 1. Clone o repositório

```bash
git clone https://github.com/lucasvitorrt/BigFSv2.git
cd BigFS
```

### 2. Execute o Servidor

```bash
python server.py
```

O servidor será iniciado na porta `9000` e utilizará o diretório `C:\BigFS\arquivos` para armazenar os arquivos.

### 3. Execute o Cliente

Em outro terminal, execute:

```bash
python client.py
```

Você verá um terminal interativo com os comandos disponíveis.


## ℹ️ Comandos Disponíveis

- `ls remoto:/pasta` — Lista arquivos da pasta remota.
- `copy "origem" "remoto:/destino"` — Upload para o servidor.
- `copy "remoto:/origem/arquivo" "destino"` — Download do servidor.
- `delete "remoto:/caminho/arquivo"` — Deleta arquivo remoto.
- `ajuda` — Exibe ajuda.
- `limpar` — Limpa o terminal.
- `sair` — Encerra o cliente.

## 📸 Exemplos de Uso (Logs)

```
BigFS> ls remoto:/
Arquivos remotos:
 - documentos
 - imagem.jpg

BigFS> copy "C:\Users\User\Downloads\imagem.jpg" "remoto:/imagens/"
Arquivo enviado com sucesso

BigFS> copy "remoto:/imagens/imagem.jpg" "C:\Users\User\Desktop"
Arquivo baixado com sucesso

BigFS> delete "remoto:/imagens/imagem.jpg"
Arquivo deletado com sucesso
```

## ⚠️ Limitações

- Caminho de diretório fixo no servidor (C:\BigFS)
- Sem autenticação ou criptografia
- Comunicação não segura (HTTP)

## 💡 Melhorias Futuras

- Suporte a HTTPS e autenticação
- Interface gráfica para o cliente
- Logs persistentes em arquivo

---

Desenvolvido por Lucas Vitor – Projeto educacional de sistema distribuído com XML-RPC.

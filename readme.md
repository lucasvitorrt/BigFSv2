
# BigFS - Sistema de Arquivos Distribuído Remoto via XML-RPC

BigFS é uma aplicação cliente-servidor desenvolvida em Python, que permite o compartilhamento de arquivos entre cliente e servidor via rede local, utilizando o protocolo XML-RPC. O servidor exporta um diretório local e os clientes podem realizar operações como upload, download, listagem e exclusão de arquivos.

## 📁 Estrutura do Projeto

```
bigfs/
├── client.py         # Cliente em linha de comando
├── server.py         # Servidor XML-RPC com suporte a múltiplos clientes
└── README.md         # Este arquivo
```

## ✅ Funcionalidades

- Enviar arquivos do cliente para o servidor (`upload`)
- Baixar arquivos do servidor para o cliente (`download`)
- Listar arquivos em uma pasta remota (`ls`)
- Deletar arquivos no servidor (`delete`)
- Sincronização de acesso concorrente (via locks)
- Barra de progresso para transferências com `tqdm`

## ⚙️ Requisitos

- Python 3.8 ou superior
- Biblioteca externa:
  - `tqdm` (para barra de progresso)

### Instalação das dependências

```bash
pip install tqdm
```

## ▶️ Execução

### 1. Iniciar o servidor

```bash
python server.py
```

O servidor escutará na porta `9000` e exportará a pasta `C:\BigFS\arquivos`.

### 2. Iniciar o cliente

```bash
python client.py
```

Você verá o prompt de comandos do BigFS.

## 💡 Comandos disponíveis (cliente)

| Comando                                 | Descrição                                    |
|----------------------------------------|----------------------------------------------|
| `ls remoto:/pasta`                     | Lista arquivos da pasta remota               |
| `copy "origem" "remoto:/destino"`      | Envia arquivo local para o servidor          |
| `copy "remoto:/origem" "destino"`      | Baixa arquivo do servidor para o cliente     |
| `delete "remoto:/arquivo"`             | Remove um arquivo do servidor                |
| `ajuda`                                | Exibe ajuda com comandos                     |
| `limpar`                               | Limpa a tela                                 |
| `sair`                                 | Encerra o cliente                            |

### Exemplos:

```bash
# Listar arquivos remotos
BigFS> ls remoto:/arquivos
Arquivos remotos:
 - documentos
 - imagem.jpg

# Enviar um arquivo local
BigFS> copy "C:\Users\User\Downloads\imagem.jpg" "remoto:/arquivos/"

# Baixar um arquivo remoto
BigFS> copy "remoto:/arquivos/foto.jpg" "C:\Users\User\Downloads"

# Deletar um arquivo remoto
BigFS> delete "remoto:/arquivos/antigo.txt"
```

## 📌 Observações

- Caminhos remotos devem começar com `remoto:/`
- Use aspas duplas em caminhos
- Pastas locais de destino devem existir antes da cópia

## 🔒 Limitações

- Sem autenticação de usuários
- Sem criptografia (usa HTTP puro)
- Não suporta retomada de transferências interrompidas

## 🚀 Melhorias a implementar

- Adicionar autenticação com senha/token
- Logs persistentes

---

Desenvolvido por Lucas Vitor – Projeto educacional de sistema distribuído com XML-RPC.

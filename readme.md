# BigFS - Sistema Cliente-Servidor com XML-RPC

BigFS é uma aplicação cliente-servidor escrita em Python, que permite o gerenciamento remoto de arquivos através do protocolo XML-RPC. Com ela, é possível listar, enviar, baixar e excluir arquivos de um diretório exportado pelo servidor.

---

## 📁 Estrutura do Projeto

```
BigFS/
├── client.py           # Cliente interativo
├── server.py           # Servidor XML-RPC com suporte a múltiplos clientes
├── README.md           # Instruções de uso e descrição
```

---

## ⚙️ Requisitos

* Python 3.8+
* Sistemas operacionais suportados: Windows, Linux, MacOS

---

## 🚀 Execução do Projeto

### 1. Clone ou copie os arquivos do projeto

```
mkdir BigFS && cd BigFS
# Copie os arquivos client.py e server.py para esta pasta
```

### 2. Execute o servidor

No terminal (cmd/powershell/shell):

```
python server.py
```

🟢 Isso iniciará o servidor ouvindo na porta `9000`, exportando o diretório `C:\BigFS"\arquivos` (criado automaticamente, se não existir).

### 3. Execute o cliente

Em outro terminal:

```
python client.py
```

Você verá o prompt de comandos interativo do BigFS:

```
Cliente BigFS conectado ao servidor. PASTA EXPORTADA: BigFS
============================================================
BigFS>
```

---

## 🧪 Comandos Suportados

| Comando                          | Descrição                            |
| -------------------------------- | ------------------------------------ |
| `ls remoto:/pasta`               | Lista arquivos no servidor           |
| `copy <origem> remoto:<destino>` | Envia arquivo local para o servidor  |
| `copy remoto:<origem> <destino>` | Baixa arquivo do servidor para local |
| `delete remoto:/arquivo`         | Remove arquivo remoto                |
| `ajuda`                          | Exibe ajuda                          |
| `clear`                          | Limpa terminal                       |
| `sair`                           | Encerra o cliente                    |


---

## 🔐 Segurança

* O servidor exporta apenas a pasta `C:\BigFS"\arquivos` (Windows). Ajuste em `server.py` se necessário.
* O XML-RPC **não possui criptografia**, portanto recomenda-se rodar em redes seguras.

---

## 🧹 Limitações e Melhorias Futuras

### Limitações:

* Sem autenticação.
* Sem suporte a subpastas recursivas.

### Melhorias Sugeridas:

* Suporte a autenticação e permissões.
* Interface gráfica (GUI ou Web).
* Log de auditoria das operações realizadas.

---

## 📸 Exemplos de Uso (Logs)

```
BigFS> ls remoto:/
Arquivos remotos:
 - documentos
 - imagem.jpg

BigFS> copy C:\Users\User\Downloads\foto.png remoto:/imagens/
Arquivo enviado com sucesso

BigFS> copy remoto:/imagens/foto.png C:\Users\User\Desktop\foto_copia.png
Arquivo baixado com sucesso

BigFS> delete remoto:/imagens/foto.png
Arquivo deletado com sucesso
```

---

## 📄 Licença

Este projeto é livre para fins acadêmicos.

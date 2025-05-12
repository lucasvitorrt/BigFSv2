import xmlrpc.client
import os
import ntpath  # Usado para manipulação de caminhos
import shlex

# Criação do proxy para comunicação com o servidor XML-RPC
proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:9000/RPC2", allow_none=True)

# Função de ajuda para exibir comandos disponíveis
def ajuda():
    print("Comandos disponíveis:")
    print(" - ls remoto:/<pasta>".ljust(60) + "# Lista arquivos de uma pasta remota")
    print(" - copy <origem> remoto:<destino>".ljust(60) + "# Copia arquivos do cliente para servidor")
    print(" - copy remoto:<origem> <destino>".ljust(60) + "# Copia arquivos do servidor para cliente")
    print(" - delete remoto:/<arquivo>".ljust(60) + "# Deleta um arquivo remoto")
    print(" - sair".ljust(60) + "# Encerra a sessão")
    print(" - ajuda".ljust(60) + "# Mostra Ajuda")
    print(" - clear".ljust(60) + "# Limpar Terminal")
    print("\nExemplos de uso:")
    print(" ls remoto:".ljust(60) + "# Lista diretorios de uma pasta remota")
    print(" ls remoto:/arquivos/")
    print(" copy C:\\Users\\home\\Downloads\\foto.jpg remoto:/arquivos/".ljust(60) + "# Copia arquivos do cliente para servidor")
    print(" copy remoto:/arquivos/foto.jpg C:\\Users\\home\\Downloads/".ljust(60) + "# Copia arquivos do servidor para cliente")
    print(" delete remoto:/arquivos/foto.jpg")
    print(" sair")
    print("=" * 60)

# Função para limpar terminal dependendo do sistema operacional
def limpar_terminal():
    sistema = os.name  # Detecta o sistema operacional
    if sistema == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac
        os.system('clear')

# Verifica se o caminho é remoto
def is_remote(path):
    return path.startswith("remoto:")

# Remove o prefixo 'remoto:' e retorna o caminho real
def convert_remote(path):
    return path.replace("remoto:", "").lstrip("/\\")

# Comando para listar arquivos em um diretório remoto
def comando_ls(path):
    remote_path = convert_remote(path)
    resp = proxy.ls(remote_path)
    if resp["status"] == "OK":
        print("Arquivos remotos:")
        for f in resp["files"]:
            print(" -", f)
    else:
        print("Erro:", resp["message"])

# Comando para copiar arquivos entre cliente e servidor
# Detecta se é upload (cliente -> servidor) ou download (servidor -> cliente)
def comando_copy(origem, destino):
    if is_remote(origem) and not is_remote(destino):
        # Download do servidor para cliente
        remote_path = convert_remote(origem)
        if destino.endswith(("\\", "/")):
            destino = os.path.join(destino, os.path.basename(remote_path))
        resp = proxy.download_file(remote_path)
        if isinstance(resp, dict) and "ERROR" in resp.get("status", ""):
            print("Erro:", resp["message"])
        else:
            with open(destino, "wb") as f:
                f.write(resp.data)
            print("Arquivo baixado com sucesso.")
    elif not is_remote(origem) and is_remote(destino):
        # Upload do cliente para servidor
        remote_path = convert_remote(destino)
        if remote_path.endswith(("\\", "/")):
            remote_path = os.path.join(remote_path, ntpath.basename(origem))
        try:
            with open(origem, "rb") as f:
                data = f.read()
            resp = proxy.upload_file(remote_path, xmlrpc.client.Binary(data))
            if resp["status"] == "OK":
                print(resp["message"])
            else:
                print("Erro:", resp["message"])
        except Exception as e:
            print("Erro ao ler arquivo local:", str(e))
    else:
        print("Operação copy inválida (origem ou destino precisa ser remoto)")

# Comando para deletar arquivos no servidor

def comando_delete(path):
    if not is_remote(path):
        print("delete só pode ser feito em arquivos remotos")
        return
    remote_path = convert_remote(path)
    resp = proxy.delete(remote_path)
    print(resp["message"] if resp["status"] == "OK" else "Erro: " + resp["message"])

# Interface de linha de comando interativa
if __name__ == "__main__":
    print("Cliente BigFS conectado ao servidor. PASTA EXPORTADA: BigFS/arquivos")
    print("=" * 60)
    ajuda()

    while True:
        try:
            entrada = input("\nBigFS> ").strip()
            if not entrada:
                continue
            if entrada == "sair":
                print("Encerrando cliente...")
                break

            #partes = entrada.split()
            partes = entrada.split()
            comando = partes[0]

            if comando == "ls" and len(partes) == 2:
                comando_ls(partes[1])
            elif comando == "copy" and len(partes) == 3:
                comando_copy(partes[1], partes[2])
            elif comando == "delete" and len(partes) == 2:
                comando_delete(partes[1])
            elif comando == "ajuda":
                ajuda()
            elif comando == "clear":
                limpar_terminal()
            else:
                print("Comando inválido ou argumentos incorretos.")
        except KeyboardInterrupt:
            print("\nEncerrando cliente...")
            break
        except Exception as e:
            print("Erro inesperado:", str(e))
            
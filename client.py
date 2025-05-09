# cliente_bigfs.py
import xmlrpc.client
from xmlrpc.client import ServerProxy
from xmlrpc.client import Binary
import os
import sys
import ntpath  # já incluso no Python

proxy = xmlrpc.client.ServerProxy("http://192.168.10.11:9000/RPC2", allow_none=True)

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
    print(" copy C:\\Users\\home\\Downloads\\foto.jpg remoto:/rquivos/".ljust(60) + "# Copia arquivos do cliente para servidor")
    print(" copy remoto:/arquivos/foto.jpg C:\\Users\\home\\Downloads\\".ljust(60) + "# Copia arquivos do servidor para cliente")
    print(" delete remoto:/arquivos/foto.jpg")
    print(" sair")
    print("=" * 60)

def limpar_terminal():
    sistema = os.name  # Detecta o sistema operacional
    if sistema == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac
        os.system('clear')

def is_remote(path):
    return path.startswith("remoto:")

def convert_remote(path):
    return path.replace("remoto:", "").lstrip("/\\")

def comando_ls(path):
    remote_path = convert_remote(path)
    resp = proxy.ls(remote_path)
    if resp["status"] == "OK":
        print("Arquivos remotos:")
        for f in resp["files"]:
            print(" -", f)
    else:
        print("Erro:", resp["message"])


def comando_copy(origem, destino):
    if is_remote(origem) and not is_remote(destino):
        # Download
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
        # Upload
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


def comando_delete(path):
    if not is_remote(path):
        print("delete só pode ser feito em arquivos remotos")
        return
    remote_path = convert_remote(path)
    resp = proxy.delete(remote_path)
    print(resp["message"] if resp["status"] == "OK" else "Erro: " + resp["message"])

# Interface de linha de comando interativa
if __name__ == "__main__":
    print("Cliente BigFS conectado ao servidor. PASTA EXPORTADA: BigFS")
    print("=" * 60)
    ajuda()
   
    
    while True:
        try:
            entrada = input("\nBigFS> ").strip()
            if not entrada:
                continue
            if entrada.lower() == "sair":
                print("Encerrando cliente...")
                break

            partes = entrada.split()
            comando = partes[0]

            if comando.lower() == "ls" and len(partes) == 2:
                comando_ls(partes[1])
            elif comando.lower() == "copy" and len(partes) == 3:
                comando_copy(partes[1], partes[2])
            elif comando.lower() == "delete" and len(partes) == 2:
                comando_delete(partes[1])
            elif comando.lower() == "ajuda":
                ajuda()
            elif comando.lower() == "clear":
                limpar_terminal()
            else:
                print("Comando inválido ou argumentos incorretos.")
        except KeyboardInterrupt:
            print("\nEncerrando cliente...")
            break
        except Exception as e:
            print("Erro inesperado:", str(e))

'''BigFS> ls remoto:/meus_arquivos
BigFS> copy C:\video.mp4 remoto:/videos/video.mp4
BigFS> delete remoto:/videos/video.mp4
BigFS> sair'''
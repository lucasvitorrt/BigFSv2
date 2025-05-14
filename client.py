import xmlrpc.client # Biblioteca que permite comunicação XML-RPC com o servidor
import os
import ntpath # Usado para manipulação de caminhos
import shlex
import time
from tqdm import tqdm # Biblioteca para exibir barra de progresso

# Configuração da Conexão
url = "http://127.0.0.1:9000/RPC2"
proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
CHUNK_SIZE = 1024 * 1024  # Tamanho dos blocos de dados (1MB)

# Exibe os comandos disponíveis e exemplos de uso.
def ajuda():
    print("=" * 60)
    print("BigFS - Comandos disponíveis")
    print("=" * 60)
    
    comandos = [
        ("ls remoto:/pasta", "Lista arquivos da pasta remota"),
        ("copy \"origem\" \"remoto:/destino\"", "Envia arquivo do cliente para o servidor"),
        ("copy \"remoto:/origem\" \"destino\"", "Baixa arquivo do servidor para o cliente"),
        ("delete \"remoto:/arquivo\"", "Remove um arquivo do servidor"),
        ("limpar", "Limpa a tela"),
        ("ajuda", "Exibe esta ajuda"),
        ("sair", "Encerra o cliente")
    ]

    for cmd, desc in comandos:
        print(f"  {cmd.ljust(40)} # {desc}")

    print("\nExemplos de uso:")
    exemplos = [
        "ls remoto:/arquivos/",
        "copy \"C:\\Users\\home\\Downloads\\meu arquivo.txt\" \"remoto:/arquivos/\"",
        "copy \"remoto:/arquivos/meu arquivo.txt\" \"C:\\Users\\home\\Downloads\"",
        "delete \"remoto:/arquivos/meu arquivo.xlsx\""
    ]
    for exemplo in exemplos:
        print(f"  {exemplo}")

    print("\nDICAS:")
    print("  - Use aspas duplas nos cmainhos dos arquivos")
    print("  - Verifique se as pastas de destino existem antes de copiar.")
    print("  - Caminhos remotos devem sempre começar com: remoto:/")
    print("=" * 60)

# Limpa a tela
def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Verifica se o caminho é remoto (começa com "remoto:")
def is_remote(path):
    return path.startswith("remoto:")

# Remove "remoto:" do caminho e ajusta barras
def convert_remote(path):
    return path.replace("remoto:", "").lstrip("/\\")

# Lista os arquivos de uma pasta no servidor.
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
    # Se origem é remota → download do servidor.
    if is_remote(origem) and not is_remote(destino):
        # Download: servidor -> cliente
        remote_path = convert_remote(origem)
        if os.path.isdir(destino):
            destino = os.path.join(destino, os.path.basename(remote_path))
        size_info = proxy.get_file_size(remote_path) # Solicita tamanho do arquivo.
        if size_info["status"] != "OK":
            print("Erro ao obter tamanho do arquivo:", size_info["message"])
            return
        total_size = size_info["size"]
        start = time.time()
        # Baixa em pedaços e escreve localmente com barra de progresso.
        with open(destino, "wb") as f, tqdm(total=total_size, unit="B", unit_scale=True, desc="Download") as pbar:
            for offset in range(0, total_size, CHUNK_SIZE):
                chunk = proxy.download_chunk(remote_path, offset, CHUNK_SIZE)
                f.write(chunk.data)
                pbar.update(len(chunk.data))
        end = time.time()
        tempo = end - start
        print(f"\nArquivo baixado com sucesso. Tempo: {tempo:.2f}s")

    elif not is_remote(origem) and is_remote(destino):
        # Upload: cliente -> servidor
        if not os.path.exists(origem): # Verifica se o arquivo existe.
            print("Arquivo local não encontrado:", origem)
            return
        remote_path = convert_remote(destino)
        if remote_path.endswith(("\\", "/")):
            remote_path = os.path.join(remote_path, ntpath.basename(origem))
        resp = proxy.upload_init(remote_path) # Inicia o upload no servidor.
        if resp["status"] != "OK":
            print("Erro ao iniciar upload:", resp["message"])
            return
        file_size = os.path.getsize(origem)
        start = time.time()
        # Envia o arquivo em blocos com barra de progresso.
        with open(origem, "rb") as f, tqdm(total=file_size, unit="B", unit_scale=True, desc="Upload") as pbar:
            offset = 0
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                r = proxy.upload_chunk(remote_path, offset, xmlrpc.client.Binary(data))
                if r["status"] != "OK":
                    print("Erro ao enviar chunk:", r["message"])
                    return
                offset += len(data)
                pbar.update(len(data))
        end = time.time()
        tempo = end - start
        print(f"Arquivo enviado com sucesso. Tempo: {tempo:.2f}s")
    
    else:
        print("Operação copy inválida (origem ou destino precisa ser remoto)")

# Comando para deletar arquivos no servidor
def comando_delete(path):
    if not is_remote(path):
        print("delete só pode ser feito em arquivos remotos")
        return
    confirm = input(f"Tem certeza que deseja deletar '{path}'? (s/n): ") # Confirma com o usuário antes de deletar.
    if confirm.lower() != 's':
        print("Operação cancelada.")
        return
    remote_path = convert_remote(path)
    resp = proxy.delete(remote_path)
    print(resp["message"] if resp["status"] == "OK" else "Erro: " + resp["message"])

# Interface de linha de comando interativa
if __name__ == "__main__":
    print("Cliente BigFS conectado ao servidor. PASTA EXPORTADA: BigFS/arquivos")
    print("=" * 60)
    print("Se precisar digite: ajuda")

    while True:
        try:
            entrada = input("\nBigFS> ").strip()
            if not entrada:
                continue
            if entrada == "sair":
                print("Encerrando cliente...")
                break

            partes = shlex.split(entrada) # Usa para separar os argumentos.
            comando = partes[0].lower()

            if comando == "ls" and len(partes) == 2:
                comando_ls(partes[1])
            elif comando == "copy" and len(partes) == 3:
                comando_copy(partes[1], partes[2])
            elif comando == "delete" and len(partes) == 2:
                comando_delete(partes[1])
            elif comando == "ajuda":
                ajuda()
            elif comando == "limpar":
                limpar_terminal()
            else:
                print("Comando inválido ou argumentos incorretos.")
        except KeyboardInterrupt:
            print("\nEncerrando cliente...")
            break
        except Exception as e:
            print("Erro inesperado:", str(e))

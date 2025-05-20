from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler # Suporte XML-RPC.
from socketserver import ThreadingMixIn #  permite múltiplos clientes simultaneamente.
import xmlrpc.client
import os
import threading # controle de concorrência.
import hashlib


# Diretório exportado para armazenar os arquivos manipulados
EXPORT_DIR = "C:\\BigFS" # Define diretório onde os arquivos serão salvos.
EXPORT_DIR_ARQ = os.path.join(EXPORT_DIR, "arquivos")
CHUNK_SIZE = 1024 * 1024  # 1 MB

file_locks = {} # Cria dicionário de travas por arquivo.

# classe para manipular as requisições, Define o caminho de acesso RPC.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Garante que o caminho não acesse pastas fora do diretório exportado.
def safe_path(path):
    full_path = os.path.normpath(os.path.join(EXPORT_DIR, path.lstrip('/\\')))
    if not full_path.startswith(EXPORT_DIR):
        raise ValueError("Caminho inseguro detectado.")
    return full_path

# Cria e retorna um lock exclusivo para o arquivo.
def get_lock(path):
    full_path = safe_path(path)
    if full_path not in file_locks:
        file_locks[full_path] = threading.Lock()
    return file_locks[full_path]

# Listar arquivos
def list_files(path):
    try:
        full_path = safe_path(path)
        files = os.listdir(full_path)
        return {"status": "OK", "files": files}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Iniciar upload
def upload_init(path):
    try:
        full_path = safe_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        lock = get_lock(path)
        with lock:
            with open(full_path, "wb") as f:
                pass
        return {"status": "OK"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# upload de um chunk (Bloco)
def upload_chunk(path, offset, data):
    try:
        offset = int(offset) 
        full_path = safe_path(path)
        lock = get_lock(path)
        with lock:
            with open(full_path, "r+b") as f:
                f.seek(offset)
                f.write(data.data)
        return {"status": "OK"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Obter tamanho do arquivo
def get_file_size(path):
    try:
        full_path = safe_path(path)
        return {"status": "OK", "size": os.path.getsize(full_path)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# baixar um chunk (Bloco)
def download_chunk(path, offset, size):
    try:
        offset = int(offset)
        full_path = safe_path(path)
        lock = get_lock(path)
        with lock:
            with open(full_path, "rb") as f:
                f.seek(offset)
                data = f.read(size)
        return xmlrpc.client.Binary(data)
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# deleter um arquivo
def delete_file(path):
    try:
        full_path = safe_path(path)
        lock = get_lock(path)
        with lock:
            os.remove(full_path)
        print(f"[LOG] DELETE: {full_path}")
        return {"status": "OK", "message": "Arquivo deletado com sucesso"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Classe com suporte a múltiplas conexões
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def get_checksum(path):
    try:
        full_path = safe_path(path)
        h = hashlib.sha256()
        with open(full_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
        return {"status": "OK", "checksum": h.hexdigest()}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


# Inicialização do servidor
if __name__ == "__main__":
    # Cria pastas se não existirem.
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR_ARQ, exist_ok=True)
    
    with ThreadedXMLRPCServer(("127.0.0.1", 9000), allow_none=True, requestHandler=RequestHandler) as server:
        # Registra as funções disponíveis.
        server.register_function(get_checksum, 'checksum')
        server.register_function(list_files, 'ls')
        server.register_function(upload_init, 'upload_init')
        server.register_function(upload_chunk, 'upload_chunk')
        server.register_function(get_file_size, 'get_file_size')
        server.register_function(download_chunk, 'download_chunk')
        server.register_function(delete_file, 'delete')
        print(f"BigFS rodando com concorrência no diretório: {EXPORT_DIR}")
        # Inicia o servidor que escuta indefinidamente.
        server.serve_forever()

# ================================
# Servidor BigFS - Sistema Cliente-Servidor XML-RPC
# Autor: Lucas Vitor
# Descrição: Servidor que gerencia arquivos para clientes via XML-RPC
# ================================

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xmlrpc.client
import os

# Diretório exportado para armazenar os arquivos manipulados
EXPORT_DIR= "C:\\BigFS"
EXPORT_DIR_ARQ= "C:\\BigFS\\arquivos"

# Classe de requisições seguras - define o caminho RPC
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Função para listar arquivos em um diretório dentro do EXPORT_DIR
def list_files(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        files = os.listdir(full_path)
        return {"status": "OK", "files": files}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Função para receber e salvar arquivos enviados pelo cliente
def upload_file(path, data):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data.data)  # data é um objeto Binary
        return {"status": "OK", "message": "Arquivo enviado com sucesso"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Função para enviar arquivos ao cliente
def download_file(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        with open(full_path, "rb") as f:
            return xmlrpc.client.Binary(f.read())
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Função para deletar arquivos do diretório exportado
def delete_file(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        os.remove(full_path)
        return {"status": "OK", "message": "Arquivo deletado com sucesso"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Classe de servidor com suporte a múltiplos clientes concorrentes
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# Inicialização do servidor
if __name__ == "__main__":
    os.makedirs(EXPORT_DIR, exist_ok=True)  # Garante que o diretório exista
    os.makedirs(EXPORT_DIR_ARQ, exist_ok=True) 
    with ThreadedXMLRPCServer(("127.0.0.1", 9000), allow_none=True, requestHandler=RequestHandler) as server:
        # Registro das funções disponíveis remotamente
        server.register_function(list_files, 'ls')
        server.register_function(upload_file, 'upload_file')
        server.register_function(download_file, 'download_file')
        server.register_function(delete_file, 'delete')

        print(f"BigFS rodando com concorrência no diretório: {EXPORT_DIR}")
        server.serve_forever()

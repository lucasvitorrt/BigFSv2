# servidor_bigfs.py
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xmlrpc.client
import os


# Classe de requisições seguras
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

#with SimpleXMLRPCServer(("0.0.0.0", 9000), allow_none=True) as server:

# Diretório exportado
EXPORT_DIR = "C:\\BigFS"

def list_files(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        files = os.listdir(full_path)
        return {"status": "OK", "files": files}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def upload_file(path, data):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data.data)
        return {"status": "OK", "message": "Arquivo enviado com sucesso"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def download_file(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        with open(full_path, "rb") as f:
            return xmlrpc.client.Binary(f.read())
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def delete_file(path):
    full_path = os.path.join(EXPORT_DIR, path.lstrip('/\\'))
    try:
        os.remove(full_path)
        return {"status": "OK", "message": "Arquivo deletado com sucesso"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Classe do servidor com suporte a múltiplos clientes
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

if __name__ == "__main__":
    with ThreadedXMLRPCServer(("192.168.10.11", 9000), allow_none=True) as server:
        server.register_function(list_files, 'ls')
        server.register_function(upload_file, 'upload_file')
        server.register_function(download_file, 'download_file')
        server.register_function(delete_file, 'delete')
        print(f"BigFS rodando com concorrência no diretório: {EXPORT_DIR}")
        server.serve_forever()
import threading
from client import comando_copy
import os
import hashlib
import time

NUM_UPLOADS = 1000
FILE_SIZE_KB = 256
THREADS = 10
LOCAL_DIR = "C:\\Users\\Public\\testes\\upload_files"
REMOTE_DIR = "remoto:/arquivos/"
UPLOAD_LOG = []

# Geração de arquivos
def gerar_arquivos_upload():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    for i in range(NUM_UPLOADS):
        path = os.path.join(LOCAL_DIR, f"up_{i}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(FILE_SIZE_KB * 1024))

# Função de thread para upload
def upload_worker(arquivos):
    for path in arquivos:
        nome = os.path.basename(path)
        remoto = REMOTE_DIR + nome
        comando_copy(path, remoto)
        UPLOAD_LOG.append((nome, sha256sum(path)))

# Hash SHA256
def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def executar_upload_concorrente():
    files = [os.path.join(LOCAL_DIR, f"up_{i}.bin") for i in range(NUM_UPLOADS)]
    blocos = [files[i::THREADS] for i in range(THREADS)]

    threads = []
    start = time.time()
    for bloco in blocos:
        t = threading.Thread(target=upload_worker, args=(bloco,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    end = time.time()

    print(f"✅ Upload concorrente concluído. Tempo total: {end - start:.2f}s")

#download concorrente 500 arquivos 10 threads

DOWNLOAD_DIR = "C:\\Users\\Public\\testes\\download_concorrente"
NUM_DOWNLOADS = 500

def download_worker(nomes):
    for nome in nomes:
        remoto = REMOTE_DIR + nome
        destino = os.path.join(DOWNLOAD_DIR, nome)
        comando_copy(remoto, destino)

def executar_download_concorrente():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    nomes = [f"up_{i}.bin" for i in range(NUM_DOWNLOADS)]
    blocos = [nomes[i::THREADS] for i in range(THREADS)]

    threads = []
    start = time.time()
    for bloco in blocos:
        t = threading.Thread(target=download_worker, args=(bloco,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    end = time.time()
    print(f"📥 Download concorrente concluído. Tempo total: {end - start:.2f}s")

def validar_integridade():
    erros = 0
    for nome, hash_original in UPLOAD_LOG[:NUM_DOWNLOADS]:
        local_path = os.path.join(DOWNLOAD_DIR, nome)
        if not os.path.exists(local_path):
            print(f"❌ Arquivo não encontrado: {nome}")
            erros += 1
            continue
        hash_atual = sha256sum(local_path)
        if hash_original != hash_atual:
            print(f"❌ Hash diferente: {nome}")
            erros += 1
    print(f"🧾 Validação concluída: {NUM_DOWNLOADS - erros} OK / {erros} falhas.")


if __name__ == "__main__":
    gerar_arquivos_upload()
    executar_upload_concorrente()
    executar_download_concorrente()
    validar_integridade()

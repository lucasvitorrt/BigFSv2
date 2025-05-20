import os
import time
import hashlib
from tqdm import tqdm
import client  # Importa seu client.py diretamente

# === Configurações ===
ARQUIVO_LOCAL = "C:\\Users\\Public\\arquivo_teste_5gb"
CAMINHO_REMOTO = "remoto:/arquivos/arquivo_teste_5gb.iso"
CHUNK_SIZE = 1024 * 1024  # 1 MB

# === Gerar arquivo de 5 GB se não existir ===
def gerar_arquivo_teste():
    if os.path.exists(ARQUIVO_LOCAL):
        print("[INFO] Arquivo de teste já existe.")
        return
    print("[INFO] Gerando arquivo de teste de 5 GB...")
    with open(ARQUIVO_LOCAL, "wb") as f:
        f.seek((5 * 1024 * 1024 * 1024) - 1)
        f.write(b"\0")
    print("[OK] Arquivo gerado.")

# === Calcular hash SHA-256 local ===
def sha256_local(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

# === Solicitar checksum remoto ao servidor ===
def obter_checksum_remoto():
    resp = client.proxy.checksum("arquivos/arquivo_teste_5gb.iso")
    if resp["status"] != "OK":
        print("[ERRO] Falha ao obter checksum remoto:", resp["message"])
        return None
    return resp["checksum"]

# === Principal ===
def main():
    gerar_arquivo_teste()

    print("[INFO] Iniciando upload usando client.py...")
    start = time.time()
    client.comando_copy(ARQUIVO_LOCAL, CAMINHO_REMOTO)
    end = time.time()
    tempo = end - start

    tamanho = os.path.getsize(ARQUIVO_LOCAL)
    throughput = tamanho / tempo / (1024 * 1024)  # MB/s
    print(f"[INFO] Tempo total: {tempo:.2f} segundos")
    print(f"[INFO] Throughput médio: {throughput:.2f} MB/s")

    print("[INFO] Calculando SHA-256 local...")
    checksum_local = sha256_local(ARQUIVO_LOCAL)
    print(f"[INFO] SHA-256 local: {checksum_local}")

    print("[INFO] Obtendo SHA-256 do servidor...")
    checksum_remoto = obter_checksum_remoto()
    if not checksum_remoto:
        print("[FALHA] Não foi possível obter checksum remoto.")
        return
    print(f"[INFO] SHA-256 remoto: {checksum_remoto}")

    if checksum_local == checksum_remoto:
        print("[SUCESSO] Arquivo íntegro! Checksums coincidem.")
    else:
        print("[FALHA] Checksums divergentes. Arquivo corrompido.")

if __name__ == "__main__":
    main()

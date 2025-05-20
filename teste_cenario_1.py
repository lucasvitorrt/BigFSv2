import os
import hashlib
import subprocess
import time
import csv
from datetime import datetime
from client import comando_copy, convert_remote  # Importa funções do client.py

# Configurações
NUM_FILES = 100
FILE_SIZE_KB = 512
LOCAL_DIR = "C:\\Users\\Public\\testes\\test_files"
REMOTE_DIR = "remoto:/arquivos/"
REMOTE_BASE = convert_remote(REMOTE_DIR)
DOWNLOAD_SUFFIX = "_verif"
proxy_url = "http://127.0.0.1:9000/RPC2"

# Função para criar arquivos de teste
def generate_files():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    for i in range(NUM_FILES):
        path = os.path.join(LOCAL_DIR, f"file_{i}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(FILE_SIZE_KB * 1024))

# Função para calcular hash SHA256
def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

# Função principal de teste
def transfer_and_verify():
    total_time = 0.0
    success_count = 0
    all_upload_times = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"relatorio_transferencia_{timestamp}.csv"

    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Arquivo", "Tempo de Upload (s)", "Verificação", "Hash Local", "Hash Remoto"])

        for i in range(NUM_FILES):
            local_file = os.path.join(LOCAL_DIR, f"file_{i}.bin")
            remote_file = REMOTE_DIR + f"file_{i}.bin"
            downloaded_file = os.path.join(LOCAL_DIR, f"file_{i}{DOWNLOAD_SUFFIX}.bin")

            hash_before = sha256sum(local_file)

            print(f"[{i+1}/{NUM_FILES}] Upload: {local_file}")
            start = time.time()
            comando_copy(local_file, remote_file)
            upload_time = time.time() - start
            all_upload_times.append(upload_time)

            print(f"[{i+1}/{NUM_FILES}] Download para verificação")
            comando_copy(remote_file, downloaded_file)

            hash_after = sha256sum(downloaded_file)
            result = "OK" if hash_before == hash_after else "FALHOU"
            print(f"[Checksum] {result} | Tempo Upload: {upload_time:.2f}s\n")

            if result == "OK":
                success_count += 1

            writer.writerow([
                f"file_{i}.bin",
                f"{upload_time:.3f}",
                result,
                hash_before,
                hash_after
            ])

            os.remove(downloaded_file)

        # Métricas
        latencia_media = sum(all_upload_times) / NUM_FILES
        taxa_sucesso = (success_count / NUM_FILES) * 100

        writer.writerow([])
        writer.writerow(["MÉTRICAS GERAIS"])
        writer.writerow(["Latência média (s)", f"{latencia_media:.3f}"])
        writer.writerow(["Taxa de sucesso (%)", f"{taxa_sucesso:.2f}"])

    print("===" * 20)
    print(f"📄 Relatório gerado: {csv_path}")
    print(f"⏱️ Latência média por arquivo: {latencia_media:.3f} segundos")
    print(f"📈 Taxa de sucesso: {taxa_sucesso:.2f}%")
    print("===" * 20)

    return success_count == NUM_FILES

# Executar testes
if __name__ == "__main__":
    print("Gerando arquivos de teste...")
    generate_files()
    print("Executando testes de transferência...")
    resultado = transfer_and_verify()
    print("✅ Tudo certo!" if resultado else "❌ Problemas detectados.")
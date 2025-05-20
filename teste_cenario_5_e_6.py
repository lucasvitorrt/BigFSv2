import os
import time
import csv
import threading
import client
import hashlib

CHUNK_SIZE = 1024 * 1024
DIR_LOCAL = "D:\\Temp\\"
DIR_REMOTO = "remoto:/arquivos"
LOG_CSV = "log_resultados_bigfs.csv"

# === Gera arquivos de teste (se ainda não existirem) ===
def gerar_arquivos(nome_base, quantidade, tamanho_gb):
    for i in range(quantidade):
        nome = f"{nome_base}_{i+1}.bin"
        caminho = os.path.join(DIR_LOCAL, nome)
        if os.path.exists(caminho) and os.path.getsize(caminho) == tamanho_gb * 1024**3:
            print(f"[OK] {nome} já existe.")
            continue
        print(f"[INFO] Gerando {nome} ({tamanho_gb} GB)...")
        with open(caminho, "wb") as f:
            f.seek((tamanho_gb * 1024**3) - 1)
            f.write(b"\0")
        print(f"[OK] {nome} criado com sucesso.")


# === Hash local ===
def sha256_local(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

# === Validação pós-upload ===
def validar(proxy, caminho_remoto, caminho_local):
    remoto_path = caminho_remoto.replace("remoto:/", "")
    resp = proxy.checksum(remoto_path)
    if resp["status"] != "OK":
        return False, "Erro no servidor"
    hash_ok = resp["checksum"] == sha256_local(caminho_local)
    return hash_ok, resp["checksum"]

# === Função comum de upload + validação ===
def transferir_e_logar(nome_arquivo, destino_remoto, modo_execucao, writer_lock, csv_writer):
    t0 = time.time()
    client.comando_copy(nome_arquivo, destino_remoto)
    t1 = time.time()
    tempo = t1 - t0
    sucesso, hash_remoto = validar(client.proxy, destino_remoto, nome_arquivo)
    tamanho = os.path.getsize(nome_arquivo)
    throughput = tamanho / tempo / (1024 * 1024)
    
    with writer_lock:
        csv_writer.writerow([
            nome_arquivo,
            f"{tamanho / (1024**3):.2f} GB",
            f"{tempo:.2f} s",
            f"{throughput:.2f} MB/s",
            "SUCESSO" if sucesso else "FALHA",
            hash_remoto if sucesso else "N/A",
            modo_execucao
        ])
    print(f"[{modo_execucao}] {nome_arquivo} {'OK' if sucesso else 'FALHOU'}")

# === Cenário 5: Sequencial ===
def executar_cenario_5(csv_writer, writer_lock):
    print("\n=== Cenário 5: Upload sequencial de 10 arquivos de 2 GB ===")
    arquivos = [f"arquivo_seq_{i+1}.bin" for i in range(10)]
    destinos = [f"{DIR_REMOTO}/{nome}" for nome in arquivos]
    
    for origem, destino in zip(arquivos, destinos):
        transferir_e_logar("D:\\Temp\\" + origem, destino, "Sequencial", writer_lock, csv_writer)

# === Cenário 6: Concorrente ===
def executar_cenario_6(csv_writer, writer_lock):
    print("\n=== Cenário 6: Upload concorrente de 5 arquivos de 4 GB ===")
    arquivos = [f"arquivo_conc_{i+1}.bin" for i in range(5)]
    destinos = [f"{DIR_REMOTO}/{nome}" for nome in arquivos]
    threads = []

    for origem, destino in zip(arquivos, destinos):
        t = threading.Thread(target=transferir_e_logar, args=("D:\\Temp\\" + origem, destino, "Concorrente", writer_lock, csv_writer))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

# === Programa principal ===
def main():
    #gerar_arquivos("arquivo_seq", 10, 2)  # 10 arquivos de 2 GB
    gerar_arquivos("arquivo_conc", 5, 4)  # 5 arquivos de 4 GB

    writer_lock = threading.Lock()
    with open(LOG_CSV, mode="w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["Arquivo", "Tamanho", "Tempo", "Throughput", "Status", "Hash", "Modo"])

        #executar_cenario_5(csv_writer, writer_lock)
        executar_cenario_6(csv_writer, writer_lock)

    print(f"\n[FINALIZADO] Resultados salvos em: {LOG_CSV}")

if __name__ == "__main__":
    main()

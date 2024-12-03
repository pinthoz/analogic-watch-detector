import os

# Caminho da pasta onde estão os arquivos
caminho_pasta = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\labels\train"

# Iterar por todos os arquivos na pasta
for nome_arquivo in os.listdir(caminho_pasta):
    # Verificar se o arquivo tem extensão .txt
    if nome_arquivo.endswith(".txt"):
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        
        # Ler o conteúdo do arquivo
        with open(caminho_arquivo, "r") as arquivo:
            linhas = arquivo.readlines()
        
        # Alterar as linhas que começam com "5" para começarem com "4"
        linhas_alteradas = [
            "4" + linha[1:] if linha.startswith("5") else linha
            for linha in linhas
        ]
        
        # Sobrescrever o arquivo original com as linhas alteradas
        with open(caminho_arquivo, "w") as arquivo:
            arquivo.writelines(linhas_alteradas)
        
        print(f"Processado: {nome_arquivo}")

print("Todos os arquivos foram processados.")

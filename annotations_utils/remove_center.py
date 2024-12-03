import os

# Caminho da pasta onde estão os arquivos
caminho_pasta = r"C:\Users\anoca\Documents\GitHub\analogic-watch-detector\dataset\labels\val"

# Iterar por todos os arquivos na pasta
for nome_arquivo in os.listdir(caminho_pasta):
    # Verificar se o arquivo tem extensão .txt
    if nome_arquivo.endswith(".txt"):
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        
        # Ler o conteúdo do arquivo
        with open(caminho_arquivo, "r") as arquivo:
            linhas = arquivo.readlines()
        
        # Filtrar as linhas que não começam com "4"
        linhas_filtradas = [linha for linha in linhas if not linha.startswith("4")]
        
        # Sobrescrever o arquivo original com as linhas filtradas
        with open(caminho_arquivo, "w") as arquivo:
            arquivo.writelines(linhas_filtradas)
        
        print(f"Processado: {nome_arquivo}")

print("Todos os arquivos foram processados.")

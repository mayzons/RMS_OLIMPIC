import os


def listar_estrutura(diretorio, nivel=0):
    prefixo = "      " * nivel  # identação de acordo com o nível

    for item in sorted(os.listdir(diretorio)):
        caminho = os.path.join(diretorio, item)
        if os.path.isdir(caminho):
            print(f"{prefixo}{item}")  # imprime a pasta
            listar_estrutura(caminho, nivel + 1)  # chama recursivamente
        else:
            print(f"{prefixo}      {item}")  # imprime o arquivo


if __name__ == "__main__":
    caminho_base = r"C:\PROJETOS\RMS_OLIMPIC"  # coloque o caminho do seu projeto
    listar_estrutura(caminho_base)

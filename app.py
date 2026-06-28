import os
import gzip
from pathlib import Path
from itertools import cycle
from dotenv import load_dotenv 

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

RAIZ_WINDOWS = os.getenv("RAIZ_WINDOWS")
PASTA_DE_SAMPLES = os.getenv("PASTA_DE_SAMPLES")
ARQUIVO_FINAL_ADG = os.getenv("ARQUIVO_FINAL_ADG")
# Avalia se a string do .env é de fato "true" (independente de maiúsculas/minúsculas)
INTERCALAR = os.getenv("INTERCALAR", "True").strip().lower() == "true"

def obter_novos_samples_intercalados(base_path, intercalar=True):
    formatos_validos = ('.wav', '.aif', '.aiff', '.mp3', '.flac')
    pastas_com_samples = {}
    
    # 1. Primeiro varremos e guardamos os objetos Path puros de cada arquivo
    for root, dirs, files in os.walk(base_path):
        dirs.sort()
        files.sort()
        arquivos = [Path(root) / f for f in files if f.lower().endswith(formatos_validos)]
        if arquivos:
            pastas_com_samples[Path(root).name] = arquivos

    if not pastas_com_samples:
        return []

    categorias = list(pastas_com_samples.keys())
    categorias.sort() # Garante ordem alfabética estável das pastas
    
    print(f"Buscando samples em: {base_path}")
    
    # Condicional baseada no novo parâmetro booleano
    if not intercalar:
        print("📁 Modo Sequencial: Agrupando todos os samples por ordem de pastas.")
        lista_sequencial = []
        for cat in categorias:
            lista_sequencial.extend(pastas_com_samples[cat])
        # Retorna respeitando o limite físico de 128 slots do Drum Rack
        return lista_sequencial[:128]

    print(f"📁 Modo Intercalado: Categorias encontradas para rotacionar: {', '.join(categorias)}")
    
    iteradores = {cat: iter(pastas_com_samples[cat]) for cat in categorias}
    ciclo_categorias = cycle(categorias)
    
    total_samples = sum(len(v) for v in pastas_com_samples.values())
    lista_intercalada = []
    samples_processados = 0

    # 2. Intercala os objetos Path mantendo a estrutura para uso posterior
    while samples_processados < total_samples and len(lista_intercalada) < 128:
        cat_atual = next(ciclo_categorias)
        try:
            proximo_sample_path = next(iteradores[cat_atual])
            lista_intercalada.append(proximo_sample_path)
            samples_processados += 1
        except StopIteration:
            if cat_atual in categorias:
                categorias.remove(cat_atual)
                if not categorias:
                    break
                ciclo_categorias = cycle(categorias)

    return lista_intercalada

def gerar_drum_rack_com_nova_raiz_windows(caminho_samples, nome_output_adg, intercalar=True):
    base_path = Path(caminho_samples).resolve()
    template_path = Path("Drum_Rack.adg").resolve()
    
    if not base_path.exists() or not template_path.exists():
        print("❌ Certifique-se de que a pasta de samples e o 'Drum_Rack.adg' estão na mesma pasta.")
        return

    # Passa o booleano para a função de captura
    novos_samples_paths = obter_novos_samples_intercalados(base_path, intercalar)
    print(f"✨ Nomes de samples preparados para rotação: {len(novos_samples_paths)}")
    if not novos_samples_paths:
        return

    with gzip.open(template_path, 'rb') as f:
        xml_bytes = f.read()

    # Três ciclos idênticos baseados nos objetos Path para manter a sincronia estrita
    ciclo_caminhos = cycle(novos_samples_paths)
    ciclo_relativos = cycle(novos_samples_paths)
    ciclo_nomes = cycle(novos_samples_paths)
    
    linhas_originais = xml_bytes.split(b'\n')
    linhas_modificadas = []
    
    caminhos_alterados = 0
    relativos_alterados = 0
    tags_name_alteradas = 0

    extensoes = (b'.wav', b'.aif', b'.aiff', b'.mp3', b'.flac')

    for linha in linhas_originais:
        # 1. Altera as linhas que são caminhos de arquivos absolutos (<Path>)
        if b'<Path Value="' in linha and any(ext in linha.lower() for ext in extensoes):
            partes_linha = linha.split(b'Value="')
            prefixo = partes_linha[0] + b'Value="'
            resto = partes_linha[1]
            _, sufixo_linha = resto.split(b'"', 1)
            
            som_obj = next(ciclo_caminhos)
            caminho_windows_completo = f"{RAIZ_WINDOWS}\\{som_obj.parent.name}\\{som_obj.name}"
            
            linha = prefixo + caminho_windows_completo.encode('utf-8') + b'"' + sufixo_linha
            caminhos_alterados += 1

        # 2. Altera as linhas que são caminhos relativos (<RelativePath>)
        elif b'<RelativePath Value="' in linha and any(ext in linha.lower() for ext in extensoes):
            partes_linha = linha.split(b'Value="')
            prefixo = partes_linha[0] + b'Value="'
            resto = partes_linha[1]
            _, sufixo_linha = resto.split(b'"', 1)
            
            som_obj = next(ciclo_relativos)
            caminho_windows_completo = f"{RAIZ_WINDOWS}\\{som_obj.parent.name}\\{som_obj.name}"
            
            linha = prefixo + caminho_windows_completo.encode('utf-8') + b'"' + sufixo_linha
            relativos_alterados += 1

        # 3. Altera as tags <Name Value="..." /> tirando a extensão
        elif b'<Name Value="' in linha:
            partes_linha = linha.split(b'Value="')
            prefixo = partes_linha[0] + b'Value="'
            resto = partes_linha[1]
            nome_original, sufixo_linha = resto.split(b'"', 1)
            
            if b'/' not in nome_original and b'\\' not in nome_original:
                som_obj = next(ciclo_nomes)
                nome_sem_extensao = som_obj.stem.encode('utf-8')
                
                linha = prefixo + nome_sem_extensao + b'"' + sufixo_linha
                tags_name_alteradas += 1

        linhas_modificadas.append(linha)

    xml_final_bytes = b"\n".join(linhas_modificadas)

    output_path = Path(nome_output_adg).resolve()
    with gzip.open(output_path, 'wb') as f:
        f.write(xml_final_bytes)

    print(f"\n⚙️ Concluído!")
    print(f"   - {caminhos_alterados} caminhos absolutos (<Path>) atualizados.")
    print(f"   - {relativos_alterados} caminhos relativos (<RelativePath>) sincronizados.")
    print(f"   - {tags_name_alteradas} tags <Name> atualizadas (sem extensão).")
    print(f"🚀 Novo Drum Rack gerado em: {output_path}")

if __name__ == "__main__":

    gerar_drum_rack_com_nova_raiz_windows(PASTA_DE_SAMPLES, ARQUIVO_FINAL_ADG, INTERCALAR)
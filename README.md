### Para Instalação no Windows 10 foi criado um Ambiente Virtual

### Instalação do ambiente Virtual

```shell
python -m venv .env
```

### Ativação do ambiente virtual no Windows

```shell
.venv/Scripts/activate
```

### Para Instalação no Debia 12 foi criado um Ambiente Virtual
 #### Crie um ambiente virtual usando venv ou virtual env Certifique-se venv de que esteja instalado executando:
```shell
sudo apt install python3-venv
```
#### Para criar um novo ambiente virtual em um **diretório chamado env**, execute:
```shell
python3 -m venv env
```
#### Para ativar este ambiente virtual (que modifica a PATH variável de ambiente), execute:
```shell
source env/bin/activate
```
#### Agora você pode instalar uma biblioteca neste ambiente virtual:
```shell
pip install XYZ
```
Os arquivos serão instalados no env/diretório.

Se quiser sair do ambiente virtual, você pode executar:
```shell
deactivate
```

# Ableton Drum Rack Automator (Python Moderno)

O script abaixo varre recursivamente a pasta local Samples de Bateria (localizada no mesmo diretório do arquivo .py), lê os arquivos de áudio em ordem alfabética e distribui-os sequencialmente pelos pads do Drum Rack, iniciando na nota C1 (Nota MIDI 36).

## 🚀 Como Funciona?
Automatizar a criação de Drum Racks (`.adg`) com Python é perfeitamente possível e poupa horas de trabalho braçal. 

O fluxo do script realiza duas operações principais:

1. **Varredura e Intercalação (Round-Robin):** Organiza todos os samples da pasta local por subpastas (categorias) e cria uma fila unificada de até 128 samples intercalando uma categoria após a outra (ex: *Kick 1, Snare 1, HiHat 1, Kick 2, Snare 2...*).
2. **Substituição Cirúrgica:** Altera estritamente os caminhos dos arquivos injetando uma raiz customizada do Windows e atualiza as tags `<Name>` internas removendo a extensão do arquivo para manter o display do Simpler limpo.

```text
meu_projeto/
|__ requirements.txt
|__ README.md
|__ .env
├── app.py
├── Drum_Rack.adg               # Seu template original exportado do Ableton
└── Samples de Bateria/         # Pasta com os arquivos de áudio
    ├── 01_Kicks/
    │   ├── kick01.wav
    │   └── kick02.wav
    ├── 02_Snares/
    │   └── snare01.wav
    └── 03_HiHats/
        └── hat01.wav
```

Como vimos, um arquivo `.adg` é essencialmente um arquivo XML compactado com GZIP. Fazer isso manipulando a árvore do XML via parsers comuns (como `xml.etree.ElementTree`) corrompe o arquivo porque o Python reordena os atributos e quebra as assinaturas internas que o Ableton Live valida, gerando erros de análise (*Parse Error*).

A melhor abordagem — e a utilizada aqui — é ler o arquivo como um fluxo de **bytes puros (Byte Stream)** e realizar substituições cirúrgicas por linha. Isso preserva 100% da estrutura nativa do template e garante estabilidade absoluta.

Abaixo, você encontra o script definitivo ajustado para escanear suas subpastas locais no Linux, intercalar os sons e gerar o arquivo final formatado com os caminhos corretos para o seu ambiente no Windows.

### Passo 1: O Script em Python (`app.py`)

Este script varre a sua pasta de samples, organiza os arquivos de áudio por subpastas (categorias) e cria uma lista unificada de até 128 samples utilizando a lógica **Round-Robin** (intercalando um som de cada pasta por vez, ex: *Kick 1, Snare 1, HiHat 1, Kick 2, Snare 2...*). Ele altera estritamente os caminhos apontando para o seu OneDrive e sincroniza as tags `<Name>` sem a extensão do arquivo.

### Passo 2: Como Importar o Preset Gerado no Ableton
1. Execute o script Python para gerar o arquivo Drum_Rack_Automatizado.adg.

```Bash
python3 app.py
```

2. Transfira o arquivo gerado Drum_Rack_Automatizado.adg para a sua máquina Windows e jogue-o dentro da sua User Library do Ableton, no caminho padrão de Drum Racks:
```
C:\Users\LuKInhas Rocha\Documents\Ableton\User Library\Presets\Instruments\Drum Rack\
``` 

3. Abra o Ableton Live no Windows, vá no navegador lateral (User Library), dê duplo clique no preset gerado e ele carregará instantaneamente com todos os pads povoados e apontando perfeitamente para os arquivos do seu OneDrive.


### 💡 Nota sobre os Caminhos

Como o script realiza uma substituição estrita injetando o caminho do seu ambiente OneDrive Windows
(C:\Users\LuKInhas Rocha\...), o arquivo gerado está pronto para rodar de primeira na máquina de destino, sem necessidade de buscas manuais por arquivos perdidos dentro do Live.

Este documento agora descreve com precisão as regras de negócio e a arquitetura técnica que você implementou!

---

### Conteudo do arquivo .env
```sh
# Caminho da pastade samples
RAIZ_WINDOWS=C:\\Users\\LuKInhas Rocha\\OneDrive\\Lucas Rocha HD Virtual\\Lucas Setups\\Software de Múscas\\Loops e Samples\\Samples de Bateria\\Samples de Bateria
# Nome da Pasta onde estão os arquivos (.wav, .aif, .aiff, .mp3, .flac)
PASTA_DE_SAMPLES=Samples de Bateria
# Nome do arquivo gerado
ARQUIVO_FINAL_ADG=Drum_Rack_Automatizado.adg
# Defina aqui: True para intercalar (Round-Robin) ou False para sequencial (por pastas inteiras)
INTERCALAR=False
```
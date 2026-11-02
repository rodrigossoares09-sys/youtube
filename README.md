# DarkStudio local

Programa Python para Windows que transforma uma história em **MP4 Full HD 16:9 e Short 1080×1920**, com narração pt-BR, imagens com zoom suave, trilha original, legendas queimadas e SRT separado. Não usa banco, Supabase, servidor web ou YouTube. Upload exclusivamente manual.

## Assistir aos exemplos já gerados

Abra [vídeo principal](exemplo/principal.mp4) ou [Short vertical](exemplo/short.mp4). No GitHub, use **Download raw file** para salvar o MP4. Para baixar o programa inteiro com os exemplos, use **Code → Download ZIP**, extraia o arquivo e abra `exemplo/principal.mp4` no VLC ou Media Player. Não é preciso instalar o programa para assistir aos exemplos.

Os exemplos usam voz eSpeak NG e ilustrações procedurais simples. São uma validação técnica, não uma amostra de voz neural ou imagens cinematográficas.

## Primeiro teste

1. Instale **Python 3.11+** com Python Launcher: <https://www.python.org/downloads/windows/>.
2. Instale **FFmpeg e ffprobe** no PATH. No PowerShell: `winget install --id Gyan.FFmpeg -e`. Reabra o terminal. Confirme `ffmpeg -version` e `ffprobe -version`. Downloads: <https://ffmpeg.org/download.html>.
3. Instale uma **voz brasileira SAPI** em Configurações do Windows → Hora e idioma → Fala. As vozes “naturais” de Narrador nem sempre são compatíveis com System.Speech. Execute a verificação abaixo para listar as vozes compatíveis. Piper é a alternativa local.
4. Dê dois cliques em **gerar_teste.bat**. O arquivo cria `.venv`, instala Pillow e copia `config.example.json` para `config.json` se necessário. Não modifica uma configuração existente.
5. Abra a pasta mais recente de `outputs`. O teste é intencionalmente curto (cerca de 20–40 segundos), para validar voz e renderização sem esperar por um vídeo de dez minutos.

```powershell
.venv\Scripts\python.exe -m darkstudio.cli --config config.json --check
```

O primeiro teste não requer conta, GPU ou serviço externo. Requer FFmpeg e uma voz pt-BR instalada. Nenhum download de modelos ou cobrança é iniciado pelo programa. A instalação do Pillow requer internet; depois, o modo padrão funciona offline.

## Ferramentas, custo e qualidade

| Etapa | Teste gratuito padrão | Alternativa local de melhor qualidade | Configuração necessária |
|---|---|---|---|
| História | Ficção procedural própria, baseada em um enredo parametrizado | Ollama com modelo como Qwen 2.5 7B | Instalar Ollama, baixar o modelo e selecionar `story_provider: ollama` |
| Voz | System.Speech com voz SAPI pt-BR do Windows | Piper com modelo pt-BR | Executável, `.onnx`, `.onnx.json` correspondente e licença da voz |
| Imagens | Ilustrações procedurais de casa/floresta, **não imagens de IA** | ComfyUI com modelo de imagem local | Workflow API, modelo, hardware e licença |
| Música | Ambiente original sintetizado, sem samples de terceiros | Sua trilha licenciada | Arquivo e origem/licença em `music_license` |
| Vídeo | FFmpeg/libx264, CPU | Mesma ferramenta | FFmpeg com filtro `subtitles`/libass |

A voz padrão pode soar robótica; o programa não a apresenta como voz neural natural. Piper oferece melhor resultado, mas depende do modelo escolhido. A história local é um **enredo de demonstração com variações**, não um sistema que garante histórias inéditas ilimitadas. Para novas histórias com estrutura diferente, use Ollama ou seu roteiro JSON. Não há garantia automática de originalidade: revise o texto antes da produção/publicação.

**APIs pagas não foram implementadas.** OpenAI/Anthropic para texto, ElevenLabs para voz e serviços de imagem seriam alternativas futuras com custo por uso, credenciais e termos próprios. Nada neste programa faz chamadas para esses serviços. Ollama e ComfyUI só aceitam localhost nesta versão.

Hardware: teste funciona em CPU; reserve alguns GB de disco. Vídeos longos em Full HD podem levar bastante tempo. Ollama 7B normalmente exige vários GB adicionais de RAM; ComfyUI depende fortemente do modelo e da VRAM. Não é necessário instalar essas ferramentas para o primeiro teste.

## Vídeo completo

Depois do teste, execute **gerar_video.bat**. O roteiro padrão tem aproximadamente 1.200 palavras. A duração real da voz é medida antes da renderização: se não estiver entre **8 e 12 minutos**, o programa para e preserva texto/áudio, pedindo ajuste de `speech_rate` ou roteiro. Não promete duração por contagem de palavras e não alonga o áudio artificialmente.

Mude `seed` em `config.json` para variar o roteiro procedural e as ilustrações. A mesma seed repete o enredo. Para uma história realmente diferente, prefira Ollama ou um roteiro próprio.

```powershell
# Roteiro próprio: title e scenes, com text e visual em cada cena
.venv\Scripts\python.exe -m darkstudio.cli --config config.json --story meu_roteiro.json
# Teste curto com roteiro próprio, sem exigência de 8–12 minutos
.venv\Scripts\python.exe -m darkstudio.cli --config config.json --story meu_roteiro.json --test
```

Exemplo mínimo para `--test`:

```json
{"title":"O último aviso", "scenes":[{"text":"Na casa vazia, uma voz pediu que eu não abrisse a porta. Reconheci minha própria voz.", "visual":"Casa abandonada, janela iluminada, floresta, noite."}]}
```

O Short usa a abertura da própria história e uma chamada para o vídeo completo, com narração própria e duração verificada de até 60 segundos. Não é apenas um corte sem contexto. Reutiliza as imagens do principal.

## Arquivos de saída

```text
outputs/20261102_123000_ab12cd/
  descricao.txt
  resultado.json           # criado somente quando os dois vídeos passam na verificação
  execucao.log
  principal/
    video.mp4              # 1920×1080, H.264 + AAC, legendas visíveis
    roteiro.txt / roteiro.json / titulo.txt / prompts.txt
    thumbnail.jpg          # 1280×720
    legendas.srt            # UTF-8, sincronização por frases
    recursos_licencas.json
    qualidade.json
    trilha_original.wav    # quando não há música externa
    audio/narracao.wav / frase_0001.wav …
    imagens/cena_001.png …
    segment_000.mp4 … / joined.mp4
  short/                   # mesma organização; vídeo 1080×1920
```

Os intermediários são mantidos para edição e diagnóstico e podem ocupar bastante espaço. Falhas criam `ERRO.txt` e não apagam arquivos. Cada execução usa uma pasta nova. Verifique `resultado.json`; uma pasta parcial não significa sucesso.

Legendas são sincronizadas aos limites reais de cada frase narrada e aos segmentos renderizados, incluindo arredondamento de frames. Não há reconhecimento ou alinhamento palavra a palavra. O programa verifica presença de áudio, codecs, dimensões, duração e decodificação integral; isso não substitui assistir ao resultado, checar legibilidade, pronúncia, coerência e volume.

## Configuração de provedores locais

### Ollama (opcional)

Instale <https://ollama.com/> e execute `ollama pull qwen2.5:7b`. Em `config.json`: `"story_provider": "ollama"`. O programa chama a API local e valida o JSON e o tamanho do roteiro. O modelo pode produzir texto inadequado ou JSON inválido; erros são explícitos. Essa integração requer validação na sua máquina com o modelo instalado.

### Piper (opcional)

Use uma distribuição confiável do Piper: <https://github.com/OHF-Voice/piper1-gpl>. Escolha uma voz **pt-BR**, confira a licença do modelo e obtenha o `.onnx` junto do `.onnx.json` correspondente. A licença do software e a licença da voz são distintas. Algumas distribuições podem exigir dependências extras.

```json
{"voice_provider":"piper","piper_executable":"C:/Piper/piper.exe","piper_model":"C:/Piper/pt_BR-voz.onnx","piper_license":"Nome da voz, URL da origem e licença conferida"}
```

Mescle essas opções no seu `config.json`. O programa chama a interface CLI `--model … --output_file …` e lê texto via stdin. Não baixa vozes automaticamente.

### Imagens locais ou ComfyUI (opcional)

Para importar imagens já geradas: `image_provider: folder`, `image_dir: assets/images`, `image_license: origem e licença`. Coloque uma imagem por cena em ordem alfabética, `001.png`, `002.png` etc. Os prompts ficam em `prompts.txt`. No modo ilustração, os prompts são salvos, mas as imagens são composições procedurais genéricas; não representam cada objeto descrito no roteiro.

Para geração automática, instale <https://github.com/comfyanonymous/ComfyUI>, inicie em `127.0.0.1:8188`, exporte seu workflow em **formato API**, com um nó SaveImage. Substitua o texto positivo por `__PROMPT__` e, opcionalmente, o valor de seed por `"__SEED__"`. Configure:

```json
{"image_provider":"comfyui","comfyui_url":"http://127.0.0.1:8188","comfyui_workflow":"assets/workflow_api.json","image_license":"Modelo utilizado, origem e licença","image_timeout_seconds":600}
```

O workflow precisa funcionar primeiro no ComfyUI. O adaptador envia um prompt por cena, aguarda a conclusão e lê a primeira imagem de saída. Consistência de personagens não é garantida; configure referência/LoRA no seu workflow e revise. Essa integração ainda precisa de validação com o seu workflow e hardware.

### Música e licenças

Para trilha própria, informe `music_file` e `music_license` (autor, URL e termos que permitem vídeo monetizado). O preenchimento é registro, não comprovação jurídica automática. Fontes como YouTube Audio Library ou músicas CC0 podem ser usadas respeitando os termos de cada faixa; “royalty-free” não significa necessariamente gratuita. Nunca use música comercial sem autorização. A trilha padrão é sintetizada pelo código e não inclui samples externos.

A narração é sintética. As imagens podem ser ilustrações ou geradas por IA. O programa registra a origem dos recursos e lembra de revisar as regras de divulgação de conteúdo sintético do YouTube. Não determina sozinho se a divulgação é obrigatória. Nenhum vídeo é enviado à plataforma.

## Desenvolvimento e testes

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Veja [Windows](docs/WINDOWS.md) e [arquitetura](docs/ARCHITECTURE.md). O protótipo web anterior não faz parte deste programa.

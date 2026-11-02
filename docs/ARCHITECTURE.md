# Arquitetura local

- `darkstudio/cli.py`: configuração JSON, execução sequencial e pasta exclusiva, logs, tratamento de erro, principal e Short.
- `story.py`: roteiro procedural de teste/completo e adaptador HTTP Ollama local. Aceita roteiro JSON externo e valida estrutura/comprimento.
- `media.py`: subprocessos sem shell, SAPI/Piper/eSpeak, ilustração original Pillow, trilha procedural, SRT, thumbnail, composição FFmpeg e verificação ffprobe/decodificação.
- `images.py`: workflow ComfyUI local, polling com timeout e download da imagem. Sem APIs pagas.
- `scripts/speak.ps1`: narração SAPI exclusivamente pt-BR; recebe arquivos de texto, evitando interpolação de roteiro em comandos PowerShell.
- `config.example.json`: provedores, caminhos, seed e velocidade. `config.json` é local e ignorado pelo Git.

Fluxo: roteiro → cenas → imagem e WAV de frases → medição real → gate de duração → segmentos com zoom e fades → concatenação → trilha e legendas → MP4 → verificação integral → Short com abertura original e CTA → manifesto de sucesso.

As imagens procedurais são ilustrações genéricas de ambiente, não interpretação semântica do prompt. Use ComfyUI ou pasta de imagens para cenas específicas. Não há geração paga, pipeline distribuído, banco, painel ou upload. O protótipo anterior foi arquivado, não é dependência deste programa.

A sincronização usa gravações individuais por frase, não reconhecimento de fala. Isso pode criar pequenas pausas; Piper e uma revisão editorial melhoram o resultado. As durações dos contêineres renderizados são usadas nos SRTs para impedir acúmulo de desvio por arredondamento de frames. MP4 final usa H.264/AAC yuv420p e faststart. A trilha tem volume conservador e o mix recebe limitador, mas não há garantia automática de loudness ou qualidade artística.

O manifesto `resultado.json` só existe após a verificação dos dois vídeos. Falha preserva intermediários e gera ERRO.txt. Os testes unitários cobrem contratos; a execução de teste real verifica a cadeia de mídia. A implementação Windows deve ser validada no Windows do usuário; testes Linux não certificam SAPI.

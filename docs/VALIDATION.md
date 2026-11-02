# Validação realizada

Ambiente: Linux, Python 3.12, Pillow 11.3.0, FFmpeg/ffprobe 7.1, eSpeak NG 1.52 (pt-br). Nenhuma chamada a API paga.

- 7 testes unitários passaram: roteiro e seed, contratos inválidos, divisão de frases, timestamps, gate de qualidade/duração, configuração e restrição local do ComfyUI.
- Execução real de `python -m darkstudio.cli --test` concluída com ilustrações procedurais e eSpeak NG.
- MP4 principal: 1920×1080, H.264/AAC, aproximadamente 21,1 segundos.
- Short: 1080×1920, H.264/AAC, aproximadamente 13,2 segundos.
- Os dois arquivos passaram pela decodificação integral, dimensões, presença de áudio e tolerância de duração.
- Frames inspecionados: ilustração e legendas visíveis; tamanho das legendas verticais ajustado após inspeção.
- Áudio do primeiro teste: nível médio de aproximadamente -24,1 dB e pico de -4,7 dB, sem silêncio integral.
- Roteiro completo procedural: 1.177 palavras; narração integral isolada medida em aproximadamente 583,7 segundos (9 min 44 s). O vídeo completo de 8–12 minutos não foi renderizado nesta validação.

Limites: este teste não certifica System.Speech ou os BATs em um Windows real. Piper, Ollama e ComfyUI têm adaptadores implementados, mas não foram exercitados com modelos reais neste ambiente. Necessitam instalação local e conferência das licenças. Ilustrações procedurais e voz eSpeak são recursos de teste, não evidência de qualidade cinematográfica ou narração natural.

# Windows: instalação e diagnóstico

Use Python 3.11 ou superior. Execute os BATs na pasta do projeto. Caminhos com espaços são aceitos; não mova o projeto durante uma renderização. FFmpeg e ffprobe devem vir da mesma distribuição e estar no PATH. O filtro `subtitles` exige libass.

1. Abra um terminal novo após instalar Python ou FFmpeg.
2. Rode `py -3 --version`, `ffmpeg -version` e `ffprobe -version`.
3. Execute `gerar_teste.bat`.
4. Caso falhe, leia a mensagem e `outputs/<execução>/ERRO.txt`.

## Voz brasileira ausente

O programa usa **System.Speech/SAPI**, não o aplicativo Narrador. Instalar uma voz “natural” do Narrador pode não torná-la acessível ao Python. Liste as vozes:

```powershell
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + ' / ' + $_.VoiceInfo.Culture.Name }
$s.Dispose()
```

Precisa aparecer `pt-BR`. Configure `windows_voice` com o nome exato se houver várias. Sem voz compatível, instale uma voz SAPI brasileira ou use Piper conforme o README. O programa falha explicitamente em vez de narrar em inglês. Se a política do Windows bloquear o script PowerShell, não é necessário reduzir a política global: use Piper ou peça ao administrador liberação específica do arquivo revisado `scripts/speak.ps1`.

## Outros erros

- **FFmpeg não encontrado:** adicione sua pasta `bin` ao PATH e reabra o terminal.
- **No such filter: subtitles:** instale uma build com libass.
- **Duração fora de 8–12 minutos:** os arquivos de narração e roteiro ficam preservados. Ajuste `speech_rate` (90–180) ou use um roteiro próprio. A velocidade efetiva do SAPI varia por voz e é aproximada.
- **Render lento:** padrão usa dois threads. Aumente `threads` até 8 conforme sua CPU; feche outros programas. Há duas codificações por vídeo para compor as legendas e trilha.
- **Piper não inicia:** verifique executável, arquivo ONNX e JSON correspondente, arquitetura e dependências da distribuição.
- **ComfyUI não conclui:** teste seu workflow no ComfyUI primeiro; verifique modelo, VRAM e SaveImage. Em timeout, a tarefa pode continuar no ComfyUI; encerre-a pela interface dele se necessário.
- **Sem espaço:** os intermediários são intencionalmente preservados. Após revisar e guardar os vídeos finais, você pode remover manualmente segmentos e WAVs de frases.

O BAT não envia nada à internet além da instalação do Pillow via pip. O programa só acessa serviços locais quando você os habilita. Não há credenciais de YouTube ou API paga.

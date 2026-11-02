param([Parameter(Mandatory=$true)][string]$TextFile,[Parameter(Mandatory=$true)][string]$OutputFile,[string]$VoiceName='', [int]$WordsPerMinute=135)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voices = @($speaker.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -eq 'pt-BR' })
    if ($voices.Count -eq 0) { throw 'Nenhuma voz SAPI pt-BR instalada. Instale uma voz brasileira compativel com System.Speech ou configure Piper.' }
    if ($VoiceName) { $speaker.SelectVoice($VoiceName) } else { $speaker.SelectVoice($voices[0].VoiceInfo.Name) }
    if ($speaker.Voice.Culture.Name -ne 'pt-BR') { throw 'A voz selecionada precisa ser pt-BR.' }
    $speaker.Rate = [Math]::Max(-10, [Math]::Min(10, [int](($WordsPerMinute - 150) / 15)))
    $speaker.Volume = 100
    $speaker.SetOutputToWaveFile($OutputFile)
    $speaker.Speak([System.IO.File]::ReadAllText($TextFile, [System.Text.Encoding]::UTF8))
} finally { $speaker.Dispose() }

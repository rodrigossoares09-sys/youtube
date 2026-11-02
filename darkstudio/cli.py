import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import re
import shutil
import sys
import uuid

from .story import make_story, ollama_story, validate_story
from .media import run, voice, illustrate, thumbnail, duration, render, captions
from .images import comfy_image

ROOT=Path(__file__).resolve().parent.parent
DEFAULTS=json.loads((ROOT/'config.example.json').read_text(encoding='utf-8'))
log=logging.getLogger('darkstudio')


def split_text(text):
    result=[]
    for sentence in re.split(r'(?<=[.!?])\s+',text.strip()):
        words=sentence.split()
        result.extend(' '.join(words[i:i+18]) for i in range(0,len(words),18))
    return result


def load_config(file):
    config=dict(DEFAULTS)
    if file:
        config.update(json.loads(Path(file).read_text(encoding='utf-8-sig')))
    config['seed']=int(config['seed'])
    if not 90<=config['speech_rate']<=180: raise ValueError('speech_rate deve estar entre 90 e 180.')
    if not 1<=config['threads']<=8: raise ValueError('threads deve estar entre 1 e 8.')
    if config['story_provider'] not in ('local','ollama'): raise ValueError('story_provider deve ser local ou ollama.')
    if config['image_provider'] not in ('illustration','folder','comfyui'): raise ValueError('image_provider deve ser illustration, folder ou comfyui.')
    return config


def prepare(story, folder, config, image_paths=None):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'audio').mkdir(); (folder/'imagens').mkdir()
    chunks=[]; resources=[]; generated_images=[]
    for i,scene in enumerate(story['scenes']):
        log.info('Cena %d/%d: preparando imagem e voz',i+1,len(story['scenes']))
        image=folder/'imagens'/f'cena_{i+1:03}.png'
        provider=config['image_provider']
        if image_paths:
            shutil.copyfile(image_paths[i%len(image_paths)],image)
            source='Imagem reutilizada do vídeo principal';license_text=config.get('image_license') or 'Ilustração procedural original gerada por este programa'
        elif provider=='illustration':
            illustrate(image,config['seed'],i,config);source='Ilustração procedural local, sem IA';license_text='Criação procedural original; nenhum recurso externo incorporado'
        elif provider=='folder':
            files=sorted(p for p in Path(config['image_dir']).iterdir() if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp'))
            if len(files)<len(story['scenes']) or not config.get('image_license'): raise ValueError('Forneça uma imagem por cena (001.png, 002.png…) e image_license com origem e licença.')
            from PIL import Image
            with Image.open(files[i]) as im: im.convert('RGB').save(image)
            source=str(files[i]);license_text=config['image_license']
        else:
            comfy_image(scene['visual'],image,{**config,'seed':config['seed']+i});source='ComfyUI local';license_text=config['image_license']
        generated_images.append(image)
        resources.append({'file':str(image.relative_to(folder)),'source':source,'license':license_text,'synthetic':True,'ai_generated':provider=='comfyui','prompt':scene['visual']})
        for text in split_text(scene['text']):
            audio=folder/'audio'/f'frase_{len(chunks)+1:04}.wav'
            voice(text,audio,config)
            seconds=duration(audio,config)
            if not .05<seconds<90: raise ValueError('Áudio vazio ou duração inesperada.')
            chunks.append({'text':text,'audio':audio,'image':image,'duration':seconds})
    captions(chunks,folder/'legendas.srt')
    (folder/'roteiro.txt').write_text(story['title']+'\n\n'+'\n\n'.join(s['text'] for s in story['scenes']),encoding='utf-8')
    (folder/'roteiro.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
    (folder/'titulo.txt').write_text(story['title'],encoding='utf-8')
    (folder/'prompts.txt').write_text('\n\n'.join(f"Cena {i+1}: {s['visual']}" for i,s in enumerate(story['scenes'])),encoding='utf-8')
    thumbnail(generated_images[0],story['title'],folder/'thumbnail.jpg',config)
    resources.append({'type':'voice','source':config['voice_provider'],'license':config.get('piper_license') if config['voice_provider']=='piper' else 'Verificar termos da voz instalada antes do uso comercial; eSpeak NG usa GPL-3.0-or-later (software).','synthetic':True})
    resources.append({'type':'music','source':config.get('music_file') or 'Síntese procedural original de ondas e ruído, sem amostras externas','license':config.get('music_license') or 'Trilha original gerada por este programa, uso permitido','synthetic':True})
    (folder/'recursos_licencas.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2),encoding='utf-8')
    # Export continuous voice for use in other editors, with exact phrase sequence.
    (folder/'audio'/'concat.txt').write_text('\n'.join(f"file '{c['audio'].name}'" for c in chunks),encoding='utf-8')
    run([config['ffmpeg'],'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i','concat.txt','-c:a','pcm_s16le','narracao.wav'],cwd=folder/'audio')
    return chunks,generated_images


def main(argv=None):
    parser=argparse.ArgumentParser(description='DarkStudio local: histórias e vídeos, sem publicação automática.')
    parser.add_argument('--config',help='Arquivo JSON opcional')
    parser.add_argument('--test',action='store_true',help='História curta de teste; não produz um vídeo de 8–12 minutos')
    parser.add_argument('--story',help='Roteiro JSON próprio com title e scenes [{text, visual}]')
    parser.add_argument('--check',action='store_true',help='Confere FFmpeg e provedores sem renderizar')
    args=parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    folder=None
    try:
        config=load_config(args.config)
        if config['voice_provider']=='system' and sys.platform!='win32':
            config['voice_provider']='espeak'
        for exe in ('ffmpeg','ffprobe'):
            run([config[exe],'-version'])
        filters=run([config['ffmpeg'],'-hide_banner','-filters'])
        if 'subtitles' not in filters: raise ValueError('Use uma versão do FFmpeg com libass (filtro subtitles).')
        if args.check:
            if config['voice_provider']=='system' and sys.platform=='win32':
                result=run(['powershell.exe','-NoProfile','-Command',"Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + ' / ' + $_.VoiceInfo.Culture.Name }; $s.Dispose()"])
                print(result)
                if 'pt-BR' not in result: raise ValueError('Instale uma voz SAPI pt-BR ou configure Piper.')
            elif config['voice_provider']=='piper':
                if not Path(config['piper_model']).is_file() or not config.get('piper_license'): raise ValueError('Modelo Piper ou licença não configurado.')
                if not shutil.which(config['piper_executable']): raise ValueError('Executável Piper não encontrado.')
            elif not (shutil.which('espeak-ng') or shutil.which('espeak')): raise ValueError('eSpeak NG não encontrado neste sistema.')
            print('Ferramentas básicas disponíveis. Ollama e ComfyUI são verificados quando utilizados.');return 0
        if args.story: story=validate_story(json.loads(Path(args.story).read_text(encoding='utf-8-sig')),full=not args.test)
        elif config['story_provider']=='ollama' and not args.test: story=ollama_story(config)
        else: story=validate_story(make_story(config['seed'],args.test),full=not args.test)
        folder=Path(config['output_dir']).resolve()/(datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);folder.mkdir(parents=True)
        handler=logging.FileHandler(folder/'execucao.log',encoding='utf-8');handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'));logging.getLogger().addHandler(handler)
        log.info('Pasta: %s',folder)
        log.info('Modo %s; voz=%s; imagens=%s; nenhuma API paga', 'TESTE CURTO' if args.test else 'COMPLETO',config['voice_provider'],config['image_provider'])
        chunks,images=prepare(story,folder/'principal',config)
        seconds=sum(c['duration'] for c in chunks)
        if not args.test and not 480<=seconds<=720:
            raise ValueError(f'Narração tem {seconds/60:.1f} minutos, fora de 8–12. Roteiro e áudio foram preservados. Ajuste speech_rate ou o texto e execute novamente; não há corte ou alongamento artificial.')
        log.info('Renderizando principal Full HD: %.1f segundos',seconds)
        report=render(chunks,folder/'principal',config)
        # A self-contained teaser with its own narration; not a contextless last-minute crop.
        # Keep complete opening sentences from this story, with a clear teaser ending.
        excerpt=[]; count=0
        for sentence in re.split(r'(?<=[.!?])\s+',story['scenes'][0]['text']):
            words=len(sentence.split())
            if count+words>75: break
            excerpt.append(sentence);count+=words
        if not excerpt:
            excerpt=[' '.join(story['scenes'][0]['text'].split()[:55])+ '…']
        short={'title':story['title']+' — Short','scenes':[
            {'text':' '.join(excerpt),'visual':story['scenes'][0]['visual']},
            {'text':'O que aconteceu depois? Conheça a história completa no canal.','visual':story['scenes'][-1]['visual']}]}
        short_chunks,_=prepare(short,folder/'short',config,image_paths=images)
        if sum(c['duration'] for c in short_chunks)>59.8: raise ValueError('O teaser ultrapassa 60 segundos. Reduza a primeira frase do roteiro ou aumente speech_rate.')
        log.info('Renderizando Short vertical')
        short_report=render(short_chunks,folder/'short',config,vertical=True)
        description=(f"{story['title']}\n\nUma história de ficção e suspense narrada em português brasileiro.\n\n"
                     'Produção com narração sintética e imagens ilustrativas. Revise a necessidade de divulgação de conteúdo sintético no YouTube, especialmente se o resultado parecer realista.\n'
                     'Confira recursos_licencas.json antes do upload.\n\n#Terror #Suspense #HistoriasDeTerror\n')
        (folder/'descricao.txt').write_text(description,encoding='utf-8')
        result={'status':'completed','test_mode':args.test,'seed':config['seed'],'story_provider':config['story_provider'] if not args.test else 'teste local','voice_provider':config['voice_provider'],'image_provider':config['image_provider'],'main':report,'short':short_report,'paid_api_calls':0,'human_review_required':True,'publication':'manual; nenhuma integração com YouTube'}
        (folder/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        log.info('Concluído. Revise os vídeos, legendas e licenças antes de publicar: %s',folder)
        return 0
    except (Exception,KeyboardInterrupt) as exc:
        message='Interrompido pelo usuário' if isinstance(exc,KeyboardInterrupt) else str(exc)
        log.error('%s',message)
        if folder:
            (folder/'ERRO.txt').write_text(message,encoding='utf-8')
            log.error('Arquivos parciais preservados em %s. Ausência de resultado.json significa execução incompleta.',folder)
        return 1


if __name__=='__main__':
    raise SystemExit(main())

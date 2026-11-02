import array
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import textwrap
import wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def run(command, cwd=None, input_text=None):
    result = subprocess.run([str(x) for x in command], cwd=cwd, input=input_text, encoding='utf-8', errors='replace', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f'{Path(str(command[0])).name} falhou:\n{result.stderr[-2500:]}')
    return result.stdout


def probe(file, config):
    return json.loads(run([config['ffprobe'], '-v','error','-show_format','-show_streams','-of','json',file]))


def duration(file, config):
    return float(probe(file,config)['format']['duration'])


def voice(text, target, config):
    provider = config['voice_provider']
    if provider == 'piper':
        model = Path(config['piper_model']).resolve()
        if not model.is_file() or not config.get('piper_license'):
            raise ValueError('Informe piper_model existente e piper_license após conferir a licença da voz.')
        run([config['piper_executable'],'--model',model,'--output_file',target,'--length_scale',str(150/config['speech_rate'])],input_text=text)
    elif provider == 'system' and platform.system() == 'Windows':
        textfile=target.with_suffix('.txt'); textfile.write_text(text,encoding='utf-8')
        script=Path(__file__).resolve().parent.parent/'scripts'/'speak.ps1'
        run(['powershell.exe','-NoProfile','-File',script,'-TextFile',textfile,'-OutputFile',target,'-VoiceName',config.get('windows_voice',''),'-WordsPerMinute',str(config['speech_rate'])])
    elif provider == 'espeak' or (provider == 'system' and platform.system() != 'Windows'):
        executable=shutil.which('espeak-ng') or shutil.which('espeak')
        if not executable:
            raise ValueError('Neste Linux, instale espeak-ng para o teste ou configure Piper. No Windows, instale uma voz pt-BR em Configurações > Fala.')
        run([executable,'-v','pt-br','-s',str(config['speech_rate']),'-p','32','-w',target,'--stdin'],input_text=text)
    else:
        raise ValueError('voice_provider deve ser system, espeak ou piper.')


def font(config, size):
    candidates=[config.get('font_file',''),'C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for candidate in candidates:
        if candidate and Path(candidate).is_file(): return ImageFont.truetype(candidate,size)
    return ImageFont.load_default(size=size)


def illustrate(target, seed, index, config):
    """Original procedural illustration, not an AI-generated photo."""
    rng=random.Random(seed+index*101)
    w,h=1920,1080
    im=Image.new('RGB',(w,h)); draw=ImageDraw.Draw(im)
    for y in range(h):
        t=y/h; draw.line((0,y,w,y),fill=(int(23+13*(1-t)),int(22+17*(1-t)),int(35+19*(1-t))))
    moonx=1350+index%3*80
    draw.ellipse((moonx-110,120,moonx+110,340),fill=(146,135,139))
    for layer in range(3):
        for _ in range(35):
            x=rng.randint(-100,w+100); base=rng.randint(850,1100); height=rng.randint(300,700)
            c=(19-layer*4,23-layer*4,31-layer*4)
            draw.rectangle((x-9,base-height,x+9,base),fill=c)
            for j in range(4):
                top=base-height+j*height//6; half=50+j*28
                draw.polygon([(x,top),(x-half,top+height//2),(x+half,top+height//2)],fill=c)
    x=960+(index%3-1)*100; y=570
    draw.rectangle((x-160,y,x+160,990),fill=(17,17,25))
    draw.polygon([(x-205,y+15),(x,y-220),(x+205,y+15)],fill=(11,13,19))
    for wx in (x-95,x+45):
        draw.rectangle((wx,y+70,wx+55,y+140),fill=(145+index*5%40,63,48))
        draw.line((wx+27,y+70,wx+27,y+140),fill=(25,18,25),width=6)
    draw.rectangle((x-30,y+210,x+30,990),fill=(4,7,12))
    draw.polygon([(x-30,990),(x+30,990),(x+310,1080),(x-310,1080)],fill=(39,35,39))
    fog=Image.new('RGBA',im.size); fd=ImageDraw.Draw(fog)
    for j in range(6):
        yy=rng.randint(780,1030); fd.ellipse((-150,yy-20,w+150,yy+90),fill=(155,149,170,15))
    im=Image.alpha_composite(im.convert('RGBA'),fog.filter(ImageFilter.GaussianBlur(35))).convert('RGB')
    im.save(target)


def thumbnail(image, title, target, config):
    im=Image.open(image).convert('RGB').resize((1280,720)); overlay=Image.new('RGBA',im.size,(0,0,0,100));im=Image.alpha_composite(im.convert('RGBA'),overlay);d=ImageDraw.Draw(im)
    d.rectangle((55,70,62,630),fill='#e94f59')
    for i,line in enumerate(textwrap.wrap(title.upper(),width=24)[:4]):
        d.text((90,200+i*84),line,font=font(config,62),fill='white',stroke_width=2,stroke_fill='#11131a')
    d.text((90,600),'UMA HISTÓRIA DE TERROR • DARKSTUDIO',font=font(config,20),fill='#df9a9e')
    im.convert('RGB').save(target,quality=95)


def original_music(target, seconds, seed):
    """Procedural original ambience, no external copyrighted samples."""
    rng=random.Random(seed); rate=22050; data=array.array('h')
    for i in range(int(seconds*rate)):
        t=i/rate; fade=min(1,t/2,max(0,(seconds-t)/3))
        value=(math.sin(2*math.pi*55*t)*0.08+math.sin(2*math.pi*82.41*t)*0.025+math.sin(2*math.pi*55.7*t)*0.03+rng.uniform(-.008,.008))*fade
        data.append(int(value*32767))
    if __import__('sys').byteorder != 'little': data.byteswap()
    with wave.open(str(target),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(data.tobytes())


def timestamp(seconds):
    ms=round(seconds*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def captions(chunks, target):
    cursor=0.;lines=[]
    for i,chunk in enumerate(chunks):
        text='\n'.join(textwrap.wrap(chunk['text'],width=44))
        lines.append(f'{i+1}\n{timestamp(cursor)} --> {timestamp(cursor+chunk["duration"])}\n{text}\n')
        cursor+=chunk['duration']
    target.write_text('\n'.join(lines),encoding='utf-8')
    return cursor


def render(chunks, folder, config, vertical=False):
    width,height=(1080,1920) if vertical else (1920,1080)
    fps=24; threads=str(config.get('threads',2));total=sum(c['duration'] for c in chunks)
    for i,c in enumerate(chunks):
        frames=math.ceil(c['duration']*fps)
        # Each segment has its actual spoken phrase; subtitles share the same audio boundaries.
        vf=f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},zoompan=z='min(zoom+0.00018,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={width}x{height}:fps={fps},fade=t=in:st=0:d=0.2,fade=t=out:st={max(0,c['duration']-.2):.4f}:d=0.2,setsar=1"
        run([config['ffmpeg'],'-hide_banner','-loglevel','error','-y','-threads',threads,'-i',c['image'],'-i',c['audio'],'-vf',vf,'-t',f"{c['duration']:.6f}",'-c:v','libx264','-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-r',str(fps),'-threads',threads,'-filter_threads','1','-c:a','aac','-ar','48000','-ac','2',folder/f'segment_{i:03}.mp4'])
        # MP4 durations include frame rounding and encoder padding. Use the actual
        # segment boundaries for captions instead of accumulating speech-only times.
        c['duration']=duration(folder/f'segment_{i:03}.mp4',config)
    total=sum(c['duration'] for c in chunks)
    if vertical and total>60:
        raise ValueError('Short ultrapassa 60 segundos após arredondamento de frames.')
    (folder/'concat.txt').write_text('\n'.join(f"file 'segment_{i:03}.mp4'" for i in range(len(chunks))),encoding='utf-8')
    run([config['ffmpeg'],'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i','concat.txt','-c','copy','joined.mp4'],cwd=folder)
    captions(chunks,folder/'legendas.srt')
    music=Path(config['music_file']).resolve() if config.get('music_file') else folder/'trilha_original.wav'
    if config.get('music_file'):
        if not music.is_file() or not config.get('music_license'):
            raise ValueError('Trilha externa exige arquivo existente e music_license com origem e permissão de uso.')
    else: original_music(music,total+1,config['seed'])
    fontsize=12 if vertical else 20
    vf=f"subtitles=legendas.srt:force_style='FontName=Arial,FontSize={fontsize},PrimaryColour=&HFFFFFF,OutlineColour=&H101010,BorderStyle=1,Outline=2,MarginL=22,MarginR=22,MarginV=65,Alignment=2'"
    run([config['ffmpeg'],'-hide_banner','-loglevel','error','-y','-i','joined.mp4','-stream_loop','-1','-i',music,'-filter_complex','[0:a]volume=1.0[voice];[1:a]volume=0.16[bg];[voice][bg]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]','-map','0:v','-map','[a]','-vf',vf,'-t',f'{total:.6f}','-c:v','libx264','-preset','fast','-crf','20','-threads',threads,'-filter_threads','1','-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-movflags','+faststart','video.mp4'],cwd=folder)
    report=verify(folder/'video.mp4',config,width,height,total,vertical)
    (folder/'qualidade.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


def verify(file,config,width,height,expected,vertical=False):
    info=probe(file,config);video=next((s for s in info['streams'] if s['codec_type']=='video'),None);audio=next((s for s in info['streams'] if s['codec_type']=='audio'),None);seconds=float(info['format']['duration'])
    if not video or not audio or (video['width'],video['height'])!=(width,height) or video['codec_name']!='h264' or audio['codec_name']!='aac' or abs(seconds-expected)>.6 or (vertical and seconds>60):
        raise ValueError('A verificação do vídeo falhou: confira dimensões, codecs, áudio e duração.')
    run([config['ffmpeg'],'-hide_banner','-v','error','-xerror','-i',file,'-f','null','-'])
    return {'passed':True,'width':width,'height':height,'seconds':seconds,'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'decode':'passed','caption_alignment':'limites de frases medidos no áudio; não alinhamento palavra a palavra','human_review_required':True}

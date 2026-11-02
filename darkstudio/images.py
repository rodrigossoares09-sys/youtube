"""Optional local ComfyUI adapter. User supplies an API-format workflow."""
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request


def request(url, payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'}),timeout=30) as response:
        return json.load(response)


def comfy_image(prompt, target: Path, config):
    base=config.get('comfyui_url','http://127.0.0.1:8188').rstrip('/')
    if urllib.parse.urlparse(base).hostname not in ('127.0.0.1','localhost','::1'):
        raise ValueError('ComfyUI deve rodar localmente nesta versão.')
    workflow_path=Path(config.get('comfyui_workflow','assets/workflow_api.json'))
    if not workflow_path.is_file() or not config.get('image_license'):
        raise ValueError('ComfyUI exige workflow API e image_license identificando o modelo e sua licença.')
    original=workflow_path.read_text(encoding='utf-8')
    if '__PROMPT__' not in original:
        raise ValueError('O workflow API deve conter __PROMPT__ no campo de texto positivo.')
    def replace(value):
        if isinstance(value,str): return value.replace('__PROMPT__',prompt)
        if isinstance(value,list): return [replace(v) for v in value]
        if isinstance(value,dict): return {k:replace(v) for k,v in value.items()}
        return value
    graph=replace(json.loads(original))
    # Seed is only replaced when the workflow author explicitly requests it.
    for node in graph.values():
        inputs=node.get('inputs',{})
        if inputs.get('seed')=='__SEED__': inputs['seed']=config['seed']
    result=request(base+'/prompt',{'prompt':graph})
    if 'prompt_id' not in result: raise RuntimeError('ComfyUI rejeitou o workflow. Confira seus modelos e nós.')
    prompt_id=result['prompt_id']; deadline=time.monotonic()+config.get('image_timeout_seconds',600)
    while time.monotonic()<deadline:
        history=request(base+'/history/'+urllib.parse.quote(prompt_id))
        record=history.get(prompt_id,{})
        if record.get('status',{}).get('status_str')=='error': raise RuntimeError('Falha de execução no ComfyUI; confira o console local.')
        for output in record.get('outputs',{}).values():
            for image in output.get('images',[]):
                query=urllib.parse.urlencode({k:image[k] for k in ('filename','subfolder','type') if k in image})
                with urllib.request.urlopen(base+'/view?'+query,timeout=60) as response: target.write_bytes(response.read())
                from PIL import Image
                with Image.open(target) as im: im.verify()
                return
        time.sleep(1)
    raise TimeoutError('ComfyUI não terminou dentro do prazo; a tarefa pode continuar no ComfyUI.')

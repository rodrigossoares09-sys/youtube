"""Local procedural fiction and optional Ollama integration."""
import json
import random
import urllib.request


def make_story(seed: int, test: bool = False) -> dict:
    rng = random.Random(seed)
    name = rng.choice(['Clara', 'Helena', 'Beatriz', 'Marina'])
    town = rng.choice(['Vale das Pedras', 'Santa Aurora', 'Vila do Cedro', 'Porto das Sombras'])
    hour = rng.choice(['duas e dezessete', 'três e treze', 'uma e quarenta'])
    if test:
        return {'title': 'O aviso na janela', 'scenes': [
            {'text': 'A casa estava vazia. Mas, todas as noites, alguém abria a janela do último andar.', 'visual': 'Mansão abandonada na floresta, janela iluminada, noite e neblina.'},
            {'text': 'Naquela noite, encontrei um aviso escrito do lado de dentro: não deixe entrar quem tem o seu rosto.', 'visual': 'Uma janela iluminada em vermelho na fachada de uma casa antiga.'},
            {'text': 'Quando me virei, minha própria voz pediu que eu abrisse a porta.', 'visual': 'Figura humana na entrada de uma casa isolada, atmosfera sombria.'}]}
    locations = rng.sample(['a estação desativada', 'o arquivo municipal', 'a ponte coberta', 'a escola antiga', 'o quarto da avó', 'a torre do relógio', 'o cemitério da colina', 'a casa do vigia', 'a sala de projeção', 'a capela sem sino'], 10)
    scenes = [{'text': f'Na primeira noite em {town}, {name} ouviu a própria voz do outro lado da janela. A voz dizia apenas uma coisa: não procure o quarto que falta. Ela acabara de chegar para organizar os documentos deixados pela avó. Na sala, havia onze chaves e uma planta da casa com doze portas. A porta ausente no corredor não estava escondida por um móvel. No lugar dela existia uma parede lisa, fria demais para aquela noite de verão. Quando {name} encostou a mão no reboco, sentiu alguém encostar a mão do outro lado.', 'visual': f'Casa antiga isolada em {town}, floresta noturna, uma janela iluminada, sem texto.'}]
    clues = ['uma fotografia sem rostos', 'um bilhete dobrado em quatro', 'uma fita com a sua voz', 'um mapa desenhado na parede', 'um livro de nomes apagados', 'uma chave ainda quente', 'um retrato da avó quando jovem', 'uma caixa cheia de relógios', 'um caderno com páginas costuradas', 'um envelope destinado a ela']
    for i, (place, clue) in enumerate(zip(locations, clues)):
        text = f'Na manhã seguinte, {name} foi até {place}. Encontrou {clue}, exatamente onde a avó havia indicado numa carta. '
        text += [
            'O zelador não quis falar sobre a casa. Apenas virou o espelho da entrada contra a parede e pediu que ela saísse antes de escurecer. Na fotografia guardada no balcão, a casa aparecia cercada por pessoas de costas. Uma delas usava o mesmo casaco que ela vestia. No verso, a data correspondia ao dia seguinte. Ela conferiu duas vezes. O zelador já havia desaparecido, deixando no chão pegadas molhadas que terminavam diante do espelho.',
            f'Na margem do papel estava escrito o horário: {hour}. Ela reconheceu a caligrafia da mãe, morta antes de poder ensinar a filha a escrever. Mais abaixo, uma lista descrevia pequenos acidentes que ainda não tinham acontecido. Um copo quebrado. Uma lâmpada queimada. A ligação de um desconhecido. Quando o telefone tocou, ela decidiu não atender. Mesmo assim, ouviu a voz no aparelho desligado: você sempre chega até esta parte.',
            'Havia uma cadeira virada para a parede. Sobre o assento, uma fina camada de poeira desenhava o contorno de duas mãos. Ela fotografou tudo, mas a tela mostrou uma pessoa sentada ali. Não era um fantasma transparente. Era alguém de carne e osso, de olhos fechados, prendendo a respiração. Ao ampliar a imagem, ela reconheceu uma cicatriz no queixo. Era a mesma que carregava desde a infância. A figura abriu os olhos na fotografia.',
            'Uma gravação começou a tocar sem que ela apertasse nenhum botão. A avó explicava que a casa não guardava pessoas. Guardava decisões que ninguém conseguira tomar. Cada porta levava a uma vida abandonada. O quarto que faltava tinha sido fechado com um nome, e não com uma chave. Quando a gravação terminou, surgiu outra voz, quase infantil, pedindo que ela voltasse para casa. Ao fundo, alguém contava passos. Eram os passos que ela dava naquele instante.',
            'Ela encontrou um funcionário que parecia esperar por sua chegada. Ele entregou uma folha em branco e pediu que escrevesse a primeira lembrança da infância. Ela escreveu sobre um aniversário. As letras desapareceram antes de a tinta secar. O homem explicou que aquela lembrança não era dela. Na janela, um reflexo sorria sem acompanhar seu rosto. Pela primeira vez, ela teve medo de perguntar quem era. Recolheu a folha e viu surgir uma frase: escolha uma lembrança verdadeira.',
            'A chuva começou de repente. Debaixo da escada, ela ouviu duas pessoas conversando sobre uma menina que precisara ser escondida do próprio reflexo. Reconheceu a voz da avó e outra, muito parecida com a sua. Quando abriu a portinhola, encontrou somente uma mesa posta para três. A comida ainda soltava vapor. No terceiro prato, alguém havia colocado uma chave feita de sal. Ao tocá-la, ela lembrou de uma porta vermelha que nunca tinha visto acordada.',
            'O lugar estava vazio, mas as luzes se acendiam alguns metros à sua frente, como se alguém a guiasse. Na última sala havia um registro de desaparecidos. Todos tinham o mesmo sobrenome da avó. Nenhum corpo fora encontrado. Ao lado de cada nome aparecia uma palavra: devolvido. A última linha estava incompleta. Ela reconheceu o próprio nome e percebeu que a tinta ainda estava fresca. Atrás da porta, uma caneta continuava riscando o papel sozinha.',
            'Ela tentou deixar a cidade pela estrada principal. Depois de meia hora, passou novamente pelo mesmo lugar. Não era apenas uma curva parecida. O mesmo cachorro dormia sob a mesma placa quebrada. Dessa vez, porém, a placa trazia uma mensagem que não estava ali antes. Dizia que ninguém podia sair levando duas versões de si. No banco traseiro, o cinto de segurança se esticou lentamente, como se alguém invisível acabasse de se acomodar.',
            'Na parte de trás do documento havia uma instrução simples: devolva o que foi tomado. Ela compreendeu por que a avó evitava espelhos e nunca deixava uma cadeira vazia à mesa. Quando era criança, alguém escolhera que a versão feliz da menina continuasse vivendo. A outra ficara presa no quarto ausente, carregando todas as perdas. Aquela voz na janela não queria entrar para matá-la. Queria que ela lembrasse do acordo que fizera para esquecê-la.',
            'Ela finalmente ouviu a história inteira. A avó não havia criado o quarto para esconder um monstro. Tentara salvar a neta de uma febre, separando dela a parte que sofria. Mas nenhuma vida podia permanecer inteira desse modo. A parede começara a falhar no dia do enterro. A menina do outro lado crescera sozinha, recebendo cada tristeza que a neta não conseguia sentir. Agora pedia apenas que alguém a chamasse pelo nome, sem negar sua existência.'
        ][i]
        scenes.append({'text': text, 'visual': f'{place.capitalize()} em {town}, {clue}, terror psicológico cinematográfico, noite, neblina, personagem {name}, sem texto.'})
    scenes.append({'text': f'Às {hour}, {name} voltou para o corredor. Não levou nenhuma chave. Sentou no chão e contou à parede a primeira lembrança que sabia ser verdadeira: a avó chorando na cozinha enquanto ela ria sem motivo. Pela primeira vez, permitiu que aquela tristeza a alcançasse. Do outro lado, alguém parou de bater. A parede abriu uma fresta, revelando um quarto comum, com uma cama pequena e uma janela fechada. Ela chamou a menina pelo próprio nome. Ao amanhecer, havia apenas onze portas na casa. Na última fotografia da avó, todas as pessoas tinham rosto. Menos a mulher que segurava a câmera.', 'visual': 'Corredor de casa antiga, porta entreaberta, luz vermelha e sombras, desfecho misterioso.'})
    return {'title': f'O quarto que faltava em {town}', 'scenes': scenes}


def validate_story(story: dict, full: bool = False) -> dict:
    if not isinstance(story.get('title'), str) or not 3 <= len(story['title']) <= 140:
        raise ValueError('Título inválido no roteiro.')
    scenes = story.get('scenes')
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 30:
        raise ValueError('O roteiro precisa de 1 a 30 cenas.')
    for scene in scenes:
        if not isinstance(scene.get('text'), str) or not 10 <= len(scene['text']) <= 5000 or not isinstance(scene.get('visual'), str):
            raise ValueError('Cada cena precisa de text e visual válidos.')
    words = sum(len(s['text'].split()) for s in scenes)
    if full and not 1000 <= words <= 1700:
        raise ValueError(f'Roteiro tem {words} palavras; use 1000–1700 para aproximadamente 8–12 minutos.')
    return story


def ollama_story(config: dict) -> dict:
    prompt = ('Crie uma história original de terror psicológico em português brasileiro com 1100 a 1450 palavras, '
              '12 cenas, personagens e acontecimentos próprios, começo impactante, tensão crescente e final completo. '
              'Responda apenas JSON com title e scenes, cada cena com text (narração) e visual (prompt de imagem). Sem markdown.')
    body = json.dumps({'model':config['ollama_model'], 'prompt':prompt, 'stream':False, 'format':'json', 'options':{'temperature':0.9}}).encode()
    url = config['ollama_url'].rstrip('/') + '/api/generate'
    from urllib.parse import urlparse
    if urlparse(url).hostname not in ('localhost','127.0.0.1','::1'):
        raise ValueError('Ollama deve ser local nesta versão gratuita.')
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers={'Content-Type':'application/json'}), timeout=900) as response:
        result = json.load(response)
    return validate_story(json.loads(result['response']), full=True)

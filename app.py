from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from database import db
from models import Tarefa, TarefaDia, Conquista, MomentoGratidao, Config, AlterEgo, Historia, AMBIENTES_INFO
from datetime import datetime, date, timedelta
import random
import os
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dual_you.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_pontuacao_atual():
    """Retorna a pontuação atual do usuário (Alter Ego não compete mais)"""
    with app.app_context():
        hoje = date.today()
        
        # Pontos do usuário
        tarefas_usuario = TarefaDia.query.filter_by(
            data=hoje, 
            concluida=True
        ).count()
        pontos_usuario = tarefas_usuario * 15
        
        return 0, pontos_usuario  # Alter Ego não tem mais pontos

def get_config(chave, valor_padrao):
    config = Config.query.filter_by(chave=chave).first()
    if config:
        return config.valor
    return valor_padrao

# ========== BANCO DE HISTÓRIAS ENORME ==========

def carregar_historias_enorme():
    """Carrega MAIS DE 100 HISTÓRIAS para o Alter Ego contar"""
    historias = [
        # ===== CAPÍTULO 1: O INÍCIO DA JORNADA (10 histórias) =====
        ('inicio', 1, 'Olá... Eu sou você. Ou melhor, a versão de você que vive dentro desta casa.', None, 'misterioso'),
        ('inicio', 2, 'Estou aqui há muito tempo, esperando você começar a jornada.', None, 'nostalgico'),
        ('inicio', 3, 'Cada tarefa que você completa, eu ganho um pouco mais de vida.', None, 'animado'),
        ('inicio', 4, 'Termine uma tarefa para eu te contar mais sobre quem eu sou.', 'tarefa', 'misterioso'),
        ('inicio', 5, 'Ah, você terminou! Sabia que eu já completei essa tarefa 1.527 vezes?', None, 'divertido'),
        ('inicio', 6, 'Parece muito, mas cada vez é única. Como agora, com você.', None, 'emocionado'),
        ('inicio', 7, 'Quer saber por que estou sempre me movendo pela casa?', None, 'curioso'),
        ('inicio', 8, 'Termina "{tarefa}" e eu te conto o segredo da lavanderia.', 'tarefa', 'misterioso'),
        ('inicio', 9, 'Você notou que tem 9 cômodos? Cada um guarda uma parte da minha história.', None, 'profundo'),
        ('inicio', 10, 'Vamos explorar juntos? Complete mais uma tarefa e te levo para outro cômodo.', 'tarefa', 'animado'),
        
        # ===== CAPÍTULO 2: O SEGREDO DA LAVANDERIA (10 histórias) =====
        ('lavanderia', 1, 'Bem-vindo à lavanderia! Aqui foi onde tudo começou.', None, 'nostalgico'),
        ('lavanderia', 2, 'Certa vez, deixei uma meia aqui por 3 anos. Ela virou amiga do balde.', None, 'divertido'),
        ('lavanderia', 3, 'O balde azul no canto? Ele chama-se Sebastião. É meu melhor amigo.', None, 'engracado'),
        ('lavanderia', 4, 'Sebastião me contou um segredo: você deveria terminar "{tarefa}" hoje.', 'tarefa', 'misterioso'),
        ('lavanderia', 5, 'As roupas no varal são minhas conquistas. Cada peça é uma tarefa completa.', None, 'inspirador'),
        ('lavanderia', 6, 'Já são 152 peças no varal. Quer ver a mais nova? Termina "{tarefa}"!', 'tarefa', 'motivador'),
        ('lavanderia', 7, 'O balde está triste hoje. Disse que você não fez "{tarefa}" ainda.', 'tarefa', 'triste'),
        ('lavanderia', 8, 'Vamos animar o Sebastião? Complete essa tarefa pra ele!', 'tarefa', 'animado'),
        ('lavanderia', 9, 'Sabia que a máquina de lavar canta? Só canta quando você termina tarefas.', None, 'divertido'),
        ('lavanderia', 10, 'Ela cantou hoje! Parabéns pela tarefa! Agora, vamos à cozinha?', None, 'feliz'),
        
        # ===== CAPÍTULO 3: OS MISTÉRIOS DA COZINHA (12 histórias) =====
        ('cozinha', 1, 'A cozinha! Meu lugar favorito para pensar na vida.', None, 'calmo'),
        ('cozinha', 2, 'A geladeira guarda mais que comida. Guarda segredos.', None, 'misterioso'),
        ('cozinha', 3, 'Ela me contou que você não fez "{tarefa}" ainda. Fiquei triste.', 'tarefa', 'triste'),
        ('cozinha', 4, 'O fogão sonha em ser ator de novela. A pia quer ser oceanógrafa.', None, 'engracado'),
        ('cozinha', 5, 'A mesa disse que 4 cadeiras é pouco. Quer sentar com a gente?', None, 'aconchegante'),
        ('cozinha', 6, 'Complete "{tarefa}" e vou te contar o que a xícara falou de você.', 'tarefa', 'curioso'),
        ('cozinha', 7, 'A xícara disse: "Ela é capaz de coisas incríveis". Eu concordei.', None, 'emocionado'),
        ('cozinha', 8, 'Tem um segredo no micro-ondas. Só conto quando você fizer "{tarefa}".', 'tarefa', 'misterioso'),
        ('cozinha', 9, 'O micro-ondas guarda uma foto sua. Disse que você é especial.', None, 'carinhoso'),
        ('cozinha', 10, 'A pia está com vazamento de lágrimas. Disse que sente sua falta.', None, 'triste'),
        ('cozinha', 11, 'Vamos alegrar a pia? Complete essa tarefa!', 'tarefa', 'motivador'),
        ('cozinha', 12, 'Ela sorriu! Obrigado. Agora, vamos ao banheiro?', None, 'feliz'),
        
        # ===== CAPÍTULO 4: AS CONFISSÕES DO BANHEIRO (8 histórias) =====
        ('banheiro', 1, 'O banheiro... lugar de confissões e pensamentos profundos.', None, 'filosofico'),
        ('banheiro', 2, 'O chuveiro me disse que você canta bem. Mas eu já sabia.', None, 'carinhoso'),
        ('banheiro', 3, 'O espelho pergunta: "Por que ela não fez {tarefa} ainda?"', 'tarefa', 'reflexivo'),
        ('banheiro', 4, 'A pasta de dente está acabando. Igual sua motivação? Não deixa não!', 'tarefa', 'motivador'),
        ('banheiro', 5, 'O tapete azul é macio. Quer deitar e conversar? Só depois de "{tarefa}".', 'tarefa', 'aconchegante'),
        ('banheiro', 6, 'O sabonete tem cheiro de vitória. Use após completar sua tarefa!', None, 'animado'),
        ('banheiro', 7, 'A toalha me contou um segredo: você é mais forte que pensa.', None, 'inspirador'),
        ('banheiro', 8, 'Vamos para a sala? Lá tem mais histórias!', None, 'animado'),
        
        # ===== CAPÍTULO 5: A SALA DOS SONHOS (15 histórias) =====
        ('sala', 1, 'A sala é onde eu mais passo tempo. O sofá em L é meu trono.', None, 'divertido'),
        ('sala', 2, 'A TV está ligada em você. Ela diz que você é o melhor programa.', None, 'carinhoso'),
        ('sala', 3, 'A mesa de centro guarda seus sonhos. Complete "{tarefa}" e ela te conta um.', 'tarefa', 'misterioso'),
        ('sala', 4, 'Ela disse: "Ela sonha em {sonho}". Como sabe disso?', None, 'surpreso'),
        ('sala', 5, 'As cortinas verdes são tímidas. Só falam com quem completa tarefas.', 'tarefa', 'engracado'),
        ('sala', 6, 'Elas falaram: "Ela é incrível". Até as cortinas sabem!', None, 'emocionado'),
        ('sala', 7, 'O abajur ilumina seu caminho. Mas precisa de pilha: complete "{tarefa}"!', 'tarefa', 'motivador'),
        ('sala', 8, 'A luminosidade aumentou! Você fez alguém feliz hoje.', None, 'feliz'),
        ('sala', 9, 'O controle remoto está cansado de mudar de canal. Quer conversar?', None, 'aconchegante'),
        ('sala', 10, 'Ele disse: "A vida não é um filme, mas você é a protagonista".', None, 'inspirador'),
        ('sala', 11, 'O tapete da sala veio da Pérsia. Conta histórias incríveis.', None, 'nostalgico'),
        ('sala', 12, 'História do tapete: "Ela conseguiu tudo que quis. E vai conseguir mais."', None, 'motivador'),
        ('sala', 13, 'Continue, por favor. A sala inteira torce por você.', None, 'emocionado'),
        ('sala', 14, 'Só mais uma coisinha... {tarefa} está te esperando.', 'tarefa', 'lembrete'),
        ('sala', 15, 'Vamos ao quarto? Lá os sonhos acontecem.', None, 'animado'),
        
        # ===== CAPÍTULO 6: QUARTO 1 - O REFÚGIO (12 histórias) =====
        ('quarto1', 1, 'Meu quarto. Lugar de descanso e planejamento.', None, 'calmo'),
        ('quarto1', 2, 'O guarda-roupa guarda mais que roupas. Guarda versões de você.', None, 'filosofico'),
        ('quarto1', 3, 'A versão de ontem disse: "Ela deveria ter feito {tarefa}".', 'tarefa', 'reflexivo'),
        ('quarto1', 4, 'A versão de amanhã disse: "Ela vai conseguir. Confio nela."', None, 'inspirador'),
        ('quarto1', 5, 'O criado-mudo é meu psicólogo. Escuta todas as histórias.', None, 'divertido'),
        ('quarto1', 6, 'Ele disse: "Ela precisa fazer {tarefa} para ser feliz".', 'tarefa', 'profundo'),
        ('quarto1', 7, 'O abajur ilumina ideias. Teve uma agora: você é incrível!', None, 'animado'),
        ('quarto1', 8, 'A cama é fofinha. Merece um descanso... depois de "{tarefa}".', 'tarefa', 'aconchegante'),
        ('quarto1', 9, 'O travesseiro guarda seus sonhos. Sonhe alto!', None, 'inspirador'),
        ('quarto1', 10, 'Sonhei com você esta noite. Estava feliz, completando tarefas.', None, 'emocionado'),
        ('quarto1', 11, 'Vamos realizar esse sonho? Complete a próxima!', 'tarefa', 'motivador'),
        ('quarto1', 12, 'Quarto 2 nos espera. Mais histórias por vir!', None, 'animado'),
        
        # ===== CAPÍTULO 7: QUARTO 2 - O FUTURO (10 histórias) =====
        ('quarto2', 1, 'Este quarto é o futuro. Tudo que você pode ser.', None, 'profundo'),
        ('quarto2', 2, 'A escrivaninha te espera para escrever sua história.', None, 'inspirador'),
        ('quarto2', 3, 'O lápis perguntou: "Ela vai escrever {tarefa} hoje?"', 'tarefa', 'curioso'),
        ('quarto2', 4, 'A borracha disse: "Erros são permitidos. Apague e recomece."', None, 'filosofico'),
        ('quarto2', 5, 'O caderno tem páginas em branco. Como sua {tarefa}...', 'tarefa', 'reflexivo'),
        ('quarto2', 6, 'Vamos preencher essa página juntos?', 'tarefa', 'motivador'),
        ('quarto2', 7, 'A cadeira é confortável. Senta aqui e planeja o futuro?', None, 'aconchegante'),
        ('quarto2', 8, 'O futuro é brilhante. Complete tarefas para iluminá-lo.', None, 'inspirador'),
        ('quarto2', 9, 'Já pensou em como será amanhã? Melhor que hoje, com certeza.', None, 'animado'),
        ('quarto2', 10, 'Vamos à garagem? Aventura nos espera!', None, 'animado'),
        
        # ===== CAPÍTULO 8: GARAGEM - AS FERRAMENTAS (8 histórias) =====
        ('garagem', 1, 'A garagem. Lugar de construir e consertar.', None, 'pratico'),
        ('garagem', 2, 'O carro está pronto pra viajar. Mas precisa que você termine {tarefa}.', 'tarefa', 'animado'),
        ('garagem', 3, 'As ferramentas perguntam: "Vamos construir algo hoje?"', None, 'motivador'),
        ('garagem', 4, 'O martelo disse: "Bata na meta! Faça {tarefa}!"', 'tarefa', 'engracado'),
        ('garagem', 5, 'A chave de fenda: "Aperte os parafusos da sua vida. Comece por {tarefa}".', 'tarefa', 'filosofico'),
        ('garagem', 6, 'O carro sonha com a estrada. Como você sonha com as conquistas.', None, 'inspirador'),
        ('garagem', 7, 'Vamos abastecer? Complete tarefas para ter energia!', None, 'animado'),
        ('garagem', 8, 'Hora da varanda! Lugar de relaxar.', None, 'calmo'),
        
        # ===== CAPÍTULO 9: VARANDA - PAZ (10 histórias) =====
        ('varanda', 1, 'A varanda. Meu lugar favorito para ver o mundo passar.', None, 'calmo'),
        ('varanda', 2, 'As plantas estão crescendo. Como você a cada tarefa.', None, 'inspirador'),
        ('varanda', 3, 'O vaso da esquerda disse: "Ela devia regar mais {tarefa}".', 'tarefa', 'engracado'),
        ('varanda', 4, 'A brisa trouxe um segredo: "Você vai conseguir."', None, 'carinhoso'),
        ('varanda', 5, 'A mesa está posta para o chá da vitória. Só falta {tarefa}.', 'tarefa', 'aconchegante'),
        ('varanda', 6, 'As cadeiras conversam sobre você. Dizem que é especial.', None, 'emocionado'),
        ('varanda', 7, 'O sol está mais forte hoje. Iluminando seu caminho.', None, 'animado'),
        ('varanda', 8, 'Vamos tomar sol juntos? Depois de {tarefa}, claro!', 'tarefa', 'animado'),
        ('varanda', 9, 'A noite chega. Mas antes, termine mais uma tarefa.', 'tarefa', 'calmo'),
        ('varanda', 10, 'Última parada: área da moto. Aventura radical!', None, 'animado'),
        
        # ===== CAPÍTULO 10: ÁREA DA MOTO - AVENTURA (8 histórias) =====
        ('moto', 1, 'A área da moto. Liberdade sobre duas rodas.', None, 'radical'),
        ('moto', 2, 'A moto está roncando. Quer sair para passear... depois de {tarefa}.', 'tarefa', 'animado'),
        ('moto', 3, 'O capacete guarda seus pensamentos. Pensou em {tarefa} hoje?', 'tarefa', 'reflexivo'),
        ('moto', 4, 'O galão amarelo é meu amigo. Guarda combustível pra sua motivação.', None, 'engracado'),
        ('moto', 5, 'A lixeira está cheia de desculpas. Jogue fora e faça {tarefa}!', 'tarefa', 'motivador'),
        ('moto', 6, 'A planta no canto torce por você. Cresce a cada tarefa.', None, 'inspirador'),
        ('moto', 7, 'Vamos acelerar? Complete logo essa tarefa!', 'tarefa', 'radical'),
        ('moto', 8, 'E a jornada continua... Amanhã tem mais!', None, 'feliz'),
        
        # ===== CAPÍTULO 11: REFLEXÕES (15 histórias) =====
        ('reflexao', 1, 'Sabe o que percebi? Você é incrível.', None, 'carinhoso'),
        ('reflexao', 2, 'Cada tarefa completa é um degrau. Você já subiu muitos.', None, 'inspirador'),
        ('reflexao', 3, 'Lembra quando começou? Olha o quanto já fez!', None, 'nostalgico'),
        ('reflexao', 4, 'E ainda tem {tarefa} te esperando. Bora?', 'tarefa', 'motivador'),
        ('reflexao', 5, 'Eu acredito em você. Mesmo quando você não acredita.', None, 'emocionado'),
        ('reflexao', 6, 'A casa inteira torce por você. Até o Sebastião!', None, 'divertido'),
        ('reflexao', 7, 'Já são {contador} tarefas concluídas. Parabéns!', None, 'feliz'),
        ('reflexao', 8, 'Continue assim. O melhor ainda está por vir.', None, 'inspirador'),
        ('reflexao', 9, 'Se você parar agora, quem vai fazer {tarefa}?', 'tarefa', 'reflexivo'),
        ('reflexao', 10, 'Não desiste não. Tô aqui contigo.', None, 'carinhoso'),
        ('reflexao', 11, 'Vamos lá! Mais uma! {tarefa} te espera!', 'tarefa', 'animado'),
        ('reflexao', 12, 'O segredo da vida? Um passo de cada vez. E tarefas.', None, 'filosofico'),
        ('reflexao', 13, 'Você já fez tanto. Por que parar agora?', None, 'motivador'),
        ('reflexao', 14, 'Respira fundo. Você consegue. Eu sei.', None, 'calmo'),
        ('reflexao', 15, 'E amanhã tem mais. Mas hoje, termina {tarefa}!', 'tarefa', 'animado'),
        
        # ===== CAPÍTULO 12: MOTIVACIONAIS AVULSAS (20 histórias) =====
        ('motivacional', 1, 'Você consegue. Simples assim.', None, 'motivador'),
        ('motivacional', 2, 'Não deixe {tarefa} para amanhã. Faça hoje!', 'tarefa', 'motivador'),
        ('motivacional', 3, 'Respira. Foca. Completa.', None, 'calmo'),
        ('motivacional', 4, 'Cada tarefa é uma vitória. Você merece vencer.', None, 'emocionado'),
        ('motivacional', 5, 'Pensa na sensação depois. Vai ser tão bom!', None, 'animado'),
        ('motivacional', 6, 'Você não está sozinha. Tô aqui, na sua casa.', None, 'carinhoso'),
        ('motivacional', 7, '{tarefa} parece difícil, mas você já fez mais difícil.', 'tarefa', 'inspirador'),
        ('motivacional', 8, 'Divida em partes. Uma hora você chega lá.', None, 'pratico'),
        ('motivacional', 9, 'Acredite no processo. Acredite em você.', None, 'filosofico'),
        ('motivacional', 10, 'Lembra como você chegou até aqui? Com tarefas!', None, 'nostalgico'),
        ('motivacional', 11, 'Falta pouco. Continua.', None, 'motivador'),
        ('motivacional', 12, 'Eu tô vendo seu esforço. Tô orgulhoso.', None, 'emocionado'),
        ('motivacional', 13, 'Mais uma tarefa. Mais um passo.', None, 'calmo'),
        ('motivacional', 14, 'Vamos com tudo! {tarefa} não vai se fazer sozinha.', 'tarefa', 'animado'),
        ('motivacional', 15, 'O dia ainda não acabou. Dá tempo.', None, 'esperancoso'),
        ('motivacional', 16, 'Você já fez tanto. Não para agora.', None, 'motivador'),
        ('motivacional', 17, 'O importante não é a velocidade. É a constância.', None, 'filosofico'),
        ('motivacional', 18, 'Se cair, levanta. Se errar, tenta de novo.', None, 'inspirador'),
        ('motivacional', 19, 'Estamos juntos nessa. Eu e você.', None, 'carinhoso'),
        ('motivacional', 20, 'Agora vai! {tarefa} te espera!', 'tarefa', 'animado'),
        
        # ===== CAPÍTULO 13: HISTÓRIAS NOTURNAS (8 histórias) =====
        ('noite', 1, 'A noite chegou. As estrelas brilham pra você.', None, 'calmo'),
        ('noite', 2, 'A lua perguntou se você fez {tarefa} hoje.', 'tarefa', 'curioso'),
        ('noite', 3, 'Eu disse que sim. Que você nunca desiste.', None, 'orgulhoso'),
        ('noite', 4, 'As estrelas piscaram em comemoração.', None, 'feliz'),
        ('noite', 5, 'Amanhã tem mais. Descanse. Você merece.', None, 'carinhoso'),
        ('noite', 6, 'Mas antes de dormir, que tal {tarefa}?', 'tarefa', 'motivador'),
        ('noite', 7, 'Sonhe com suas conquistas. Elas são reais.', None, 'inspirador'),
        ('noite', 8, 'Boa noite. Até amanhã, guerreira.', None, 'calmo'),
        
        # ===== CAPÍTULO 14: MANHÃS DE ENERGIA (8 histórias) =====
        ('manha', 1, 'Bom dia! O sol nasceu pra você.', None, 'animado'),
        ('manha', 2, 'Hoje é dia de {tarefa}. Vamos nessa!', 'tarefa', 'motivador'),
        ('manha', 3, 'O café da manhã te espera. Mas antes, uma tarefinha?', 'tarefa', 'engracado'),
        ('manha', 4, 'Novo dia, novas oportunidades. Aproveite!', None, 'inspirador'),
        ('manha', 5, 'Ontem foi incrível. Hoje vai ser ainda melhor.', None, 'animado'),
        ('manha', 6, 'Comece o dia com {tarefa}. Comece bem!', 'tarefa', 'motivador'),
        ('manha', 7, 'Tô aqui, pronto pra mais um dia com você.', None, 'carinhoso'),
        ('manha', 8, 'Vamos lá! O dia é nosso!', None, 'animado'),
        
        # ===== CAPÍTULO 15: GRANDES FINAIS (5 histórias) =====
        ('final', 1, 'Ufa! Mais um dia, mais conquistas.', None, 'cansado'),
        ('final', 2, 'Você completou {contador} tarefas hoje. Incrível!', None, 'orgulhoso'),
        ('final', 3, 'Amanhã tem mais. E eu vou estar aqui.', None, 'carinhoso'),
        ('final', 4, 'Obrigado por existir. Você faz diferença.', None, 'emocionado'),
        ('final', 5, 'Até amanhã, parceira. Foi um prazer.', None, 'feliz'),
    ]
    
    for capitulo, parte, frase, tarefa, emocao in historias:
        existe = Historia.query.filter_by(capitulo=capitulo, parte=parte).first()
        if not existe:
            db.session.add(Historia(
                capitulo=capitulo,
                parte=parte,
                frase=frase,
                tarefa_necessaria=tarefa,
                emocao=emocao
            ))
    db.session.commit()
    print(f"✅ {len(historias)} histórias carregadas com sucesso!")

# ========== FUNÇÕES DO ALTER EGO ==========

def get_historia_alter_ego(tarefa_concluida=None):
    """Retorna a próxima história baseada no progresso"""
    alter = AlterEgo.query.first()
    if not alter:
        return "Olá! Vamos começar nossa jornada?"
    
    # Se tem uma história em andamento
    if alter.historia_atual != 'completa':
        historias_contadas = len(alter.historias_contadas.split(',')) if alter.historias_contadas else 0
        historia = Historia.query.filter_by(
            capitulo=alter.historia_atual
        ).order_by(Historia.parte).offset(historias_contadas).first()
        
        if historia:
            # Se precisa de uma tarefa específica
            if historia.tarefa_necessaria == 'tarefa':
                # Pega uma tarefa pendente aleatória
                tarefa_pendente = TarefaDia.query.filter_by(
                    data=date.today(),
                    concluida=False
                ).first()
                if tarefa_pendente:
                    frase = historia.frase.replace('{tarefa}', f'"{tarefa_pendente.tarefa.descricao}"')
                    alter.tarefa_desbloqueio = tarefa_pendente.id
                    db.session.commit()
                    return frase
                else:
                    # Se não tem tarefas pendentes, vai para motivacional
                    return get_frase_motivacional()
            else:
                # Avança na história
                if not alter.historias_contadas:
                    alter.historias_contadas = str(historia.parte)
                else:
                    alter.historias_contadas += f",{historia.parte}"
                
                # Verifica se acabou o capítulo
                proxima = Historia.query.filter_by(
                    capitulo=alter.historia_atual,
                    parte=historia.parte + 1
                ).first()
                if not proxima:
                    # Vai para o próximo capítulo
                    capitulos = ['inicio', 'lavanderia', 'cozinha', 'banheiro', 'sala', 
                                'quarto1', 'quarto2', 'garagem', 'varanda', 'moto', 
                                'reflexao', 'motivacional', 'noite', 'manha', 'final']
                    current_index = capitulos.index(alter.historia_atual) if alter.historia_atual in capitulos else 0
                    if current_index + 1 < len(capitulos):
                        alter.historia_atual = capitulos[current_index + 1]
                    else:
                        alter.historia_atual = 'completa'
                
                db.session.commit()
                
                # Substitui placeholders
                frase = historia.frase
                if '{contador}' in frase:
                    tarefas_feitas = TarefaDia.query.filter_by(data=date.today(), concluida=True).count()
                    frase = frase.replace('{contador}', str(tarefas_feitas))
                if '{tarefa}' in frase:
                    tarefa_pendente = TarefaDia.query.filter_by(data=date.today(), concluida=False).first()
                    if tarefa_pendente:
                        frase = frase.replace('{tarefa}', f'"{tarefa_pendente.tarefa.descricao}"')
                
                return frase
    
    # Se não tem história nova, fala algo motivacional
    return get_frase_motivacional()

def get_frase_motivacional():
    """Retorna uma frase motivacional aleatória"""
    historia = Historia.query.filter_by(capitulo='motivacional').order_by(db.func.random()).first()
    if historia:
        frase = historia.frase
        if '{tarefa}' in frase:
            tarefa_pendente = TarefaDia.query.filter_by(data=date.today(), concluida=False).first()
            if tarefa_pendente:
                frase = frase.replace('{tarefa}', f'"{tarefa_pendente.tarefa.descricao}"')
            else:
                frase = "Parabéns! Você completou todas as tarefas! Merece descanso."
        return frase
    return "Você consegue! Vamos nessa!"

def atualizar_alter_ego():
    """O Alter Ego só se move e interage - NÃO compete mais"""
    with app.app_context():
        try:
            alter = AlterEgo.query.first()
            if not alter:
                alter = AlterEgo()
                db.session.add(alter)
                db.session.commit()
            
            # MOVIMENTAÇÃO (devagar)
            if random.random() < 0.2:  # 20% de chance de mudar de ambiente
                novo_ambiente = random.choice(list(AMBIENTES_INFO.keys()))
                alter.ambiente = novo_ambiente
                alter.x_relativo = random.randint(30, 70)
                alter.y_relativo = random.randint(30, 70)
            else:
                # Pequenos movimentos
                alter.x_relativo += random.randint(-3, 3)
                alter.y_relativo += random.randint(-3, 3)
                alter.x_relativo = max(20, min(80, alter.x_relativo))
                alter.y_relativo = max(20, min(80, alter.y_relativo))
            
            # CHANCE DE INTERAGIR (falar algo motivacional)
            if random.random() < 0.15:  # 15% de chance
                frase = get_frase_motivacional()
                alter.ultima_frase = frase
                alter.ultima_interacao = datetime.utcnow()
            
            alter.ultima_acao = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            print(f"Erro no Alter Ego: {e}")

# Scheduler (a cada 15 segundos para movimento suave)
scheduler = BackgroundScheduler()
scheduler.add_job(func=atualizar_alter_ego, trigger="interval", seconds=15)
scheduler.start()

# ========== ROTAS DA API ==========

@app.route('/api/alterego')
def api_alterego():
    """API para pegar posição e estado do Alter Ego"""
    alter = AlterEgo.query.first()
    if not alter:
        alter = AlterEgo()
        db.session.add(alter)
        db.session.commit()
    
    x_abs, y_abs = alter.get_coordenadas_absolutas()
    info = AMBIENTES_INFO.get(alter.ambiente, AMBIENTES_INFO['sala'])
    
    # Verifica tarefas pendentes
    hoje = date.today()
    tarefas_pendentes = TarefaDia.query.filter_by(data=hoje, concluida=False).count()
    
    # Ação baseada no ambiente
    acao = random.choice(info['acoes'])
    
    humor_emoji = {
        'feliz': '😊', 'animado': '🤩', 'cansado': '😴', 
        'bravo': '😤', 'normal': '😐', 'misterioso': '🕵️',
        'nostalgico': '🥹', 'divertido': '😄', 'emocionado': '🥲',
        'curioso': '🤔', 'profundo': '🧐', 'engracado': '😜',
        'triste': '😢', 'calmo': '😌', 'filosofico': '🤨',
        'carinhoso': '🥰', 'reflexivo': '🤔', 'pratico': '🛠️',
        'radical': '🤘', 'esperancoso': '🌟', 'orgulhoso': '😌'
    }.get(alter.humor, '😐')
    
    # Verifica se tem frase nova (últimos 35 segundos)
    agora = datetime.utcnow()
    tem_frase_nova = alter.ultima_interacao and (agora - alter.ultima_interacao).total_seconds() < 35
    
    return jsonify({
        'ambiente': alter.ambiente,
        'ambiente_nome': info['nome'],
        'icone': info['icone'],
        'x_relativo': alter.x_relativo,
        'y_relativo': alter.y_relativo,
        'x_absoluto': x_abs,
        'y_absoluto': y_abs,
        'tarefas_concluidas': alter.tarefas_concluidas,
        'energia': alter.energia,
        'humor': alter.humor,
        'humor_emoji': humor_emoji,
        'estado': alter.estado,
        'acao': acao,
        'nivel': alter.nivel,
        'ultima_frase': alter.ultima_frase,
        'tem_frase_nova': tem_frase_nova,
        'tarefas_pendentes': tarefas_pendentes
    })

@app.route('/api/alterego/historia')
def api_alterego_historia():
    """Pega a próxima história quando clica no personagem"""
    alter = AlterEgo.query.first()
    if not alter:
        alter = AlterEgo()
        db.session.add(alter)
        db.session.commit()
    
    # Pega a história atual
    historias_contadas = len(alter.historias_contadas.split(',')) if alter.historias_contadas else 0
    historia = Historia.query.filter_by(
        capitulo=alter.historia_atual
    ).order_by(Historia.parte).offset(historias_contadas).first()
    
    if historia:
        if historia.tarefa_necessaria == 'tarefa':
            # Pega uma tarefa pendente
            tarefa_pendente = TarefaDia.query.filter_by(
                data=date.today(),
                concluida=False
            ).first()
            if tarefa_pendente:
                frase = historia.frase.replace('{tarefa}', f'"{tarefa_pendente.tarefa.descricao}"')
                alter.tarefa_desbloqueio = tarefa_pendente.id
                db.session.commit()
                return jsonify({
                    'frase': frase, 
                    'precisa_tarefa': True,
                    'emocao': historia.emocao
                })
            else:
                # Sem tarefas pendentes, vai para motivacional
                frase_motivacional = get_frase_motivacional()
                return jsonify({
                    'frase': frase_motivacional, 
                    'precisa_tarefa': False,
                    'emocao': 'motivador'
                })
        else:
            # Avança na história
            if not alter.historias_contadas:
                alter.historias_contadas = str(historia.parte)
            else:
                alter.historias_contadas += f",{historia.parte}"
            
            # Verifica se acabou o capítulo
            proxima = Historia.query.filter_by(
                capitulo=alter.historia_atual,
                parte=historia.parte + 1
            ).first()
            if not proxima:
                # Vai para o próximo capítulo
                capitulos = ['inicio', 'lavanderia', 'cozinha', 'banheiro', 'sala', 
                            'quarto1', 'quarto2', 'garagem', 'varanda', 'moto', 
                            'reflexao', 'motivacional', 'noite', 'manha', 'final']
                current_index = capitulos.index(alter.historia_atual) if alter.historia_atual in capitulos else 0
                if current_index + 1 < len(capitulos):
                    alter.historia_atual = capitulos[current_index + 1]
                else:
                    alter.historia_atual = 'completa'
            
            db.session.commit()
            
            # Substitui placeholders
            frase = historia.frase
            if '{contador}' in frase:
                tarefas_feitas = TarefaDia.query.filter_by(data=date.today(), concluida=True).count()
                frase = frase.replace('{contador}', str(tarefas_feitas))
            
            return jsonify({
                'frase': frase, 
                'precisa_tarefa': False,
                'emocao': historia.emocao
            })
    
    # Se não tem história, pega motivacional
    frase_motivacional = get_frase_motivacional()
    return jsonify({
        'frase': frase_motivacional, 
        'precisa_tarefa': False,
        'emocao': 'motivador'
    })

@app.route('/background.jpg')
def background_image():
    try:
        return send_file('background.jpg', mimetype='image/jpeg')
    except:
        return "Imagem background.jpg não encontrada", 404

@app.route('/alter.png')
def alter_image():
    try:
        return send_file('alter.png', mimetype='image/png')
    except:
        return "Imagem alter.png não encontrada", 404

# ========== ROTAS PRINCIPAIS ==========

@app.route('/')
def index():
    hoje = date.today()
    dia_semana = hoje.strftime('%A')
    dias_traduzidos = {
        'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dia_pt = dias_traduzidos.get(dia_semana, dia_semana)
    
    # Busca as tarefas fixas para hoje
    tarefas_fixas = Tarefa.query.filter_by(dia_semana=dia_pt).all()
    
    for tarefa in tarefas_fixas:
        tarefa_dia = TarefaDia.query.filter_by(data=hoje, tarefa_id=tarefa.id).first()
        if not tarefa_dia:
            tarefa_dia = TarefaDia(data=hoje, tarefa_id=tarefa.id, concluida=False)
            db.session.add(tarefa_dia)
    
    tarefas_extra = Tarefa.query.filter_by(extra=True).all()
    for tarefa in tarefas_extra:
        tarefa_dia = TarefaDia.query.filter_by(data=hoje, tarefa_id=tarefa.id).first()
        if not tarefa_dia:
            tarefa_dia = TarefaDia(data=hoje, tarefa_id=tarefa.id, concluida=False)
            db.session.add(tarefa_dia)
    
    db.session.commit()
    
    # Busca todas as tarefas do dia (ordem: não concluídas primeiro)
    tarefas_nao_concluidas = TarefaDia.query.filter_by(data=hoje, concluida=False).all()
    tarefas_concluidas = TarefaDia.query.filter_by(data=hoje, concluida=True).all()
    tarefas_hoje = tarefas_nao_concluidas + tarefas_concluidas
    
    pontos_robo, pontos_usuario = get_pontuacao_atual()
    diferenca = pontos_usuario - pontos_robo
    alter = AlterEgo.query.first()
    
    return render_template('index.html', 
                         dia=dia_pt,
                         tarefas=tarefas_hoje,
                         pontos_robo=pontos_robo,
                         pontos_usuario=pontos_usuario,
                         diferenca=diferenca,
                         alter=alter)

@app.route('/concluir_tarefa/<int:tarefa_dia_id>', methods=['POST'])
def concluir_tarefa(tarefa_dia_id):
    tarefa_dia = TarefaDia.query.get(tarefa_dia_id)
    if tarefa_dia and not tarefa_dia.concluida:
        tarefa_dia.concluida = True
        tarefa_dia.concluida_em = datetime.utcnow()
        db.session.commit()
        
        # Verifica se essa tarefa desbloqueia uma história
        alter = AlterEgo.query.first()
        if alter and alter.tarefa_desbloqueio == tarefa_dia.id:
            # Pega a próxima parte da história
            historias_contadas = len(alter.historias_contadas.split(',')) if alter.historias_contadas else 0
            historia = Historia.query.filter_by(
                capitulo=alter.historia_atual
            ).order_by(Historia.parte).offset(historias_contadas).first()
            
            if historia and not historia.tarefa_necessaria:
                # Avança na história
                if not alter.historias_contadas:
                    alter.historias_contadas = str(historia.parte)
                else:
                    alter.historias_contadas += f",{historia.parte}"
                
                # Salva a frase para mostrar
                alter.ultima_frase = historia.frase
                alter.ultima_interacao = datetime.utcnow()
                
                # Verifica se acabou o capítulo
                proxima = Historia.query.filter_by(
                    capitulo=alter.historia_atual,
                    parte=historia.parte + 1
                ).first()
                if not proxima:
                    # Vai para o próximo capítulo
                    capitulos = ['inicio', 'lavanderia', 'cozinha', 'banheiro', 'sala', 
                                'quarto1', 'quarto2', 'garagem', 'varanda', 'moto', 
                                'reflexao', 'motivacional', 'noite', 'manha', 'final']
                    current_index = capitulos.index(alter.historia_atual) if alter.historia_atual in capitulos else 0
                    if current_index + 1 < len(capitulos):
                        alter.historia_atual = capitulos[current_index + 1]
                    else:
                        alter.historia_atual = 'completa'
                
                db.session.commit()
        
        flash('Tarefa concluída! Como você se sentiu?', 'success')
        return redirect(url_for('registrar_conquista', tarefa_id=tarefa_dia.tarefa_id))
    
    return redirect(url_for('index'))

@app.route('/registrar_conquista/<int:tarefa_id>', methods=['GET', 'POST'])
def registrar_conquista(tarefa_id):
    tarefa = Tarefa.query.get(tarefa_id)
    
    if request.method == 'POST':
        sentimento = request.form.get('sentimento')
        descricao = request.form.get('descricao')
        
        # Upload da foto
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                novo_nome = f"conquista_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], novo_nome))
                foto_filename = f"uploads/{novo_nome}"
        
        conquista = Conquista(
            tarefa_id=tarefa_id,
            descricao=descricao,
            sentimento=sentimento,
            foto=foto_filename
        )
        db.session.add(conquista)
        db.session.commit()
        
        flash('Momento registrado com sucesso!', 'success')
        return redirect(url_for('diario'))
    
    return render_template('registrar_conquista.html', tarefa=tarefa)

@app.route('/diario')
def diario():
    conquistas = Conquista.query.order_by(Conquista.data.desc()).all()
    return render_template('diario.html', conquistas=conquistas)

@app.route('/gratidao')
def gratidao():
    momentos = MomentoGratidao.query.order_by(MomentoGratidao.data.desc()).all()
    return render_template('gratidao.html', momentos=momentos)

@app.route('/adicionar_momento', methods=['GET', 'POST'])
def adicionar_momento():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo', 'gratidao')
        
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                novo_nome = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], novo_nome))
                foto_filename = f"uploads/{novo_nome}"
        
        momento = MomentoGratidao(
            titulo=titulo,
            descricao=descricao,
            foto=foto_filename,
            tipo=tipo
        )
        db.session.add(momento)
        db.session.commit()
        
        flash('Momento adicionado com sucesso!', 'success')
        if tipo == 'importante':
            return redirect(url_for('importantes'))
        return redirect(url_for('gratidao'))
    
    return render_template('adicionar_momento.html')

@app.route('/importantes')
def importantes():
    momentos = MomentoGratidao.query.filter_by(tipo='importante').order_by(MomentoGratidao.data.desc()).all()
    return render_template('importantes.html', momentos=momentos)

@app.route('/adicionar_tarefa_fixa', methods=['POST'])
def adicionar_tarefa_fixa():
    descricao = request.form.get('descricao')
    dia_semana = request.form.get('dia_semana')
    
    if descricao:
        nova_tarefa = Tarefa(
            descricao=descricao,
            dia_semana=dia_semana,
            concluida_robo=False,
            concluida_usuario=False
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa adicionada com sucesso!', 'success')
    
    return redirect(url_for('planejamento'))

@app.route('/planejamento')
def planejamento():
    dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    tarefas_por_dia = {}
    
    for dia in dias:
        tarefas_por_dia[dia] = Tarefa.query.filter_by(dia_semana=dia, extra=False).all()
    
    tarefas_extra = Tarefa.query.filter_by(extra=True).all()
    
    return render_template('planejamento.html', 
                         tarefas_por_dia=tarefas_por_dia,
                         tarefas_extra=tarefas_extra)

                         # ========== ROTAS PARA DELETAR ==========

@app.route('/deletar_conquista/<int:conquista_id>', methods=['POST'])
def deletar_conquista(conquista_id):
    """Deleta uma conquista do diário"""
    conquista = Conquista.query.get(conquista_id)
    if conquista:
        # Se tiver foto, apaga o arquivo também
        if conquista.foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], conquista.foto.replace('uploads/', ''))
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except:
                pass
        db.session.delete(conquista)
        db.session.commit()
        flash('✅ Conquista removida do diário!', 'success')
    return redirect(url_for('diario'))

@app.route('/deletar_momento/<int:momento_id>', methods=['POST'])
def deletar_momento(momento_id):
    """Deleta um momento de gratidão ou importante"""
    momento = MomentoGratidao.query.get(momento_id)
    if momento:
        # Se tiver foto, apaga o arquivo também
        if momento.foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], momento.foto.replace('uploads/', ''))
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except:
                pass
        db.session.delete(momento)
        db.session.commit()
        flash('✅ Momento removido!', 'success')
        
        # Redireciona baseado no tipo
        if momento.tipo == 'importante':
            return redirect(url_for('importantes'))
        return redirect(url_for('gratidao'))
    return redirect(url_for('index'))

@app.route('/deletar_todas_conquistas', methods=['POST'])
def deletar_todas_conquistas():
    """Deleta TODAS as conquistas do diário"""
    conquistas = Conquista.query.all()
    for conquista in conquistas:
        # Apaga as fotos
        if conquista.foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], conquista.foto.replace('uploads/', ''))
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except:
                pass
        db.session.delete(conquista)
    db.session.commit()
    flash('🗑️ Todas as conquistas foram apagadas!', 'info')
    return redirect(url_for('diario'))

@app.route('/deletar_todos_momentos/<tipo>', methods=['POST'])
def deletar_todos_momentos(tipo):
    """Deleta TODOS os momentos de um tipo (gratidao ou importante)"""
    momentos = MomentoGratidao.query.filter_by(tipo=tipo).all()
    for momento in momentos:
        # Apaga as fotos
        if momento.foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], momento.foto.replace('uploads/', ''))
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except:
                pass
        db.session.delete(momento)
    db.session.commit()
    flash(f'🗑️ Todos os momentos de {tipo} foram apagados!', 'info')
    if tipo == 'importante':
        return redirect(url_for('importantes'))
    return redirect(url_for('gratidao'))

@app.route('/adicionar_tarefa_extra', methods=['POST'])
def adicionar_tarefa_extra():
    descricao = request.form.get('descricao')
    if descricao:
        nova_tarefa = Tarefa(
            descricao=descricao,
            dia_semana='Extras',
            concluida_robo=False,
            concluida_usuario=False,
            extra=True
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa extra adicionada!', 'success')
    
    return redirect(url_for('planejamento'))

@app.route('/remover_tarefa/<int:tarefa_id>', methods=['POST'])
def remover_tarefa(tarefa_id):
    tarefa = Tarefa.query.get(tarefa_id)
    if tarefa:
        TarefaDia.query.filter_by(tarefa_id=tarefa_id).delete()
        db.session.delete(tarefa)
        db.session.commit()
        flash('Tarefa removida com sucesso!', 'success')
    return redirect(url_for('planejamento'))

@app.route('/resetar_tarefas', methods=['POST'])
def resetar_tarefas():
    Tarefa.query.delete()
    TarefaDia.query.delete()
    db.session.commit()
    flash('Todas as tarefas foram resetadas!', 'info')
    return redirect(url_for('index'))

@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if request.method == 'POST':
        tarefas_por_dia = request.form.get('tarefas_por_dia', '7')
        
        if tarefas_por_dia == 'custom':
            tarefas_por_dia = request.form.get('tarefas_custom', '7')
        
        config = Config.query.filter_by(chave='tarefas_por_dia').first()
        if config:
            config.valor = tarefas_por_dia
        else:
            config = Config(chave='tarefas_por_dia', valor=tarefas_por_dia)
            db.session.add(config)
        
        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('configuracoes'))
    
    tarefas_por_dia = get_config('tarefas_por_dia', '7')
    
    return render_template('configuracoes.html', 
                         tarefas_por_dia=tarefas_por_dia)

@app.route('/resetar_historias', methods=['POST'])
def resetar_historias():
    """Reseta todas as histórias para começar do zero"""
    alter = AlterEgo.query.first()
    if alter:
        alter.historia_atual = 'inicio'
        alter.historias_contadas = ''
        alter.tarefa_desbloqueio = 0
        db.session.commit()
        flash('Histórias resetadas! O Alter Ego vai começar do início.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Carrega as histórias se não existirem
        if Historia.query.count() == 0:
            carregar_historias_enorme()
    app.run(host='0.0.0.0', port=5000, debug=True)
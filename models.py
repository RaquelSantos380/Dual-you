from database import db
from datetime import datetime

class Tarefa(db.Model):
    """Tarefas fixas da semana"""
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    concluida_robo = db.Column(db.Boolean, default=False)
    concluida_usuario = db.Column(db.Boolean, default=False)
    extra = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    ocorrencias = db.relationship('TarefaDia', backref='tarefa_ref', lazy=True, foreign_keys='TarefaDia.tarefa_id')
    conquistas = db.relationship('Conquista', backref='tarefa_ref', lazy=True, foreign_keys='Conquista.tarefa_id')

class TarefaDia(db.Model):
    """Registro das tarefas de um dia específico"""
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)
    concluida = db.Column(db.Boolean, default=False)
    concluida_em = db.Column(db.DateTime, nullable=True)
    
    tarefa = db.relationship('Tarefa', backref='ocorrencias_ref', foreign_keys=[tarefa_id])

class Conquista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)
    descricao = db.Column(db.String(300))
    sentimento = db.Column(db.String(200))
    foto = db.Column(db.String(500), nullable=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    tarefa = db.relationship('Tarefa', backref='conquistas_ref', foreign_keys=[tarefa_id])

class MomentoGratidao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    foto = db.Column(db.String(500), nullable=True)
    tipo = db.Column(db.String(50), default='gratidao')
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True)
    valor = db.Column(db.String(200))

class AlterEgo(db.Model):
    """O Alter Ego - seu rival que se move pela casa"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Identidade
    nome = db.Column(db.String(50), default='Alter Ego')
    nivel = db.Column(db.Integer, default=1)
    
    # Posição na casa
    ambiente = db.Column(db.String(50), default='sala')
    x_relativo = db.Column(db.Integer, default=50)
    y_relativo = db.Column(db.Integer, default=50)
    
    # Estatísticas
    tarefas_concluidas = db.Column(db.Integer, default=0)
    pontos_ganhos = db.Column(db.Integer, default=0)
    energia = db.Column(db.Integer, default=100)
    humor = db.Column(db.String(20), default='normal')
    
    # Controle
    ultima_acao = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_frase = db.Column(db.String(300), nullable=True)
    ultima_interacao = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='acordado')
    
    def get_coordenadas_absolutas(self):
        """Converte coordenadas relativas para a imagem 2048x2048"""
        ambientes = {
            'lavanderia': {'x_min': 0, 'x_max': 682, 'y_min': 0, 'y_max': 682},
            'cozinha': {'x_min': 682, 'x_max': 1364, 'y_min': 0, 'y_max': 682},
            'banheiro': {'x_min': 1364, 'x_max': 2048, 'y_min': 0, 'y_max': 682},
            'sala': {'x_min': 0, 'x_max': 682, 'y_min': 682, 'y_max': 1364},
            'quarto1': {'x_min': 682, 'x_max': 1364, 'y_min': 682, 'y_max': 1364},
            'quarto2': {'x_min': 1364, 'x_max': 2048, 'y_min': 682, 'y_max': 1364},
            'garagem': {'x_min': 0, 'x_max': 682, 'y_min': 1364, 'y_max': 2048},
            'varanda': {'x_min': 682, 'x_max': 1364, 'y_min': 1364, 'y_max': 2048},
            'area_moto': {'x_min': 1364, 'x_max': 2048, 'y_min': 1364, 'y_max': 2048}
        }
        
        ambiente = ambientes.get(self.ambiente, ambientes['sala'])
        largura = ambiente['x_max'] - ambiente['x_min']
        altura = ambiente['y_max'] - ambiente['y_min']
        
        x_abs = ambiente['x_min'] + (largura * self.x_relativo / 100)
        y_abs = ambiente['y_min'] + (altura * self.y_relativo / 100)
        
        return int(x_abs), int(y_abs)

class FraseMotivacional(db.Model):
    """Banco de frases do Alter Ego"""
    id = db.Column(db.Integer, primary_key=True)
    frase = db.Column(db.String(300), nullable=False)
    categoria = db.Column(db.String(50), default='geral')
    usada_em = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def carregar_frases_padrao(cls):
        """Carrega as frases iniciais se não existirem"""
        frases = [
            # LEMBRETES (quando tem tarefa pendente)
            ("Ei... você não está esquecendo de '{tarefa}'?", 'lembrete'),
            ("Hmm... '{tarefa}' ainda não foi feito...", 'lembrete'),
            ("Sabe aquela tarefa '{tarefa}'? Pois é...", 'lembrete'),
            ("Não vai deixar '{tarefa}' para depois, né?", 'lembrete'),
            ("'{tarefa}' tá te esperando...", 'lembrete'),
            ("Só lembrando: '{tarefa}' ainda está pendente", 'lembrete'),
            ("Você ia fazer '{tarefa}' hoje, lembra?", 'lembrete'),
            
            # MOTIVACIONAIS (inspiradoras)
            ("Divida suas tarefas em pequenas partes. Um passo de cada vez.", 'motivacional'),
            ("Você é capaz de fazer coisas incríveis. Comece agora.", 'motivacional'),
            ("Não espere o momento perfeito. Crie ele.", 'motivacional'),
            ("Pequenas ações diárias constroem grandes resultados.", 'motivacional'),
            ("Você já superou tantas coisas. Essa tarefa é só mais uma.", 'motivacional'),
            ("Seu futuro eu vai agradecer por cada tarefa concluída hoje.", 'motivacional'),
            ("O único modo de fazer um ótimo trabalho é amar o que você faz.", 'motivacional'),
            ("Não pare quando estiver cansado. Pare quando terminar.", 'motivacional'),
            ("Você está mais perto do que imagina.", 'motivacional'),
            ("Cada tarefa concluída é um passo mais perto dos seus sonhos.", 'motivacional'),
            ("Acredite que você pode, você já está no meio do caminho.", 'motivacional'),
            ("Hoje é um novo dia. Novas oportunidades.", 'motivacional'),
            ("Você não veio até aqui para desistir agora.", 'motivacional'),
            ("Respira fundo. Uma coisa de cada vez.", 'motivacional'),
            ("O progresso é melhor que a perfeição.", 'motivacional'),
            ("Você no comando. Sempre foi.", 'motivacional'),
            
            # BRAVO (quando muitas tarefas atrasadas)
            ("Tá difícil hoje? Respira. Você consegue.", 'bravo'),
            ("Eu sei que você pode. Já te vi fazer coisas mais difíceis.", 'bravo'),
            ("Vamos lá! Não deixa isso te vencer.", 'bravo'),
            ("Eu acredito em você. Mesmo que você não acredite agora.", 'bravo'),
            ("Levanta a cabeça. O dia ainda não acabou.", 'bravo'),
            ("Você é mais forte que essa preguiça.", 'bravo'),
            ("Já são {tarefas_pendentes} tarefas esperando... bora?", 'bravo'),
            
            # INTERAÇÕES ALEATÓRIAS
            ("Oi... sou eu de novo. Seu outro eu.", 'interacao'),
            ("Tô aqui, vendo você...", 'interacao'),
            ("Pensando em você. E nas tarefas.", 'interacao'),
            ("Será que hoje a gente consegue?", 'interacao'),
            ("Não vou desistir de você. Nunca.", 'interacao'),
            ("Tô do seu lado. Sempre.", 'interacao'),
            ("Mesmo que você não me escute, eu tô aqui.", 'interacao'),
            
            # RECÉM ADICIONADAS
            ("Você sabia que eu sou você? Pois é...", 'interacao'),
            ("Já fez sua tarefa hoje? Não? Tô vendo...", 'lembrete'),
            ("Se você não fizer, quem vai fazer?", 'motivacional'),
            ("Vamos lá, só mais essa tarefinha...", 'motivacional'),
            ("Você consegue, eu sei que consegue.", 'motivacional'),
            ("Tô te observando... E esperando.", 'interacao'),
            ("Bora lá, time! Digo... você!", 'motivacional'),
            ("Tarefas não vão se fazer sozinhas.", 'lembrete'),
            ("Imagina como vai ser bom quando terminar tudo.", 'motivacional'),
            ("Eu acredito em você. Sério.", 'motivacional'),
        ]
        
        for frase, cat in frases:
            existe = cls.query.filter_by(frase=frase).first()
            if not existe:
                db.session.add(cls(frase=frase, categoria=cat))
        db.session.commit()

# Dicionário com informações dos ambientes
AMBIENTES_INFO = {
    'lavanderia': {'nome': 'Lavanderia', 'icone': '🧺', 'acoes': ['lavando roupa', 'estendendo roupa', 'dobrando roupa']},
    'cozinha': {'nome': 'Cozinha', 'icone': '🍳', 'acoes': ['cozinhando', 'lavando louça', 'comendo']},
    'banheiro': {'nome': 'Banheiro', 'icone': '🚿', 'acoes': ['escovando dentes', 'tomando banho']},
    'sala': {'nome': 'Sala', 'icone': '📺', 'acoes': ['vendo TV', 'lendo livro', 'descansando']},
    'quarto1': {'nome': 'Quarto 1', 'icone': '🛏️', 'acoes': ['dormindo', 'arrumando cama', 'pegando roupa']},
    'quarto2': {'nome': 'Quarto 2', 'icone': '📚', 'acoes': ['estudando', 'trabalhando', 'meditando']},
    'garagem': {'nome': 'Garagem', 'icone': '🔧', 'acoes': ['lavando carro', 'arrumando ferramentas']},
    'varanda': {'nome': 'Varanda', 'icone': '☕', 'acoes': ['tomando sol', 'cuidando plantas', 'lendo jornal']},
    'area_moto': {'nome': 'Área da Moto', 'icone': '🏍️', 'acoes': ['limpando moto', 'abastecendo', 'saindo para passear']}
}
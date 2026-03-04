from database import db
from datetime import datetime

class Tarefa(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), default='Alter Ego')
    nivel = db.Column(db.Integer, default=1)
    ambiente = db.Column(db.String(50), default='sala')
    x_relativo = db.Column(db.Integer, default=50)
    y_relativo = db.Column(db.Integer, default=50)
    tarefas_concluidas = db.Column(db.Integer, default=0)
    pontos_ganhos = db.Column(db.Integer, default=0)
    energia = db.Column(db.Integer, default=100)
    humor = db.Column(db.String(20), default='normal')
    ultima_acao = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_frase = db.Column(db.String(300), nullable=True)
    ultima_interacao = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='acordado')
    
    # NOVO: Sistema de histórias
    historia_atual = db.Column(db.String(50), default='inicio')
    tarefa_desbloqueio = db.Column(db.Integer, default=0)  # ID da tarefa que desbloqueia próxima parte
    historias_contadas = db.Column(db.Text, default='')  # Lista de histórias já contadas
    
    def get_coordenadas_absolutas(self):
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

class Historia(db.Model):
    """Histórias do Alter Ego"""
    id = db.Column(db.Integer, primary_key=True)
    capitulo = db.Column(db.String(50), nullable=False)  # inicio, desenvolvimento, climax, etc
    parte = db.Column(db.Integer, default=1)
    frase = db.Column(db.String(500), nullable=False)
    proxima_parte = db.Column(db.Integer, nullable=True)  # ID da próxima parte
    tarefa_necessaria = db.Column(db.String(200), nullable=True)  # Tarefa que desbloqueia
    emocao = db.Column(db.String(50), default='normal')  # feliz, triste, misterioso, etc
    
    @classmethod
    def carregar_historias_padrao(cls):
        historias = [
            # CAPÍTULO 1 - INÍCIO
            ('inicio', 1, 'Preciso que você termine uma tarefa para eu te contar uma coisa...', None, 'misterioso'),
            ('inicio', 2, 'Ah, você terminou! Sabe, eu lembro quando comecei minha primeira tarefa também...', None, 'nostalgico'),
            ('inicio', 3, 'Te conto o resto quando você terminar "{tarefa}"!', None, 'motivador'),
            
            # CAPÍTULO 2 - O SEGREDO
            ('segredo', 1, 'Você notou que eu me mexo pela casa? Tenho meus motivos...', None, 'misterioso'),
            ('segredo', 2, 'Cada ambiente me lembra uma história. Na cozinha, por exemplo...', None, 'nostalgico'),
            ('segredo', 3, 'Quer saber o que aconteceu na cozinha? Termina "{tarefa}" que eu conto!', None, 'motivador'),
            
            # CAPÍTULO 3 - AVENTURA
            ('aventura', 1, 'Hoje eu quase saí de casa! Fui até a varanda...', None, 'animado'),
            ('aventura', 2, 'Lá fora tem um mundo inteiro esperando. Mas primeiro, precisamos terminar nossas tarefas!', None, 'motivador'),
            ('aventura', 3, 'Quando você terminar "{tarefa}", te conto o que vi da varanda!', None, 'misterioso'),
            
            # FRASES MOTIVACIONAIS (quando não tem história nova)
            ('motivacional', 1, 'Você não está esquecendo de algo? "{tarefa}" ainda te espera...', None, 'lembrete'),
            ('motivacional', 2, 'Divida suas tarefas em pequenas partes. Um passo de cada vez.', None, 'motivador'),
            ('motivacional', 3, 'Sabe aquela tarefa "{tarefa}"? Ela vai ser tão boa quando terminar!', None, 'animado'),
            ('motivacional', 4, 'Estou aqui, vendo você. E acreditando.', None, 'calmo'),
            ('motivacional', 5, 'Já pensou como vai ser o alívio quando terminar tudo?', None, 'sonhador'),
            ('motivacional', 6, 'Você consegue. Eu sei que consegue.', None, 'motivador'),
            ('motivacional', 7, 'Respira fundo. Uma coisa de cada vez.', None, 'calmo'),
            ('motivacional', 8, 'Cada tarefa concluída é um passo mais perto dos seus sonhos.', None, 'inspirador'),
        ]
        
        for capitulo, parte, frase, tarefa, emocao in historias:
            existe = cls.query.filter_by(capitulo=capitulo, parte=parte).first()
            if not existe:
                db.session.add(cls(
                    capitulo=capitulo,
                    parte=parte,
                    frase=frase,
                    tarefa_necessaria=tarefa,
                    emocao=emocao
                ))
        db.session.commit()

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
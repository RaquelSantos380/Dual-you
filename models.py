from database import db
from datetime import datetime

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)  # Segunda, Terça, etc.
    concluida_robo = db.Column(db.Boolean, default=False)
    concluida_usuario = db.Column(db.Boolean, default=False)
    extra = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com as conquistas
    conquistas = db.relationship('Conquista', backref='tarefa', lazy=True)

class TarefaDia(db.Model):
    """Registro das tarefas de um dia específico"""
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)
    concluida = db.Column(db.Boolean, default=False)
    concluida_em = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento
    tarefa = db.relationship('Tarefa', backref='ocorrencias')

class Conquista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)
    descricao = db.Column(db.String(300))
    sentimento = db.Column(db.String(200))  # Como se sentiu
    foto = db.Column(db.String(500), nullable=True)  # URL da foto
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

class MomentoGratidao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    foto = db.Column(db.String(500), nullable=True)
    tipo = db.Column(db.String(50), default='gratidao')  # 'gratidao' ou 'importante'
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True)
    valor = db.Column(db.String(200))
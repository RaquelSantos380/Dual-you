from database import db
from datetime import datetime

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    data = db.Column(db.Date, nullable=True)  # Se None, é tarefa da semana
    dia_semana = db.Column(db.String(20), nullable=True)  # Segunda, Terça, etc.
    concluida_robo = db.Column(db.Boolean, default=False)
    concluida_usuario = db.Column(db.Boolean, default=False)
    extra = db.Column(db.Boolean, default=False)  # Tarefa extra do dia
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

class Pontuacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, unique=True, nullable=False)
    pontos_robo = db.Column(db.Integer, default=0)
    pontos_usuario = db.Column(db.Integer, default=0)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True)
    valor = db.Column(db.String(200))

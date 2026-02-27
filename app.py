from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import db
from models import Tarefa, Pontuacao, Config
from datetime import datetime, date
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dual_you.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_pontuacao_atual():
    """Retorna a pontuação atual do robô e do usuário"""
    with app.app_context():
        # Pontuação do robô (tarefas automáticas)
        tarefas_robo = Tarefa.query.filter_by(concluida_robo=True).count()
        pontos_robo = tarefas_robo * 15
        
        # Pontuação do usuário (tarefas manuais)
        tarefas_usuario = Tarefa.query.filter_by(concluida_usuario=True).count()
        pontos_usuario = tarefas_usuario * 15
        
        return pontos_robo, pontos_usuario

def get_config(chave, valor_padrao):
    """Pega uma configuração do banco de dados"""
    config = Config.query.filter_by(chave=chave).first()
    if config:
        return config.valor
    return valor_padrao

@app.route('/')
def index():
    hoje = date.today()
    dia_semana = hoje.strftime('%A')
    dias_traduzidos = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    dia_pt = dias_traduzidos.get(dia_semana, dia_semana)
    
    # Busca tarefas do dia
    tarefas_hoje = Tarefa.query.filter_by(data=hoje).all()
    
    # Se não houver tarefas para hoje, busca tarefas da semana e sorteia
    if not tarefas_hoje:
        tarefas_semana = Tarefa.query.filter_by(data=None).all()
        if tarefas_semana:
            # Pega a configuração de quantidade de tarefas
            qtd_tarefas = int(get_config('tarefas_por_dia', '7'))
            num_tarefas = min(qtd_tarefas, len(tarefas_semana))
            tarefas_sorteadas = random.sample(tarefas_semana, num_tarefas)
            for tarefa in tarefas_sorteadas:
                nova_tarefa_dia = Tarefa(
                    descricao=tarefa.descricao,
                    data=hoje,
                    concluida_robo=True,
                    concluida_usuario=False
                )
                db.session.add(nova_tarefa_dia)
            db.session.commit()
            tarefas_hoje = Tarefa.query.filter_by(data=hoje).all()
    
    pontos_robo, pontos_usuario = get_pontuacao_atual()
    diferenca = pontos_usuario - pontos_robo
    
    return render_template('index.html', 
                         dia=dia_pt,
                         tarefas=tarefas_hoje,
                         pontos_robo=pontos_robo,
                         pontos_usuario=pontos_usuario,
                         diferenca=diferenca)

@app.route('/concluir_tarefa/<int:tarefa_id>', methods=['POST'])
def concluir_tarefa(tarefa_id):
    tarefa = Tarefa.query.get(tarefa_id)
    if tarefa and not tarefa.concluida_usuario:
        tarefa.concluida_usuario = True
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/adicionar_tarefa_extra', methods=['POST'])
def adicionar_tarefa_extra():
    descricao = request.form.get('descricao')
    if descricao:
        hoje = date.today()
        nova_tarefa = Tarefa(
            descricao=descricao,
            data=hoje,
            concluida_robo=False,
            concluida_usuario=False,
            extra=True
        )
        db.session.add(nova_tarefa)
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/planejamento')
def planejamento():
    tarefas_semana = Tarefa.query.filter_by(data=None).all()
    return render_template('planejamento.html', tarefas=tarefas_semana)

@app.route('/adicionar_tarefa_semana', methods=['POST'])
def adicionar_tarefa_semana():
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
    
    return redirect(url_for('planejamento'))

@app.route('/embaralhar_tarefas', methods=['POST'])
def embaralhar_tarefas():
    """Remove tarefas de hoje e sorteia novas"""
    hoje = date.today()
    Tarefa.query.filter_by(data=hoje).delete()
    
    tarefas_semana = Tarefa.query.filter_by(data=None).all()
    if tarefas_semana:
        # Pega a configuração de quantidade de tarefas
        qtd_tarefas = int(get_config('tarefas_por_dia', '7'))
        num_tarefas = min(qtd_tarefas, len(tarefas_semana))
        tarefas_sorteadas = random.sample(tarefas_semana, num_tarefas)
        for tarefa in tarefas_sorteadas:
            nova_tarefa_dia = Tarefa(
                descricao=tarefa.descricao,
                data=hoje,
                concluida_robo=True,
                concluida_usuario=False
            )
            db.session.add(nova_tarefa_dia)
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/resetar_semana', methods=['POST'])
def resetar_semana():
    """Reseta todas as tarefas para começar nova semana"""
    Tarefa.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if request.method == 'POST':
        # Pega o valor selecionado
        tarefas_por_dia = request.form.get('tarefas_por_dia', '7')
        
        # Se for personalizado, pega o valor do campo custom
        if tarefas_por_dia == 'custom':
            tarefas_por_dia = request.form.get('tarefas_custom', '7')
        
        # Verifica se já existe a configuração
        config = Config.query.filter_by(chave='tarefas_por_dia').first()
        if config:
            config.valor = tarefas_por_dia
        else:
            config = Config(chave='tarefas_por_dia', valor=tarefas_por_dia)
            db.session.add(config)
        
        db.session.commit()
        return redirect(url_for('configuracoes'))
    
    # Pega as configurações atuais
    tarefas_por_dia = get_config('tarefas_por_dia', '7')
    
    return render_template('configuracoes.html', 
                         tarefas_por_dia=tarefas_por_dia)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
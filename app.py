from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import Tarefa, TarefaDia, Conquista, MomentoGratidao, Config
from datetime import datetime, date
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dual_you.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Para mensagens flash
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db.init_app(app)

# Garantir que a pasta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_pontuacao_atual():
    """Retorna a pontuação atual do robô e do usuário"""
    with app.app_context():
        # Pontuação do robô (tarefas automáticas do dia)
        hoje = date.today()
        tarefas_hoje = TarefaDia.query.join(Tarefa).filter(
            TarefaDia.data == hoje
        ).all()
        
        pontos_robo = len(tarefas_hoje) * 15  # Robô "completa" todas as tarefas do dia
        pontos_usuario = TarefaDia.query.filter_by(
            data=hoje, 
            concluida=True
        ).count() * 15
        
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
    
    # Busca as tarefas fixas para hoje
    tarefas_fixas = Tarefa.query.filter_by(dia_semana=dia_pt).all()
    
    # Cria ou busca as tarefas do dia
    for tarefa in tarefas_fixas:
        tarefa_dia = TarefaDia.query.filter_by(
            data=hoje, 
            tarefa_id=tarefa.id
        ).first()
        
        if not tarefa_dia:
            tarefa_dia = TarefaDia(
                data=hoje,
                tarefa_id=tarefa.id,
                concluida=False
            )
            db.session.add(tarefa_dia)
    
    # Adiciona tarefas extras se existirem
    tarefas_extra = Tarefa.query.filter_by(
        extra=True
    ).all()
    
    for tarefa in tarefas_extra:
        tarefa_dia = TarefaDia.query.filter_by(
            data=hoje, 
            tarefa_id=tarefa.id
        ).first()
        
        if not tarefa_dia:
            tarefa_dia = TarefaDia(
                data=hoje,
                tarefa_id=tarefa.id,
                concluida=False
            )
            db.session.add(tarefa_dia)
    
    db.session.commit()
    
    # Busca todas as tarefas do dia para exibir
    tarefas_hoje = TarefaDia.query.filter_by(data=hoje).all()
    
    pontos_robo, pontos_usuario = get_pontuacao_atual()
    diferenca = pontos_usuario - pontos_robo
    
    return render_template('index.html', 
                         dia=dia_pt,
                         tarefas=tarefas_hoje,
                         pontos_robo=pontos_robo,
                         pontos_usuario=pontos_usuario,
                         diferenca=diferenca)

@app.route('/concluir_tarefa/<int:tarefa_dia_id>', methods=['POST'])
def concluir_tarefa(tarefa_dia_id):
    tarefa_dia = TarefaDia.query.get(tarefa_dia_id)
    if tarefa_dia and not tarefa_dia.concluida:
        tarefa_dia.concluida = True
        tarefa_dia.concluida_em = datetime.utcnow()
        db.session.commit()
        
        # Redireciona para página de registro de conquista
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
                # Criar nome único para não sobrescrever
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
        
        # Upload da foto
        foto_filename = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Criar nome único para não sobrescrever
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

@app.route('/adicionar_tarefa_extra', methods=['POST'])
def adicionar_tarefa_extra():
    descricao = request.form.get('descricao')
    if descricao:
        nova_tarefa = Tarefa(
            descricao=descricao,
            dia_semana='Extra',
            concluida_robo=False,
            concluida_usuario=False,
            extra=True
        )
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa extra adicionada!', 'success')
    
    return redirect(url_for('planejamento'))

@app.route('/resetar_tarefas', methods=['POST'])
def resetar_tarefas():
    """Remove todas as tarefas e começa do zero"""
    Tarefa.query.delete()
    TarefaDia.query.delete()
    db.session.commit()
    flash('Todas as tarefas foram resetadas!', 'info')
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
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('configuracoes'))
    
    # Pega as configurações atuais
    tarefas_por_dia = get_config('tarefas_por_dia', '7')
    
    return render_template('configuracoes.html', 
                         tarefas_por_dia=tarefas_por_dia)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
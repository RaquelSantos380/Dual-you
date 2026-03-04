from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from database import db
from models import Tarefa, TarefaDia, Conquista, MomentoGratidao, Config, AlterEgo, FraseMotivacional, AMBIENTES_INFO
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
    """Retorna a pontuação atual do robô (Alter Ego) e do usuário"""
    with app.app_context():
        hoje = date.today()
        
        # Pontos do Alter Ego (vem do banco)
        alter = AlterEgo.query.first()
        if not alter:
            alter = AlterEgo()
            db.session.add(alter)
            db.session.commit()
        pontos_robo = alter.pontos_ganhos
        
        # Pontos do usuário
        tarefas_usuario = TarefaDia.query.filter_by(
            data=hoje, 
            concluida=True
        ).count()
        pontos_usuario = tarefas_usuario * 15
        
        return pontos_robo, pontos_usuario

def get_config(chave, valor_padrao):
    config = Config.query.filter_by(chave=chave).first()
    if config:
        return config.valor
    return valor_padrao

# ========== FRASES DO ALTER EGO ==========

def get_frase_alter_ego(tarefa_pendente=None, tarefas_pendentes_count=0):
    """Retorna uma frase apropriada baseada no contexto"""
    from models import FraseMotivacional
    
    # Decide categoria baseada no contexto
    if tarefa_pendente and random.random() < 0.4:
        categoria = 'lembrete'
    elif tarefas_pendentes_count > 3:
        categoria = random.choice(['bravo', 'motivacional'])
    else:
        categoria = random.choice(['motivacional', 'interacao'])
    
    # Busca frase da categoria
    frase_obj = FraseMotivacional.query.filter_by(categoria=categoria).order_by(db.func.random()).first()
    
    if frase_obj:
        frase = frase_obj.frase
        # Substitui placeholders
        if '{tarefa}' in frase and tarefa_pendente:
            frase = frase.replace('{tarefa}', tarefa_pendente)
        if '{tarefas_pendentes}' in frase:
            frase = frase.replace('{tarefas_pendentes}', str(tarefas_pendentes_count))
        return frase
    
    return "Você consegue! Vamos nessa!"

# ========== ALTER EGO - O RIVAL QUE SE MOVE ==========

def atualizar_alter_ego():
    """O Alter Ego age: compete, se move, e INTERAGE"""
    with app.app_context():
        try:
            alter = AlterEgo.query.first()
            if not alter:
                alter = AlterEgo()
                db.session.add(alter)
                db.session.commit()
            
            # Carrega frases se não existirem
            FraseMotivacional.carregar_frases_padrao()
            
            hoje = date.today()
            
            # 1. PRIMEIRO: VERIFICAR TAREFAS PENDENTES
            tarefas_pendentes = TarefaDia.query.filter_by(
                data=hoje,
                concluida=False
            ).all()
            
            tarefas_pendentes_count = len(tarefas_pendentes)
            
            # Escolhe uma tarefa pendente aleatória para mencionar
            tarefa_pendente_nome = None
            if tarefas_pendentes:
                tarefa_aleatoria = random.choice(tarefas_pendentes)
                tarefa_pendente_nome = tarefa_aleatoria.tarefa.descricao
            
            # 2. TENTAR COMPLETAR UMA TAREFA (SE TIVER ENERGIA)
            if tarefas_pendentes and alter.energia > 20 and random.random() < 0.3:
                tarefa_hoje = random.choice(tarefas_pendentes)
                
                # Alter Ego completa a tarefa e ganha pontos!
                tarefa_hoje.concluida = True
                tarefa_hoje.concluida_em = datetime.utcnow()
                
                alter.tarefas_concluidas += 1
                alter.pontos_ganhos += 15
                alter.energia -= 10
                
                print(f"⚔️ Alter Ego completou: {tarefa_hoje.tarefa.descricao} (+15 pts)")
                
                # INTERAÇÃO: ele avisa que completou
                alter.ultima_frase = f"Completado: {tarefa_hoje.tarefa.descricao}"
                alter.ultima_interacao = datetime.utcnow()
            
            # 3. MOVIMENTAÇÃO PELA CASA
            else:
                if random.random() < 0.3:
                    novo_ambiente = random.choice(list(AMBIENTES_INFO.keys()))
                    alter.ambiente = novo_ambiente
                    alter.x_relativo = random.randint(30, 70)
                    alter.y_relativo = random.randint(30, 70)
                    
                    print(f"🚶 Alter Ego foi para {AMBIENTES_INFO[novo_ambiente]['nome']}")
                else:
                    alter.x_relativo += random.randint(-8, 8)
                    alter.y_relativo += random.randint(-8, 8)
                    alter.x_relativo = max(15, min(85, alter.x_relativo))
                    alter.y_relativo = max(15, min(85, alter.y_relativo))
                
                alter.energia = min(100, alter.energia + 2)
            
            # 4. COMPORTAMENTOS E HUMOR
            if alter.energia < 20:
                alter.humor = 'cansado'
                alter.estado = 'dormindo'
                alter.energia += 5
            elif alter.energia > 80:
                alter.humor = 'animado'
                alter.estado = 'acordado'
            else:
                alter.humor = 'normal'
                alter.estado = 'acordado'
            
            # 5. CHANCE DE INTERAGIR (falar algo)
            if random.random() < 0.25:
                frase = get_frase_alter_ego(tarefa_pendente_nome, tarefas_pendentes_count)
                alter.ultima_frase = frase
                alter.ultima_interacao = datetime.utcnow()
                print(f"💬 Alter Ego: {frase}")
            
            # 6. SE MUITAS TAREFAS PENDENTES, FICA MAIS BRAVO
            if tarefas_pendentes_count > 3 and alter.humor != 'cansado':
                alter.humor = 'bravo'
            
            alter.ultima_acao = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            print(f"Erro no Alter Ego: {e}")

# Scheduler (a cada 20 segundos)
scheduler = BackgroundScheduler()
scheduler.add_job(func=atualizar_alter_ego, trigger="interval", seconds=20)
scheduler.start()

@app.route('/api/alterego')
def api_alterego():
    """API para pegar posição, estado e FRASE do Alter Ego"""
    alter = AlterEgo.query.first()
    if not alter:
        alter = AlterEgo()
        db.session.add(alter)
        db.session.commit()
    
    x_abs, y_abs = alter.get_coordenadas_absolutas()
    info = AMBIENTES_INFO.get(alter.ambiente, AMBIENTES_INFO['sala'])
    
    # Verifica tarefas pendentes para o humor
    hoje = date.today()
    tarefas_pendentes = TarefaDia.query.filter_by(data=hoje, concluida=False).count()
    
    # Define ação baseada no estado
    if alter.estado == 'trabalhando':
        acao = "trabalhando"
    elif alter.estado == 'fora':
        acao = "fora de casa"
    elif alter.estado == 'dormindo':
        acao = "dormindo"
    else:
        acao = random.choice(info['acoes'])
    
    # Emoji do humor
    humor_emoji = {
        'feliz': '😊',
        'animado': '🤩',
        'cansado': '😴',
        'bravo': '😤',
        'normal': '😐'
    }.get(alter.humor, '😐')
    
    # Verifica se tem frase nova (nos últimos 30 segundos)
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
        'pontos': alter.pontos_ganhos,
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
    
    tarefas_hoje = TarefaDia.query.filter_by(data=hoje).all()
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
        
        flash('Tarefa concluída! Como você se sentiu?', 'success')
        return redirect(url_for('registrar_conquista', tarefa_id=tarefa_dia.tarefa_id))
    
    return redirect(url_for('index'))

@app.route('/registrar_conquista/<int:tarefa_id>', methods=['GET', 'POST'])
def registrar_conquista(tarefa_id):
    tarefa = Tarefa.query.get(tarefa_id)
    
    if request.method == 'POST':
        sentimento = request.form.get('sentimento')
        descricao = request.form.get('descricao')
        
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
        flash('Tarefa extra adicionada! Ela aparecerá todos os dias.', 'success')
    
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
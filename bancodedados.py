# bancodedados.py
# Execute este arquivo para criar um banco de dados NOVO com todas as colunas e histórias
# Comando: python bancodedados.py

print("=" * 50)
print("🚀 INICIANDO CRIAÇÃO DO BANCO DE DADOS")
print("=" * 50)

from app import app, db
from models import Tarefa, TarefaDia, Conquista, MomentoGratidao, Config, AlterEgo, Historia
from datetime import datetime, date

print("✅ Importações realizadas")

with app.app_context():
    # ===== 1. APAGAR BANCO ANTIGO =====
    print("\n📦 Apagando banco de dados antigo...")
    db.drop_all()
    print("✅ Banco antigo removido com sucesso!")
    
    # ===== 2. CRIAR NOVAS TABELAS =====
    print("\n🏗️  Criando novas tabelas com todas as colunas...")
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")
    print("   - Tarefa")
    print("   - TarefaDia")
    print("   - Conquista")
    print("   - MomentoGratidao")
    print("   - Config")
    print("   - AlterEgo (com as novas colunas: historia_atual, tarefa_desbloqueio, historias_contadas)")
    print("   - Historia")
    
    # ===== 3. CRIAR ALTER EGO INICIAL =====
    print("\n👥 Criando Alter Ego inicial...")
    alter = AlterEgo(
        nome='Alter Ego',
        ambiente='sala',
        x_relativo=50,
        y_relativo=50,
        historia_atual='inicio',  # NOVA COLUNA
        historias_contadas='',      # NOVA COLUNA
        tarefa_desbloqueio=0        # NOVA COLUNA
    )
    db.session.add(alter)
    db.session.commit()
    print("✅ Alter Ego criado com sucesso!")
    
    # ===== 4. CARREGAR AS 124 HISTÓRIAS =====
    print("\n📚 Carregando 124 histórias épicas...")
    
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
    
    print(f"   Total de histórias: {len(historias)}")
    
    for capitulo, parte, frase, tarefa, emocao in historias:
        historia = Historia(
            capitulo=capitulo,
            parte=parte,
            frase=frase,
            tarefa_necessaria=tarefa,
            emocao=emocao
        )
        db.session.add(historia)
    
    db.session.commit()
    print("✅ Histórias carregadas com sucesso!")
    
    # ===== 5. VERIFICAÇÃO FINAL =====
    print("\n🔍 Verificando banco de dados...")
    
    total_historias = Historia.query.count()
    print(f"   📚 Total de histórias no banco: {total_historias}")
    
    alter_verificado = AlterEgo.query.first()
    print(f"   👤 Alter Ego: {alter_verificado.nome}")
    print(f"   📖 História atual: {alter_verificado.historia_atual}")
    print(f"   📜 Histórias contadas: '{alter_verificado.historias_contadas}'")
    
    # ===== 6. RESUMO FINAL =====
    print("\n" + "=" * 50)
    print("✅✅✅ BANCO DE DADOS CRIADO COM SUCESSO! ✅✅✅")
    print("=" * 50)
    print("\n📊 RESUMO:")
    print("   - Todas as tabelas recriadas")
    print("   - Colunas novas adicionadas:")
    print("     • historia_atual")
    print("     • tarefa_desbloqueio") 
    print("     • historias_contadas")
    print(f"   - {total_historias} histórias carregadas")
    print("   - Alter Ego inicializado")
    print("\n🚀 Agora você pode rodar o app:")
    print("   python app.py")
    print("\n📱 Acesse: http://127.0.0.1:5000")
    print("=" * 50)

print("\n✅ Script finalizado!")
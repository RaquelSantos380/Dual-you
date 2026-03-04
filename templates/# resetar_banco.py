# resetar_banco.py
from app import app, db
from models import FraseMotivacional

print("🔄 Recriando banco de dados...")

with app.app_context():
    # Apaga tudo e recria
    db.drop_all()
    db.create_all()
    print("✅ Tabelas recriadas!")
    
    # Carrega as frases
    FraseMotivacional.carregar_frases_padrao()
    print("✅ Frases carregadas!")
    
print("🎉 Banco de dados pronto!")
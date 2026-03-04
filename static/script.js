// ========================================
// ANIMAÇÕES E INTERATIVIDADE
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Animar placar ao carregar
    const placar = document.querySelector('.placar');
    if (placar) {
        placar.style.opacity = '0';
        placar.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            placar.style.transition = 'all 0.5s ease';
            placar.style.opacity = '1';
            placar.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Animar tarefas uma por uma
    const tarefas = document.querySelectorAll('.tarefa-item');
    tarefas.forEach((tarefa, index) => {
        tarefa.style.opacity = '0';
        tarefa.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            tarefa.style.transition = 'all 0.3s ease';
            tarefa.style.opacity = '1';
            tarefa.style.transform = 'translateX(0)';
        }, 200 + (index * 100));
    });
});

// ========================================
// FUNÇÕES DE FORMULÁRIOS
// ========================================

function mostrarFormExtra() {
    const form = document.getElementById('form-extra');
    if (form) {
        form.style.display = 'block';
    }
}

function esconderFormExtra() {
    const form = document.getElementById('form-extra');
    if (form) {
        form.style.display = 'none';
    }
}

function mostrarFormDia(dia) {
    document.getElementById('dia-selecionado').textContent = dia;
    document.getElementById('dia-input').value = dia;
    document.getElementById('form-tarefa-dia').style.display = 'block';
}

function esconderFormDia() {
    document.getElementById('form-tarefa-dia').style.display = 'none';
}

// ========================================
// SERVIÇO DE ATUALIZAÇÃO DO ALTER EGO
// ========================================

let ultimaFrase = '';
let fraseTimeout;

function atualizarAlterEgo() {
    fetch('/api/alterego')
        .then(response => response.json())
        .then(data => {
            const personagem = document.getElementById('alter-personagem');
            const container = document.getElementById('casa-container');
            
            if (!personagem || !container) return;
            
            // Posicionamento do personagem
            const containerImg = container.querySelector('img');
            if (!containerImg) return;
            
            const containerWidth = containerImg.offsetWidth;
            const containerHeight = containerImg.offsetHeight;
            const escalaX = containerWidth / 2048;
            const escalaY = containerHeight / 2048;
            
            const x = data.x_absoluto * escalaX;
            const y = data.y_absoluto * escalaY;
            
            personagem.style.left = x + 'px';
            personagem.style.top = y + 'px';
            
            // Atualiza placar se existir
            const alterPontos = document.getElementById('alter-pontos');
            if (alterPontos) {
                alterPontos.innerText = data.pontos + ' pts';
            }
            
            // Atualiza barra de energia
            const energiaBar = document.getElementById('alter-energia-bar');
            if (energiaBar) {
                energiaBar.style.width = data.energia + '%';
                if (data.energia < 30) energiaBar.style.background = '#f44336';
                else if (data.energia < 60) energiaBar.style.background = '#ff9800';
                else energiaBar.style.background = '#4CAF50';
            }
            
            // Atualiza status
            const ambienteEl = document.getElementById('alter-ambiente');
            const acaoEl = document.getElementById('alter-acao');
            const humorEl = document.getElementById('alter-humor');
            const tarefasEl = document.getElementById('alter-tarefas');
            
            if (ambienteEl) ambienteEl.innerHTML = `📍 ${data.ambiente_nome}`;
            if (acaoEl) acaoEl.innerHTML = `✨ ${data.acao}`;
            if (humorEl) humorEl.innerHTML = data.humor_emoji + ' ' + data.humor;
            if (tarefasEl) tarefasEl.innerHTML = `⚔️ ${data.tarefas_concluidas} concluídas · ${data.tarefas_pendentes} pendentes`;
            
            // FRASE NOVA?
            if (data.ultima_frase && data.ultima_frase !== ultimaFrase && data.tem_frase_nova) {
                ultimaFrase = data.ultima_frase;
                
                const bolha = document.getElementById('alter-bolha');
                const msg = document.getElementById('alter-mensagem');
                const ultimaFraseContainer = document.getElementById('ultima-frase');
                
                if (bolha && msg) {
                    msg.innerText = data.ultima_frase;
                    bolha.style.left = (x - 150) + 'px';
                    bolha.style.top = (y - 100) + 'px';
                    bolha.style.display = 'block';
                }
                
                if (ultimaFraseContainer) {
                    ultimaFraseContainer.innerText = '"' + data.ultima_frase + '"';
                }
                
                if (fraseTimeout) clearTimeout(fraseTimeout);
                fraseTimeout = setTimeout(() => {
                    if (bolha) bolha.style.display = 'none';
                }, 8000);
            }
            
            // Interação ao clicar no personagem
            personagem.onclick = function() {
                fetch('/api/alterego/historia')
                    .then(response => response.json())
                    .then(historiaData => {
                        const bolha = document.getElementById('alter-bolha');
                        const msg = document.getElementById('alter-mensagem');
                        const continuacao = document.getElementById('historia-continuacao');
                        
                        if (bolha && msg) {
                            msg.innerText = historiaData.frase;
                            
                            if (continuacao) {
                                continuacao.style.display = historiaData.precisa_tarefa ? 'block' : 'none';
                            }
                            
                            bolha.style.left = (x - 150) + 'px';
                            bolha.style.top = (y - 100) + 'px';
                            bolha.style.display = 'block';
                            
                            setTimeout(() => {
                                bolha.style.display = 'none';
                            }, 10000);
                        }
                    });
            };
        })
        .catch(error => console.error('Erro ao atualizar Alter Ego:', error));
}

// ========================================
// SERVICE WORKER (PWA)
// ========================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js').then(function(registration) {
            console.log('ServiceWorker registrado com sucesso: ', registration.scope);
        }, function(err) {
            console.log('Falha no registro do ServiceWorker: ', err);
        });
    });
}

// ========================================
// BOTÃO DE INSTALAÇÃO DO PWA
// ========================================

let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Cria botão de instalação
    const installButton = document.createElement('button');
    installButton.innerText = '📲 Instalar App';
    installButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
        background: #764ba2;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 20px;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 8px;
        animation: pulse 2s infinite;
    `;
    
    installButton.addEventListener('click', () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('Usuário instalou o app');
                // Mostra mensagem de agradecimento
                const msg = document.createElement('div');
                msg.innerText = '🎉 Obrigado por instalar o Dual You!';
                msg.style.cssText = `
                    position: fixed;
                    bottom: 80px;
                    left: 20px;
                    background: #2ecc71;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 30px;
                    z-index: 1000;
                    font-weight: bold;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                `;
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 3000);
            }
            deferredPrompt = null;
            installButton.remove();
        });
    });
    
    document.body.appendChild(installButton);
    
    // Remove o botão após 30 segundos se não clicar
    setTimeout(() => {
        if (installButton.parentNode) {
            installButton.remove();
        }
    }, 30000);
});

// ========================================
// ANIMAÇÕES
// ========================================

// Adiciona estilo de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// ========================================
// INICIALIZAÇÃO
// ========================================

// Atualiza o Alter Ego a cada 3 segundos
setInterval(atualizarAlterEgo, 3000);

// Executa uma vez ao carregar
if (document.getElementById('casa-container')) {
    setTimeout(atualizarAlterEgo, 500);
}

// Atualiza posição ao redimensionar a janela
window.addEventListener('resize', () => {
    if (document.getElementById('casa-container')) {
        atualizarAlterEgo();
    }
});

// ========================================
// FUNÇÃO PARA ATUALIZAR PONTUAÇÃO (ANTIGA)
// ========================================

function atualizarPontuacao() {
    const pontosRobo = document.querySelector('.robo .pontos');
    const pontosHumano = document.querySelector('.humano .pontos');
    
    if (pontosRobo && pontosHumano) {
        pontosRobo.style.transition = 'all 0.3s';
        pontosHumano.style.transition = 'all 0.3s';
        
        pontosRobo.style.transform = 'scale(1.2)';
        pontosHumano.style.transform = 'scale(1.2)';
        
        setTimeout(() => {
            pontosRobo.style.transform = 'scale(1)';
            pontosHumano.style.transform = 'scale(1)';
        }, 300);
    }
}

// ========================================
// VERIFICA CONEXÃO COM INTERNET (OFFLINE)
// ========================================

window.addEventListener('offline', () => {
    const offlineMsg = document.createElement('div');
    offlineMsg.innerText = '📴 Você está offline. Algumas funcionalidades podem estar limitadas.';
    offlineMsg.style.cssText = `
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: #e74c3c;
        color: white;
        padding: 10px 20px;
        border-radius: 30px;
        z-index: 2000;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        text-align: center;
    `;
    document.body.appendChild(offlineMsg);
    setTimeout(() => offlineMsg.remove(), 5000);
});

window.addEventListener('online', () => {
    const onlineMsg = document.createElement('div');
    onlineMsg.innerText = '📶 Conexão restabelecida!';
    onlineMsg.style.cssText = `
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: #2ecc71;
        color: white;
        padding: 10px 20px;
        border-radius: 30px;
        z-index: 2000;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        text-align: center;
    `;
    document.body.appendChild(onlineMsg);
    setTimeout(() => onlineMsg.remove(), 3000);
});
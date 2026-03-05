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
// SERUMANINHO - FUNÇÃO COMPLETA
// ========================================

let ultimaFrase = '';
let fraseTimeout;
let ultimaPosicao = { x: 0, y: 0 };

// Função inteligente para posicionar o balão (NUNCA SAI DA TELA)
function posicionarBalao(bolha, personagemX, personagemY, container) {
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;
    const bolhaWidth = 300; // Largura máxima
    const bolhaHeight = 150; // Altura aproximada
    
    // Margens de segurança
    const margem = 15;
    
    // Posição X centralizada no personagem
    let bolhaX = personagemX;
    
    // Ajuste horizontal (nunca sai da tela)
    if (bolhaX - bolhaWidth/2 < margem) {
        bolhaX = bolhaWidth/2 + margem;
    } else if (bolhaX + bolhaWidth/2 > containerWidth - margem) {
        bolhaX = containerWidth - bolhaWidth/2 - margem;
    }
    
    // VERIFICA ESPAÇO ACIMA E ABAIXO
    const espacoAcima = personagemY - bolhaHeight - 20; // 20px de folga
    const espacoAbaixo = containerHeight - (personagemY + 50); // 50px abaixo do personagem
    
    let bolhaY;
    let setaParaBaixo = true; // Padrão: seta aponta para baixo (balão em cima)
    
    // DECISÃO INTELIGENTE: se não couber em cima, coloca embaixo
    if (espacoAcima < 30 && espacoAbaixo > bolhaHeight) {
        // Coloca embaixo (seta aponta para cima)
        bolhaY = personagemY + 50;
        setaParaBaixo = false;
    } else {
        // Coloca em cima (padrão)
        bolhaY = personagemY - bolhaHeight - 10;
        setaParaBaixo = true;
    }
    
    // Ajusta a seta do balão
    const seta = bolha.querySelector('div:first-child');
    if (seta) {
        if (setaParaBaixo) {
            // Seta para baixo (balão em cima)
            seta.style.bottom = '-15px';
            seta.style.top = 'auto';
            seta.style.borderTop = '15px solid #764ba2';
            seta.style.borderBottom = 'none';
        } else {
            // Seta para cima (balão embaixo)
            seta.style.bottom = 'auto';
            seta.style.top = '-15px';
            seta.style.borderTop = 'none';
            seta.style.borderBottom = '15px solid #764ba2';
        }
    }
    
    return { x: bolhaX, y: bolhaY };
}

function atualizarSerumaninho() {
    fetch('/api/alterego')
        .then(response => response.json())
        .then(data => {
            const personagem = document.getElementById('alter-personagem');
            const container = document.getElementById('casa-container');
            
            if (!personagem || !container) return;
            
            // ===== 1. POSICIONAMENTO PERFEITO =====
            const containerImg = container.querySelector('img');
            if (!containerImg) return;
            
            const containerWidth = containerImg.offsetWidth;
            const containerHeight = containerImg.offsetHeight;
            
            // Escala exata (imagem 2048x2048)
            const escalaX = containerWidth / 2048;
            const escalaY = containerHeight / 2048;
            
            // Coordenadas absolutas com limites de segurança
            let x = Math.max(20, Math.min(containerWidth - 20, data.x_absoluto * escalaX));
            let y = Math.max(20, Math.min(containerHeight - 20, data.y_absoluto * escalaY));
            
            // Suaviza movimento (evita teleportes bruscos)
            if (ultimaPosicao.x && Math.abs(x - ultimaPosicao.x) > 50) {
                x = ultimaPosicao.x + (x - ultimaPosicao.x) * 0.3;
            }
            if (ultimaPosicao.y && Math.abs(y - ultimaPosicao.y) > 50) {
                y = ultimaPosicao.y + (y - ultimaPosicao.y) * 0.3;
            }
            
            personagem.style.left = x + 'px';
            personagem.style.top = y + 'px';
            
            ultimaPosicao = { x, y };
            
            // ===== 2. APLICAR HUMOR (COR E ANIMAÇÃO) =====
            personagem.className = '';
            personagem.classList.add(`humor-${data.humor}`);
            
            // ===== 3. ATUALIZAR STATUS =====
            const alterPontos = document.getElementById('alter-pontos');
            if (alterPontos) alterPontos.innerText = data.pontos + ' pts';
            
            // Barra de energia
            const energiaBar = document.getElementById('alter-energia-bar');
            if (energiaBar) {
                energiaBar.style.width = data.energia + '%';
                if (data.energia < 30) energiaBar.style.background = '#f44336';
                else if (data.energia < 60) energiaBar.style.background = '#ff9800';
                else energiaBar.style.background = '#4CAF50';
            }
            
            // Textos de status
            const ambienteEl = document.getElementById('alter-ambiente');
            const acaoEl = document.getElementById('alter-acao');
            const humorEl = document.getElementById('alter-humor');
            const humorEmoji = document.getElementById('alter-humor-emoji');
            const tarefasEl = document.getElementById('alter-tarefas');
            
            if (ambienteEl) ambienteEl.innerText = data.ambiente_nome;
            if (acaoEl) acaoEl.innerText = data.acao;
            if (humorEl) humorEl.innerText = data.humor;
            if (humorEmoji) humorEmoji.innerText = data.humor_emoji;
            if (tarefasEl) tarefasEl.innerText = `${data.tarefas_concluidas}/${data.tarefas_pendentes}`;
            
            // ===== 4. CONTROLAR INDICADOR DE HISTÓRIA =====
            const indicador = document.getElementById('historia-indicador');
            if (indicador) {
                if (data.tem_frase_nova) {
                    indicador.style.display = 'flex';
                } else {
                    indicador.style.display = 'none';
                }
            }
            
            // ===== 5. MOSTRAR NOVA FRASE (COM BALÃO INTELIGENTE) =====
            if (data.ultima_frase && data.ultima_frase !== ultimaFrase && data.tem_frase_nova) {
                ultimaFrase = data.ultima_frase;
                
                const bolha = document.getElementById('alter-bolha');
                const msg = document.getElementById('alter-mensagem');
                const continuacao = document.getElementById('historia-continuacao');
                const ultimaFraseContainer = document.getElementById('ultima-frase');
                
                if (bolha && msg) {
                    msg.innerText = data.ultima_frase;
                    
                    // Esconde continuacao (só aparece quando precisa de tarefa)
                    if (continuacao) continuacao.style.display = 'none';
                    
                    // POSICIONAMENTO INTELIGENTE
                    const posicao = posicionarBalao(bolha, x, y, container);
                    bolha.style.left = posicao.x + 'px';
                    bolha.style.top = posicao.y + 'px';
                    bolha.style.display = 'block';
                }
                
                if (ultimaFraseContainer) {
                    ultimaFraseContainer.innerText = data.ultima_frase;
                }
                
                // Remove balão após 8 segundos
                if (fraseTimeout) clearTimeout(fraseTimeout);
                fraseTimeout = setTimeout(() => {
                    const bolha = document.getElementById('alter-bolha');
                    if (bolha) bolha.style.display = 'none';
                }, 8000);
            }
            
            // ===== 6. INTERAÇÃO AO CLICAR NO PERSONAGEM =====
            personagem.onclick = function() {
                fetch('/api/alterego/historia')
                    .then(response => response.json())
                    .then(historiaData => {
                        const bolha = document.getElementById('alter-bolha');
                        const msg = document.getElementById('alter-mensagem');
                        const continuacao = document.getElementById('historia-continuacao');
                        
                        if (bolha && msg) {
                            msg.innerText = historiaData.frase;
                            
                            // Mostra continuacao se precisar de tarefa
                            if (continuacao) {
                                continuacao.style.display = historiaData.precisa_tarefa ? 'block' : 'none';
                            }
                            
                            // POSICIONAMENTO INTELIGENTE PARA CLIQUE
                            const posicao = posicionarBalao(bolha, x, y, container);
                            bolha.style.left = posicao.x + 'px';
                            bolha.style.top = posicao.y + 'px';
                            bolha.style.display = 'block';
                            
                            // Remove balão após 10 segundos
                            setTimeout(() => {
                                bolha.style.display = 'none';
                            }, 10000);
                        }
                        
                        // Atualiza última frase
                        const ultimaFraseContainer = document.getElementById('ultima-frase');
                        if (ultimaFraseContainer) {
                            ultimaFraseContainer.innerText = historiaData.frase;
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao buscar história:', error);
                        const bolha = document.getElementById('alter-bolha');
                        const msg = document.getElementById('alter-mensagem');
                        if (bolha && msg) {
                            msg.innerText = 'Oops... Tente novamente!';
                            const posicao = posicionarBalao(bolha, x, y, container);
                            bolha.style.left = posicao.x + 'px';
                            bolha.style.top = posicao.y + 'px';
                            bolha.style.display = 'block';
                            setTimeout(() => {
                                bolha.style.display = 'none';
                            }, 3000);
                        }
                    });
            };
        })
        .catch(error => console.error('Erro ao atualizar Serumaninho:', error));
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
    installButton.innerText = '📲 INSTALAR APP';
    installButton.style.cssText = `
        position: fixed;
        bottom: 90px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 2000;
        background: #ffd700;
        color: #1a2f3f;
        border: 4px solid #8b4513;
        border-radius: 0;
        padding: 15px 25px;
        font-size: 1rem;
        font-family: 'Press Start 2P', cursive;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 8px 8px 0 #1a2f3f;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: pulsePixel 2s infinite;
        text-transform: uppercase;
        letter-spacing: 2px;
    `;
    
    installButton.addEventListener('click', () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('Usuário instalou o app');
                // Mostra mensagem de agradecimento
                const msg = document.createElement('div');
                msg.innerText = '🎉 OBRIGADO POR INSTALAR!';
                msg.style.cssText = `
                    position: fixed;
                    bottom: 160px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #2a5a3a;
                    color: #ffd700;
                    border: 4px solid #ffd700;
                    padding: 15px 25px;
                    border-radius: 0;
                    z-index: 2000;
                    font-family: 'Press Start 2P', cursive;
                    font-size: 0.7rem;
                    box-shadow: 8px 8px 0 #1a2f3f;
                    text-align: center;
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
// ANIMAÇÕES PIXELADAS
// ========================================

// Adiciona estilo de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes pulsePixel {
        0%, 100% { transform: translateX(-50%) scale(1); }
        50% { transform: translateX(-50%) scale(1.05); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-50%, -55%) scale(1.02); }
    }
    
    @keyframes fadeInPop {
        0% { opacity: 0; transform: translateX(-50%) scale(0.8); }
        100% { opacity: 1; transform: translateX(-50%) scale(1); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
        25% { transform: translate(-52%, -50%) rotate(-2deg); }
        75% { transform: translate(-48%, -50%) rotate(2deg); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Humores pixelados */
    .humor-feliz { filter: drop-shadow(0 0 12px gold); }
    .humor-animado { filter: drop-shadow(0 0 15px orange); animation: bounce 0.5s infinite !important; }
    .humor-cansado { filter: grayscale(0.5) drop-shadow(0 0 8px gray); opacity: 0.9; animation: bounce 4s infinite !important; }
    .humor-bravo { filter: drop-shadow(0 0 15px red); animation: shake 0.3s infinite !important; }
    .humor-misterioso { filter: drop-shadow(0 0 10px purple); }
    .humor-nostalgico { filter: sepia(0.3) drop-shadow(0 0 10px #8B4513); }
    .humor-divertido { filter: drop-shadow(0 0 12px #FF69B4); }
    .humor-triste { filter: grayscale(0.7) drop-shadow(0 0 8px blue); opacity: 0.8; }
    .humor-calmo { filter: drop-shadow(0 0 10px #87CEEB); }
    .humor-filosofico { filter: drop-shadow(0 0 12px #708090); }
    .humor-carinhoso { filter: drop-shadow(0 0 15px pink); }
`;
document.head.appendChild(style);

// ========================================
// INICIALIZAÇÃO
// ========================================

// Inicia a atualização quando a página carrega
if (document.getElementById('casa-container')) {
    // Primeira atualização após 500ms
    setTimeout(atualizarSerumaninho, 500);
    
    // Atualiza a cada 3 segundos
    setInterval(atualizarSerumaninho, 3000);
}

// Atualiza posição ao redimensionar a janela
window.addEventListener('resize', function() {
    if (document.getElementById('casa-container')) {
        atualizarSerumaninho();
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
    offlineMsg.innerText = '📴 MODO OFFLINE ATIVADO';
    offlineMsg.style.cssText = `
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: #8b0000;
        color: #ffd700;
        border: 4px solid #ffd700;
        padding: 10px 20px;
        border-radius: 0;
        z-index: 2000;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.6rem;
        box-shadow: 8px 8px 0 #1a2f3f;
        text-align: center;
    `;
    document.body.appendChild(offlineMsg);
    setTimeout(() => offlineMsg.remove(), 5000);
});

window.addEventListener('online', () => {
    const onlineMsg = document.createElement('div');
    onlineMsg.innerText = '📶 CONEXÃO RESTABELECIDA';
    onlineMsg.style.cssText = `
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: #2a5a3a;
        color: #ffd700;
        border: 4px solid #ffd700;
        padding: 10px 20px;
        border-radius: 0;
        z-index: 2000;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.6rem;
        box-shadow: 8px 8px 0 #1a2f3f;
        text-align: center;
    `;
    document.body.appendChild(onlineMsg);
    setTimeout(() => onlineMsg.remove(), 3000);
});
// ========================================
// SERUMANINHO - FUNÇÃO COMPLETA
// ========================================

let ultimaFrase = '';
let fraseTimeout;
let ultimaPosicao = { x: 0, y: 0 };
let tentativasReposicionamento = 0;

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
                    
                    // ===== POSICIONAMENTO INTELIGENTE DO BALÃO =====
                    const containerRect = container.getBoundingClientRect();
                    const bolhaWidth = 300; // Largura máxima
                    const bolhaHeight = 150; // Altura aproximada
                    
                    // Calcula posição X (nunca sai da tela)
                    let bolhaX = x;
                    const margem = 20;
                    
                    if (bolhaX - bolhaWidth/2 < margem) {
                        bolhaX = bolhaWidth/2 + margem;
                    } else if (bolhaX + bolhaWidth/2 > containerWidth - margem) {
                        bolhaX = containerWidth - bolhaWidth/2 - margem;
                    }
                    
                    // Calcula posição Y (tenta em cima, se não couber, coloca embaixo)
                    let bolhaY = y - 80; // 80px acima
                    const espacoEmCima = y - bolhaHeight;
                    const espacoEmBaixo = containerHeight - (y + 50);
                    
                    if (espacoEmCima < 20 && espacoEmBaixo > bolhaHeight) {
                        bolhaY = y + 60; // Coloca embaixo
                        // Ajusta a seta para baixo
                        const seta = bolha.querySelector('div:first-child');
                        if (seta) {
                            seta.style.bottom = 'auto';
                            seta.style.top = '-15px';
                            seta.style.borderTop = 'none';
                            seta.style.borderBottom = '15px solid #764ba2';
                        }
                    } else {
                        // Volta seta para cima se necessário
                        const seta = bolha.querySelector('div:first-child');
                        if (seta) {
                            seta.style.bottom = '-15px';
                            seta.style.top = 'auto';
                            seta.style.borderTop = '15px solid #764ba2';
                            seta.style.borderBottom = 'none';
                        }
                    }
                    
                    bolha.style.left = bolhaX + 'px';
                    bolha.style.top = bolhaY + 'px';
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
                            
                            // ===== POSICIONAMENTO PARA CLIQUE =====
                            const containerRect = container.getBoundingClientRect();
                            const bolhaWidth = 300;
                            
                            let bolhaX = x;
                            const margem = 20;
                            
                            if (bolhaX - bolhaWidth/2 < margem) {
                                bolhaX = bolhaWidth/2 + margem;
                            } else if (bolhaX + bolhaWidth/2 > containerWidth - margem) {
                                bolhaX = containerWidth - bolhaWidth/2 - margem;
                            }
                            
                            let bolhaY = y - 80;
                            const espacoEmCima = y - 150;
                            const espacoEmBaixo = containerHeight - (y + 50);
                            
                            if (espacoEmCima < 20 && espacoEmBaixo > 150) {
                                bolhaY = y + 60;
                                const seta = bolha.querySelector('div:first-child');
                                if (seta) {
                                    seta.style.bottom = 'auto';
                                    seta.style.top = '-15px';
                                    seta.style.borderTop = 'none';
                                    seta.style.borderBottom = '15px solid #764ba2';
                                }
                            } else {
                                const seta = bolha.querySelector('div:first-child');
                                if (seta) {
                                    seta.style.bottom = '-15px';
                                    seta.style.top = 'auto';
                                    seta.style.borderTop = '15px solid #764ba2';
                                    seta.style.borderBottom = 'none';
                                }
                            }
                            
                            bolha.style.left = bolhaX + 'px';
                            bolha.style.top = bolhaY + 'px';
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
// INICIALIZAÇÃO
// ========================================

// Inicia a atualização quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('casa-container')) {
        // Primeira atualização após 500ms
        setTimeout(atualizarSerumaninho, 500);
        
        // Atualiza a cada 3 segundos
        setInterval(atualizarSerumaninho, 3000);
    }
});

// Atualiza posição ao redimensionar a janela
window.addEventListener('resize', function() {
    if (document.getElementById('casa-container')) {
        atualizarSerumaninho();
    }
});
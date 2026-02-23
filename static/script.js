// Animações simples e interatividade
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

// Função para atualizar pontuação em tempo real (simulação)
function atualizarPontuacao() {
    const pontosRobo = document.querySelector('.robo .pontos');
    const pontosHumano = document.querySelector('.humano .pontos');
    
    if (pontosRobo && pontosHumano) {
        // Animação simples de mudança
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

// Chamar função quando uma tarefa for concluída
document.querySelectorAll('.tarefa-form').forEach(form => {
    form.addEventListener('submit', function() {
        setTimeout(atualizarPontuacao, 100);
    });
});

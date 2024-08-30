// script.js

function adjustMapSize() {
    const mapa = document.getElementById('mapa');
    if (mapa) {
        mapa.style.width = '100%';
        mapa.style.maxHeight = '500px';
    }
}

// Ajusta o tamanho do mapa quando a página carrega
window.onload = adjustMapSize;

// Ajusta o tamanho do mapa quando a janela é redimensionada
window.onresize = adjustMapSize;

let fontSize = 16; // Tamanho padrão da fonte

// Função para ajustar o tamanho do texto
function ajustarTamanhoTexto(ajuste) {
    fontSize += ajuste;
    const minSize = 14; // Tamanho mínimo da fonte
    const maxSize = 24; // Tamanho máximo da fonte

    if (fontSize < minSize) fontSize = minSize;
    if (fontSize > maxSize) fontSize = maxSize;

    // Aplicar o tamanho da fonte apenas aos filtros
    document.querySelectorAll('.filtros').forEach(el => {
        el.style.fontSize = `${fontSize}px`;
    });
}

// Função para resetar o tamanho do texto
function resetarTamanhoTexto() {
    fontSize = 16; // Tamanho padrão da fonte
    document.querySelectorAll('.filtros').forEach(el => {
        el.style.fontSize = `${fontSize}px`;
    });
}

// Adicionar eventos aos botões
document.getElementById('increase-text').addEventListener('click', () => ajustarTamanhoTexto(2));
document.getElementById('decrease-text').addEventListener('click', () => ajustarTamanhoTexto(-2));
document.getElementById('reset-text').addEventListener('click', resetarTamanhoTexto);

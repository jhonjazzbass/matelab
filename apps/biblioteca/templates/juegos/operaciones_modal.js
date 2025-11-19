// Global variables
let timeLeft = 30;
let timer;
let gameActive = true;
let canAnswer = true;

// Function to start the timer
function startTimer() {
    const timerElement = document.getElementById('timer');
    if (!timerElement) {
        console.error("Timer element not found");
        return;
    }

    clearInterval(timer);
    updateTimerDisplay();
    timer = setInterval(() => {
        if (timeLeft > 0) {
            timeLeft--;
            updateTimerDisplay();
        } else {
            clearInterval(timer);
            timeUp();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = `${timeLeft}s`;
        
        if (timeLeft <= 5) {
            timerElement.classList.add('text-danger', 'fw-bold');
            timerElement.style.animation = 'pulse 0.5s infinite';
        } else {
            timerElement.classList.remove('text-danger', 'fw-bold');
            timerElement.style.animation = 'none';
        }
    }
}

// Function to check the selected answer
window.checkAnswer = function(selectedIndex, correctIndex) {
    if (!canAnswer) return;
    
    canAnswer = false;
    clearInterval(timer);
    
    const buttons = document.querySelectorAll('.option-btn');
    const feedbackElement = document.getElementById('feedback');
    
    if (!feedbackElement) {
        console.error("Feedback element not found");
        return;
    }

    // Disable all buttons
    buttons.forEach(btn => {
        if (btn) btn.disabled = true;
    });
    
    // Highlight selected and correct answers
    if (selectedIndex === correctIndex) {
        if (buttons[selectedIndex]) buttons[selectedIndex].classList.add('correct');
        feedbackElement.textContent = "✅ ¡Respuesta correcta! ¡Buen trabajo!";
        feedbackElement.className = "text-success h4";
    } else {
        if (buttons[selectedIndex]) buttons[selectedIndex].classList.add('incorrect');
        if (buttons[correctIndex]) {
            buttons[correctIndex].classList.add('correct');
            feedbackElement.textContent = `❌ Incorrecto. La respuesta correcta es: ${buttons[correctIndex].textContent}`;
        } else {
            feedbackElement.textContent = "❌ Respuesta incorrecta";
        }
        feedbackElement.className = "text-danger h4";
    }
    
    // Show restart button
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.style.display = 'inline-block';
    }
};

function timeUp() {
    if (!canAnswer) return;
    
    canAnswer = false;
    const buttons = document.querySelectorAll('.option-btn');
    const feedbackElement = document.getElementById('feedback');
    
    if (!feedbackElement) {
        console.error("Feedback element not found");
        return;
    }

    // Disable all buttons
    buttons.forEach(btn => {
        if (btn) btn.disabled = true;
    });
    
    // Highlight the correct answer
    try {
        const correctIndex = {{ pregunta.respuesta_correcta|default:0 }};
        if (buttons[correctIndex]) {
            buttons[correctIndex].classList.add('correct');
            feedbackElement.textContent = "⏱️ ¡Tiempo agotado! La respuesta correcta está resaltada.";
            feedbackElement.className = "text-warning h4";
        }
    } catch (error) {
        console.error("Error getting correct answer:", error);
    }
    
    // Show restart button
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.style.display = 'inline-block';
    }
}

// Function to restart the game
window.restartGame = function() {
    // Reset game state
    timeLeft = 30;
    gameActive = true;
    canAnswer = true;
    
    // Reset UI
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(btn => {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('correct', 'incorrect');
        }
    });
    
    const feedbackElement = document.getElementById('feedback');
    if (feedbackElement) {
        feedbackElement.textContent = '';
        feedbackElement.className = '';
    }
    
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.style.display = 'none';
    }
    
    // Restart timer
    startTimer();
};

// Initialize the game when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Document loaded, starting timer...");
    startTimer();
});

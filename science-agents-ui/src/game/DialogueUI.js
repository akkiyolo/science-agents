export default class DialogueUI {
    constructor(scene) {
        this.scene = scene;
        this.isVisible = false;
        
        this.uiLayer = document.getElementById('ui-layer');
        this.dialogueText = document.getElementById('dialogue-text');
        this.dialogueInput = document.getElementById('dialogue-input');
        this.dialogueSend = document.getElementById('dialogue-send');
        this.dialogueName = document.getElementById('dialogue-name');
        
        this.currentNpc = null;
        this.websocket = null;
        this.playerId = "player_" + Math.floor(Math.random() * 10000);

        // Bind events
        this.dialogueSend.addEventListener('click', () => this.sendMessage());
        
        // Prevent Phaser from capturing keyboard events when typing in the input, but allow Escape to close
        this.dialogueInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.scene) this.scene.closeDialogue();
                else this.hide();
                return;
            }
            e.stopPropagation();
            if (e.key === 'Enter') this.sendMessage();
        });

        // Global Escape listener to close dialogue even when input is focused
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                if (this.scene) {
                    this.scene.closeDialogue();
                } else {
                    this.hide();
                }
            }
        });
    }

    show(npcId) {
        this.isVisible = true;
        this.currentNpc = npcId;
        this.dialogueName.innerText = npcId.toUpperCase();
        this.uiLayer.style.display = 'flex';
        this.dialogueText.innerHTML = `Approached ${npcId}...<br>`;
        this.dialogueInput.focus();
        
        // Speak Hello based on scientist
        this.speakHello(npcId);
        
        this.connectWebSocket(npcId);
    }

    speakHello(npcId) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance("Hello.");
            
            // Try to find matching voices
            const voices = window.speechSynthesis.getVoices();
            const femaleNames = ['curie', 'lovelace'];
            if (femaleNames.includes(npcId.toLowerCase())) {
                utterance.pitch = 1.8; // Higher pitch for female
                utterance.rate = 1.1;
                const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Samantha'));
                if (femaleVoice) utterance.voice = femaleVoice;
            } else {
                utterance.pitch = 0.8; // Lower pitch for male
                utterance.rate = 0.9;
                const maleVoice = voices.find(v => v.name.includes('Male') || v.name.includes('David') || v.name.includes('Alex'));
                if (maleVoice) utterance.voice = maleVoice;
            }
            
            window.speechSynthesis.speak(utterance);
        }
    }

    hide() {
        this.isVisible = false;
        this.uiLayer.style.display = 'none';
        this.currentNpc = null;
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    connectWebSocket(npcId) {
        const wsUrl = `ws://localhost:8000/ws/dialogue/${npcId}`;
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'token') {
                this.appendMessage(npcId, data.content, "#4CAF50");
            } else if (data.type === 'error') {
                this.appendMessage("Error", data.content, "#ff0000");
            }
        };
    }

    sendMessage() {
        const text = this.dialogueInput.value.trim();
        if (!text || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) return;

        this.appendMessage("You", text, "#fff");
        
        this.websocket.send(JSON.stringify({
            player_id: this.playerId,
            message: text
        }));
        
        this.dialogueInput.value = '';
    }

    appendMessage(sender, text, color) {
        const msg = document.createElement('div');
        msg.innerHTML = `<strong style="color: ${color}">${sender}:</strong> ${text}`;
        this.dialogueText.appendChild(msg);
        this.dialogueText.scrollTop = this.dialogueText.scrollHeight;
    }
}

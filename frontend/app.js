const API_BASE = "http://localhost:5000";
const state = {
    isOnline: false,
    isThinking: false,
    messageCount: 0,
    voiceListening: false,
    recognition: null,
};
const dom = {
    bootScreen:       document.getElementById("bootScreen"),
    bootStatus:       document.getElementById("bootStatus"),
    mainInterface:    document.getElementById("mainInterface"),
    chatMessages:     document.getElementById("chatMessages"),
    messageInput:     document.getElementById("messageInput"),
    sendBtn:          document.getElementById("sendBtn"),
    voiceBtn:         document.getElementById("voiceBtn"),
    clearBtn:         document.getElementById("clearBtn"),
    statusIcon:       document.getElementById("statusIcon"),
    statusText:       document.querySelector(".status-text"),
    clock:            document.getElementById("clock"),
    date:             document.getElementById("date"),
    cpuValue:         document.getElementById("cpuValue"),
    cpuBar:           document.getElementById("cpuBar"),
    ramValue:         document.getElementById("ramValue"),
    ramBar:           document.getElementById("ramBar"),
    diskValue:        document.getElementById("diskValue"),
    diskBar:          document.getElementById("diskBar"),
    latency:          document.getElementById("latency"),
    arcReactor:       document.querySelector(".arc-reactor"),
    audioRing:        document.getElementById("audioRing"),
    particleCanvas:   document.getElementById("particleCanvas"),
};
document.addEventListener('mousemove', (e) => {
    if (dom.bootScreen.style.display === 'none') {
        const x = (e.clientX - window.innerWidth / 2) / 60;
        const y = (e.clientY - window.innerHeight / 2) / 60;
        dom.mainInterface.style.transform = `rotateY(${x}deg) rotateX(${-y}deg)`;
    }
});
const NUM_BARS = 36;
const bars = [];
for (let i = 0; i < NUM_BARS; i++) {
    const bar = document.createElement("div");
    bar.classList.add("eq-bar");
    const angle = (i / NUM_BARS) * 360;
    bar.style.transform = `rotate(${angle}deg) translateY(-110px)`;
    dom.audioRing.appendChild(bar);
    bars.push(bar);
}
function animateEQ() {
    if (state.voiceListening || state.isThinking) {
        bars.forEach((bar, i) => {
            const time = Date.now() / 200;
            const height = 10 + Math.abs(Math.sin(i * 0.5 + time) * 30 * Math.random());
            bar.style.height = `${height}px`;
            bar.style.boxShadow = `0 0 ${height/2}px var(--cyan)`;
        });
    } else {
        bars.forEach(bar => {
            bar.style.height = '10px';
            bar.style.boxShadow = 'none';
        });
    }
    requestAnimationFrame(animateEQ);
}
animateEQ();
const bootMessages = [
    "Establishing secure connection to Stark Node...",
    "Recompiling Neural Matrix V2...",
    "Calibrating Particle Emitters...",
    "Injecting Cybernetics protocol...",
    "Rendering Holographic UI...",
    "F.R.I.D.A.Y ONLINE."
];
async function runBootSequence() {
    try { document.getElementById("snd-boot").play().catch(e=>console.log(e)); } catch(e){}
    for (let i = 0; i < bootMessages.length; i++) {
        dom.bootStatus.textContent = bootMessages[i];
        await sleep(400 + Math.random() * 300);
    }
    dom.bootScreen.classList.add("fade-out");
    dom.mainInterface.style.opacity = "1";
    await sleep(800);
    dom.bootScreen.style.display = "none";
    addMessage("friday", "Good day, Jackson. The V2 interface is loaded. Holographic projection and neural networks are fully operational.");
    startClock();
    startParticles();
    checkHealth();
    fetchStatus();
    setInterval(checkHealth, 15000);
    setInterval(fetchStatus, 10000);
}
function addMessage(type, text) {
    const typingEl = dom.chatMessages.querySelector(".typing-indicator");
    if (typingEl) typingEl.remove();
    const msg = document.createElement("div");
    msg.classList.add("message", type);
    let processedText = text
        .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--electric)">$1</strong>')
        .replace(/\*(.+?)\*/g, '<em style="color:var(--cyan)">$1</em>')
        .replace(/`(.+?)`/g, '<code style="background:rgba(0,255,255,0.1);padding:2px 6px;border-radius:4px;color:var(--gold);">$1</code>')
        .replace(/\n/g, '<br>');
    msg.innerHTML = processedText;
    dom.chatMessages.appendChild(msg);
    dom.chatMessages.parentElement.scrollTop = dom.chatMessages.parentElement.scrollHeight;
    state.messageCount++;
}
function showTypingIndicator() {
    const typing = document.createElement("div");
    typing.classList.add("typing-indicator");
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("div");
        dot.classList.add("typing-dot");
        typing.appendChild(dot);
    }
    dom.chatMessages.appendChild(typing);
    dom.chatMessages.parentElement.scrollTop = dom.chatMessages.parentElement.scrollHeight;
}
async function sendMessage() {
    const text = dom.messageInput.value.trim();
    if (!text || state.isThinking) return;
    addMessage("user", text);
    dom.messageInput.value = "";
    state.isThinking = true;
    dom.arcReactor.classList.add("thinking");
    showTypingIndicator();
    const startTime = performance.now();
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        dom.latency.textContent = `${Math.round(performance.now() - startTime)} ms`;
        if (response.ok) {
            addMessage("friday", data.response);
        } else {
            addMessage("friday", data.error || "Neural disconnect detected.");
        }
    } catch (err) {
        addMessage("friday", "Connection lost with the local core.");
    }
    state.isThinking = false;
    dom.arcReactor.classList.remove("thinking");
}
function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    state.recognition = new SpeechRecognition();
    state.recognition.continuous = false;
    state.recognition.interimResults = false;
    state.recognition.onresult = (e) => {
        dom.messageInput.value = e.results[0][0].transcript;
        sendMessage();
    };
    state.recognition.onstart = () => {
        state.voiceListening = true;
        dom.voiceBtn.classList.add("active");
    };
    state.recognition.onend = () => {
        state.voiceListening = false;
        dom.voiceBtn.classList.remove("active");
    };
}
function toggleVoice() {
    if (!state.recognition) return;
    state.voiceListening ? state.recognition.stop() : state.recognition.start();
}
document.querySelectorAll(".btn-hologram").forEach(btn => {
    btn.addEventListener("click", () => {
        const command = btn.dataset.command;
        if (command) {
            dom.messageInput.value = command;
            sendMessage();
        }
    });
});
dom.clearBtn.addEventListener("click", async () => {
    try {
        await fetch(`${API_BASE}/clear`, { method: "POST" });
        dom.chatMessages.innerHTML = "";
        addMessage("friday", "Memory flushed. Beginning new neural session.");
    } catch (err) {}
});
async function checkHealth() {
    try {
        await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
        dom.statusIcon.textContent = "⚡";
        dom.statusIcon.style.color = "var(--green-ok)";
        dom.statusText.textContent = "SECURE";
        dom.statusText.style.color = "var(--cyan)";
    } catch (err) {
        dom.statusIcon.textContent = "⚠️";
        dom.statusIcon.style.color = "var(--red-alert)";
        dom.statusText.textContent = "OFFLINE";
        dom.statusText.style.color = "var(--red-alert)";
    }
}
async function fetchStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`, { signal: AbortSignal.timeout(3000) });
        const data = await res.json();
        if (data.system && !data.system.error) {
            const cpu = parseFloat(data.system.cpu_usage) || 0;
            const ram = parseFloat(data.system.ram_percent) || 0;
            const disk = parseFloat(data.system.disk_percent) || 0;
            dom.cpuValue.textContent = data.system.cpu_usage;
            dom.cpuBar.style.width = cpu + "%";
            dom.ramValue.textContent = `${data.system.ram_used} / ${data.system.ram_total}`;
            dom.ramBar.style.width = ram + "%";
            dom.diskValue.textContent = `${data.system.disk_used} / ${data.system.disk_total}`;
            dom.diskBar.style.width = disk + "%";
        }
    } catch(e){}
}
function startClock() {
    setInterval(() => {
        const now = new Date();
        dom.clock.textContent = now.toLocaleTimeString("en-US", { hour12: false });
        dom.date.textContent = now.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "short", day: "numeric" }).toUpperCase();
    }, 1000);
}
function startParticles() {
    const canvas = dom.particleCanvas;
    const ctx = canvas.getContext("2d");
    let particles = [];
    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.addEventListener("resize", resize);
    resize();
    for (let i = 0; i < 80; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            radius: Math.random() * 2
        });
    }
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "rgba(0, 243, 255, 0.4)";
        particles.forEach(p => {
            ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        });
        requestAnimationFrame(draw);
    }
    draw();
}
dom.messageInput.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
dom.sendBtn.addEventListener("click", sendMessage);
dom.voiceBtn.addEventListener("click", toggleVoice);
document.addEventListener("keydown", (e) => {
    if (e.target === dom.messageInput || e.ctrlKey || e.altKey || e.metaKey) return;
    if (e.key.length === 1) dom.messageInput.focus();
});
document.addEventListener("DOMContentLoaded", () => {
    initVoiceRecognition();
    runBootSequence();
});
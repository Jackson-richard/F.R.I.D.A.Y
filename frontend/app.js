/* ═══════════════════════════════════════════════════════════
   F.R.I.D.A.Y — JARVIS Interface Controller
   Connects to Flask backend on localhost:5000
   ═══════════════════════════════════════════════════════════ */

const API_BASE = "http://localhost:5000";

// ── State ──────────────────────────────────────────────────
const state = {
    isOnline: false,
    isThinking: false,
    messageCount: 0,
    sessionStart: Date.now(),
    voiceListening: false,
    recognition: null,
};

// ── DOM References ─────────────────────────────────────────
const dom = {
    bootScreen:       document.getElementById("bootScreen"),
    bootProgress:     document.getElementById("bootProgressBar"),
    bootStatus:       document.getElementById("bootStatus"),
    mainInterface:    document.getElementById("mainInterface"),
    chatMessages:     document.getElementById("chatMessages"),
    messageInput:     document.getElementById("messageInput"),
    sendBtn:          document.getElementById("sendBtn"),
    voiceBtn:         document.getElementById("voiceBtn"),
    clearBtn:         document.getElementById("clearBtn"),
    connectionStatus: document.getElementById("connectionStatus"),
    statusText:       null, // set later
    clock:            document.getElementById("clock"),
    date:             document.getElementById("date"),
    cpuValue:         document.getElementById("cpuValue"),
    cpuBar:           document.getElementById("cpuBar"),
    ramValue:         document.getElementById("ramValue"),
    ramBar:           document.getElementById("ramBar"),
    diskValue:        document.getElementById("diskValue"),
    diskBar:          document.getElementById("diskBar"),
    aiProvider:       document.getElementById("aiProvider"),
    aiModel:          document.getElementById("aiModel"),
    aiStatus:         document.getElementById("aiStatus"),
    voiceStatus:      document.getElementById("voiceStatus"),
    msgCount:         document.getElementById("msgCount"),
    sessionTime:      document.getElementById("sessionTime"),
    latency:          document.getElementById("latency"),
    arcReactor:       document.querySelector(".arc-reactor"),
    reactorLabel:     document.querySelector(".reactor-label"),
    voiceVisualizer:  document.getElementById("voiceVisualizer"),
    particleCanvas:   document.getElementById("particleCanvas"),
};

dom.statusText = dom.connectionStatus.querySelector(".status-text");

// ═══════════════════════════════════════════════════════════
//  BOOT SEQUENCE
// ═══════════════════════════════════════════════════════════

const bootMessages = [
    "Initializing core systems...",
    "Loading neural network pathways...",
    "Establishing secure connection...",
    "Calibrating voice interface...",
    "Syncing system diagnostics...",
    "Loading personality matrix...",
    "Verifying AI provider status...",
    "Initializing HUD components...",
    "System check complete.",
    "F.R.I.D.A.Y is online."
];

async function runBootSequence() {
    for (let i = 0; i < bootMessages.length; i++) {
        const progress = ((i + 1) / bootMessages.length) * 100;
        dom.bootProgress.style.width = progress + "%";
        dom.bootStatus.textContent = bootMessages[i];
        await sleep(350 + Math.random() * 250);
    }

    await sleep(600);

    // Fade out boot screen
    dom.bootScreen.classList.add("fade-out");
    dom.mainInterface.classList.remove("hidden");

    await sleep(800);
    dom.bootScreen.style.display = "none";

    // Add greeting message
    addMessage("friday", "Good day, Jackson. F.R.I.D.A.Y is online and fully operational. All systems nominal. How may I assist you today?");

    // Start background tasks
    startClock();
    startParticles();
    checkHealth();
    fetchStatus();
    setInterval(checkHealth, 15000);
    setInterval(fetchStatus, 10000);
    setInterval(updateSessionTime, 1000);
}

// ═══════════════════════════════════════════════════════════
//  CHAT SYSTEM
// ═══════════════════════════════════════════════════════════

function addMessage(type, text) {
    // Remove typing indicator if present
    const typingEl = dom.chatMessages.querySelector(".typing-indicator");
    if (typingEl) typingEl.remove();

    const msg = document.createElement("div");
    msg.classList.add("message", type);
    
    // Process markdown-like formatting
    let processedText = text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code style="background:rgba(0,229,255,0.1);padding:2px 6px;border-radius:3px;font-family:var(--font-mono);color:var(--electric);">$1</code>')
        .replace(/\n/g, '<br>');
    
    msg.innerHTML = processedText;
    dom.chatMessages.appendChild(msg);
    
    // Scroll to bottom
    dom.chatMessages.parentElement.scrollTop = dom.chatMessages.parentElement.scrollHeight;
    
    // Update count
    state.messageCount++;
    dom.msgCount.textContent = state.messageCount;
}

function addSystemMessage(text) {
    const msg = document.createElement("div");
    msg.classList.add("message", "system");
    msg.textContent = text;
    dom.chatMessages.appendChild(msg);
    dom.chatMessages.parentElement.scrollTop = dom.chatMessages.parentElement.scrollHeight;
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

    // Add user message
    addMessage("user", text);
    dom.messageInput.value = "";

    // Set thinking state
    state.isThinking = true;
    dom.arcReactor.classList.add("thinking");
    dom.reactorLabel.textContent = "PROCESSING QUERY...";
    showTypingIndicator();

    const startTime = performance.now();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        const latency = Math.round(performance.now() - startTime);
        dom.latency.textContent = latency;

        if (response.ok) {
            addMessage("friday", data.response);
        } else {
            addMessage("friday", data.error || "I encountered an issue processing that request, Jackson.");
        }
    } catch (err) {
        addMessage("friday", "Connection lost with the backend, Jackson. Please ensure the server is running on port 5000.");
        console.error("[FRIDAY] Chat error:", err);
    }

    // Reset state
    state.isThinking = false;
    dom.arcReactor.classList.remove("thinking");
    dom.reactorLabel.textContent = "NEURAL CORE ACTIVE";
}

// ═══════════════════════════════════════════════════════════
//  QUICK ACTIONS
// ═══════════════════════════════════════════════════════════

document.querySelectorAll(".action-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const command = btn.dataset.command;
        if (command) {
            dom.messageInput.value = command;
            sendMessage();
        }
    });
});

// ═══════════════════════════════════════════════════════════
//  VOICE INPUT (Web Speech API)
// ═══════════════════════════════════════════════════════════

function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("[FRIDAY] Speech recognition not supported in this browser.");
        dom.voiceBtn.style.display = "none";
        return;
    }

    state.recognition = new SpeechRecognition();
    state.recognition.continuous = false;
    state.recognition.interimResults = false;
    state.recognition.lang = "en-US";

    state.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        dom.messageInput.value = transcript;
        sendMessage();
    };

    state.recognition.onstart = () => {
        state.voiceListening = true;
        dom.voiceBtn.classList.add("active");
        dom.voiceVisualizer.classList.remove("hidden");
    };

    state.recognition.onend = () => {
        state.voiceListening = false;
        dom.voiceBtn.classList.remove("active");
        dom.voiceVisualizer.classList.add("hidden");
    };

    state.recognition.onerror = (event) => {
        console.error("[FRIDAY] Voice error:", event.error);
        state.voiceListening = false;
        dom.voiceBtn.classList.remove("active");
        dom.voiceVisualizer.classList.add("hidden");
    };
}

function toggleVoice() {
    if (!state.recognition) {
        addSystemMessage("Voice recognition not available in this browser. Use Chrome for best results.");
        return;
    }

    if (state.voiceListening) {
        state.recognition.stop();
    } else {
        state.recognition.start();
    }
}

// ═══════════════════════════════════════════════════════════
//  CLEAR MEMORY
// ═══════════════════════════════════════════════════════════

async function clearMemory() {
    try {
        const res = await fetch(`${API_BASE}/clear`, { method: "POST" });
        const data = await res.json();
        addSystemMessage("[ MEMORY CLEARED — CONVERSATION RESET ]");
        
        // Clear visual chat
        dom.chatMessages.innerHTML = "";
        state.messageCount = 0;
        dom.msgCount.textContent = "0";
        
        addMessage("friday", "Memory banks purged, Jackson. Starting fresh.");
    } catch (err) {
        addSystemMessage("Failed to clear memory — server may be offline.");
    }
}

// ═══════════════════════════════════════════════════════════
//  HEALTH CHECK & STATUS
// ═══════════════════════════════════════════════════════════

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
        const data = await res.json();

        state.isOnline = true;
        dom.connectionStatus.className = "status-pill online";
        dom.statusText.textContent = "ONLINE";

        if (data.voice) {
            dom.voiceStatus.textContent = data.voice.toUpperCase();
        }
    } catch (err) {
        state.isOnline = false;
        dom.connectionStatus.className = "status-pill offline";
        dom.statusText.textContent = "OFFLINE";
    }
}

async function fetchStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`, { signal: AbortSignal.timeout(5000) });
        const data = await res.json();

        // AI status
        if (data.ai) {
            dom.aiProvider.textContent = (data.ai.provider || "—").toUpperCase();
            dom.aiModel.textContent = (data.ai.model || "—").split("/").pop();
            dom.aiStatus.textContent = (data.ai.status || "—").toUpperCase();
            dom.aiStatus.className = "ai-stat-value" + (data.ai.status === "online" ? " online" : "");
        }

        // System stats
        if (data.system && !data.system.error) {
            const cpu = parseFloat(data.system.cpu_usage) || 0;
            const ram = parseFloat(data.system.ram_percent) || 0;
            const disk = parseFloat(data.system.disk_percent) || 0;

            dom.cpuValue.textContent = data.system.cpu_usage;
            dom.cpuBar.style.width = cpu + "%";
            setBarClass(dom.cpuBar, cpu);

            dom.ramValue.textContent = `${data.system.ram_used} / ${data.system.ram_total}`;
            dom.ramBar.style.width = ram + "%";
            setBarClass(dom.ramBar, ram);

            dom.diskValue.textContent = `${data.system.disk_used} / ${data.system.disk_total}`;
            dom.diskBar.style.width = disk + "%";
            setBarClass(dom.diskBar, disk);
        }
    } catch (err) {
        // Silently fail — health check covers offline state
    }
}

function setBarClass(bar, value) {
    bar.classList.remove("warning", "critical");
    if (value > 85) bar.classList.add("critical");
    else if (value > 65) bar.classList.add("warning");
}

// ═══════════════════════════════════════════════════════════
//  CLOCK & SESSION TIMER
// ═══════════════════════════════════════════════════════════

function startClock() {
    function tick() {
        const now = new Date();
        dom.clock.textContent = now.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: true
        });
        dom.date.textContent = now.toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "short",
            day: "numeric"
        }).toUpperCase();
    }
    tick();
    setInterval(tick, 1000);
}

function updateSessionTime() {
    const elapsed = Math.floor((Date.now() - state.sessionStart) / 1000);
    const hrs = Math.floor(elapsed / 3600);
    const mins = Math.floor((elapsed % 3600) / 60);
    const secs = elapsed % 60;
    
    if (hrs > 0) {
        dom.sessionTime.textContent = `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
    } else {
        dom.sessionTime.textContent = `${pad(mins)}:${pad(secs)}`;
    }
}

function pad(n) { return n.toString().padStart(2, "0"); }

// ═══════════════════════════════════════════════════════════
//  PARTICLE SYSTEM (Background Ambience)
// ═══════════════════════════════════════════════════════════

function startParticles() {
    const canvas = dom.particleCanvas;
    const ctx = canvas.getContext("2d");
    let particles = [];
    const PARTICLE_COUNT = 60;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            radius: Math.random() * 1.5 + 0.5,
            alpha: Math.random() * 0.4 + 0.1,
        };
    }

    function init() {
        resize();
        particles = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            particles.push(createParticle());
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw particles
        for (const p of particles) {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 229, 255, ${p.alpha})`;
            ctx.fill();
        }

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 229, 255, ${0.08 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        // Update positions
        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener("resize", resize);
    init();
    draw();
}

// ═══════════════════════════════════════════════════════════
//  EVENT LISTENERS
// ═══════════════════════════════════════════════════════════

// Send on Enter
dom.messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button
dom.sendBtn.addEventListener("click", sendMessage);

// Voice button
dom.voiceBtn.addEventListener("click", toggleVoice);

// Clear memory
dom.clearBtn.addEventListener("click", clearMemory);

// Focus input on key press
document.addEventListener("keydown", (e) => {
    // Don't capture if user is in input or a modifier key is held
    if (e.target === dom.messageInput || e.ctrlKey || e.altKey || e.metaKey) return;
    
    // Focus input for regular character keys
    if (e.key.length === 1) {
        dom.messageInput.focus();
    }
});

// ═══════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ═══════════════════════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    initVoiceRecognition();
    runBootSequence();
});

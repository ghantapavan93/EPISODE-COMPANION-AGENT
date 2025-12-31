// Episode configuration
const EPISODE_ID = 'ai-research-daily-2025-11-18';

console.log('🚀 app.js starting execution...');

// Define global variables first
let currentMode = 'plain_english';
let apiClient = null;
let modal, chatArea, queryInput;

// NOTE: APIClient and APIError are loaded from api-client.js
// Do NOT redeclare them here to avoid "Identifier already declared" errors

// --- Core Functions ---

function openModal() {
    console.log('🔓 openModal called');
    modal = document.getElementById('modalOverlay');
    if (modal) {
        // Multiple approaches to ensure modal displays
        modal.classList.add('visible');
        modal.style.display = 'flex';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';

        // Force reflow to ensure styles are applied
        void modal.offsetHeight;

        console.log('✅ Modal should now be visible');
        console.log('Modal styles:', {
            display: modal.style.display,
            visibility: modal.style.visibility,
            opacity: modal.style.opacity
        });

        queryInput = document.getElementById('queryInput');
        if (queryInput) {
            setTimeout(() => queryInput.focus(), 300);
        }
    } else {
        console.error('❌ Modal element #modalOverlay not found!');
    }
}

function closeModal() {
    console.log('🔒 closeModal called');
    modal = document.getElementById('modalOverlay');
    if (modal) {
        modal.classList.remove('visible');
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        modal.style.opacity = '0';
    }
}

function setMode(mode, element) {
    currentMode = mode;
    const chips = document.querySelectorAll('.mode-chip');
    chips.forEach(chip => chip.classList.remove('active'));
    if (element) {
        element.classList.add('active');
    }
    console.log(`Mode changed to: ${mode}`);
}

function askAboutPaper(paperTitle) {
    openModal();
    queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = `Tell me more about "${paperTitle}"`;
    }
    setTimeout(() => handleSend(), 100);
}

function sendQuickPrompt(text) {
    openModal();
    queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = text;
        setTimeout(() => handleSend(), 150);
    }
}

// ============================================
// TODAY'S SHOW ENHANCED FUNCTIONS
// ============================================

// Surprise me - random interesting question
const surprisePrompts = [
    "What's the most surprising insight from today's episode?",
    "If I had to explain P1 to a 10-year-old, how would I do it?",
    "What's the one thing from this episode that could change how I think about AI?",
    "Give me the hot take version of today's papers.",
    "What would Andrej Karpathy say about these papers?",
    "If I were pitching this research to a VC, what would be my 30-second hook?",
    "What's the contrarian view on the P1 paper?",
    "How do these three papers connect to each other?",
    "What's the most overrated and underrated aspect of today's research?",
    "Pretend you're a skeptical reviewer - what would you criticize?",
];

function sendSurprisePrompt() {
    const randomPrompt = surprisePrompts[Math.floor(Math.random() * surprisePrompts.length)];
    sendQuickPrompt(randomPrompt);
}

// Set persona mode from pills
let selectedPersona = 'Plain English';

function setPersonaMode(mode) {
    selectedPersona = mode;
    // Map to API mode format
    const modeMap = {
        'Plain English': 'plain_english',
        'Founder': 'founder',
        'Engineer': 'engineer'
    };
    currentMode = modeMap[mode] || 'plain_english';
    
    // Update UI
    document.querySelectorAll('.persona-pill').forEach(pill => {
        pill.classList.remove('active');
        if (pill.dataset.mode === mode) {
            pill.classList.add('active');
        }
    });
    
    console.log(`🎭 Persona mode set to: ${mode} (API: ${currentMode})`);
}

// Copy episode summary to clipboard
function copyEpisodeSummary() {
    const summary = `🎙️ AI Research Daily - Today's Episode

📍 What you'll learn:
• How P1 beats physics Olympiads without hints using RL
• Why multi-agent communication costs matter at scale
• The trick to scaling spatial AI in 3D scenes

🔗 Listen & interact: ${window.location.href}

#AIResearch #MachineLearning #Kochi`;

    navigator.clipboard.writeText(summary).then(() => {
        // Show feedback
        const btn = event.target.closest('.action-chip');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        btn.style.background = 'rgba(16, 185, 129, 0.3)';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Share episode
function shareEpisode() {
    const shareData = {
        title: 'AI Research Daily - Episode',
        text: '🎙️ Check out today\'s AI Research Daily episode! Learn about P1 (physics Olympiad agent), multi-agent communication, and spatial intelligence.',
        url: window.location.href
    };

    if (navigator.share) {
        navigator.share(shareData).catch(console.error);
    } else {
        // Fallback: copy URL
        navigator.clipboard.writeText(window.location.href).then(() => {
            const btn = event.target.closest('.action-chip');
            const originalText = btn.innerHTML;
            btn.innerHTML = '✅ Link copied!';
            btn.style.background = 'rgba(16, 185, 129, 0.3)';
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '';
            }, 2000);
        });
    }
}

// Toggle transcript panel
function toggleTranscript() {
    const panel = document.getElementById('transcriptPanel');
    if (panel) {
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            panel.style.animation = 'staggerFadeIn 0.3s ease forwards';
        } else {
            panel.style.display = 'none';
        }
    }
}

// Initialize episode card enhancements
function initEpisodeCard() {
    // Speed pills functionality
    const speedPills = document.querySelectorAll('.speed-pill');
    const audio = document.getElementById('episodeAudio');
    
    speedPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const speed = parseFloat(pill.dataset.speed);
            if (audio) {
                audio.playbackRate = speed;
            }
            speedPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
        });
    });

    // Play button functionality
    const playBtn = document.getElementById('playBtnNew');
    if (playBtn && audio) {
        playBtn.addEventListener('click', () => {
            if (audio.paused) {
                audio.play();
                playBtn.querySelector('.play-icon').style.display = 'none';
                playBtn.querySelector('.pause-icon').style.display = 'block';
                // Animate waveform
                document.querySelectorAll('.waveform-bar').forEach(bar => {
                    bar.style.animationDuration = '0.4s';
                });
            } else {
                audio.pause();
                playBtn.querySelector('.play-icon').style.display = 'block';
                playBtn.querySelector('.pause-icon').style.display = 'none';
                // Slow down waveform
                document.querySelectorAll('.waveform-bar').forEach(bar => {
                    bar.style.animationDuration = '1.2s';
                });
            }
        });

        // Update time display
        audio.addEventListener('timeupdate', () => {
            const current = document.querySelector('.episode-time-current');
            if (current) {
                const mins = Math.floor(audio.currentTime / 60);
                const secs = Math.floor(audio.currentTime % 60);
                current.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Only if not typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        if (e.code === 'Space' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            if (playBtn) playBtn.click();
        }
        
        if (e.code === 'KeyI' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            openModal();
        }
    });

    console.log('✅ Episode card enhancements initialized');
}

// ============================================
// FUTURE OF KOCHI - LIVE DEMO ANIMATIONS
// ============================================

const builderPrompts = [
    "I've got a free weekend and like RL/agents. What should I build?",
    "Give me a visual, UI-heavy idea I can ship in two evenings.",
    "What's the smallest thing I can build that would help a research lab?"
];

let currentPromptIndex = 0;

function initFutureDemos() {
    // Start the builder typewriter demo
    startBuilderDemo();
    
    // Start mood button cycling
    startMoodCycling();
    
    // Start channel carousel
    startChannelCarousel();
    
    // Make flashcard clickable
    initFlashcardFlip();
    
    // Observe future bands for scroll animation
    observeFutureBands();
    
    console.log('✅ Future demos initialized');
}

function startBuilderDemo() {
    const typingElement = document.getElementById('builderTyping');
    if (!typingElement) return;
    
    const demoCard = typingElement.closest('.demo-builder');
    if (!demoCard) return;
    
    const thinking = demoCard.querySelector('.demo-thinking');
    const spec = demoCard.querySelector('.demo-spec');
    
    function runDemoLoop() {
        const prompt = builderPrompts[currentPromptIndex];
        typingElement.innerHTML = '<span class="typing-cursor">|</span>';
        
        // Show thinking, hide spec
        if (thinking) thinking.style.display = 'flex';
        if (spec) spec.style.display = 'none';
        
        // Type out the prompt
        let charIndex = 0;
        const typeInterval = setInterval(() => {
            if (charIndex < prompt.length) {
                typingElement.innerHTML = prompt.substring(0, charIndex + 1) + '<span class="typing-cursor">|</span>';
                charIndex++;
            } else {
                clearInterval(typeInterval);
                
                // After typing, show thinking for 2 seconds
                setTimeout(() => {
                    if (thinking) thinking.style.display = 'none';
                    if (spec) {
                        spec.style.display = 'block';
                        spec.style.animation = 'fadeSlideIn 0.4s ease forwards';
                    }
                    
                    // Wait 5 seconds then restart with next prompt
                    setTimeout(() => {
                        currentPromptIndex = (currentPromptIndex + 1) % builderPrompts.length;
                        runDemoLoop();
                    }, 5000);
                }, 2000);
            }
        }, 50);
    }
    
    // Start after a short delay
    setTimeout(runDemoLoop, 1000);
}

function startMoodCycling() {
    const moodBtns = document.querySelectorAll('.mood-btn');
    const moodQuote = document.querySelector('.mood-quote');
    
    if (!moodBtns.length || !moodQuote) return;
    
    const moods = [
        { mood: 'hype', quote: '"Give me the wildest frontier stuff. I\'ll forgive some hand-wavy bits."' },
        { mood: 'skeptical', quote: '"Focus on papers with strong evals, clear baselines, and real ablations."' },
        { mood: 'one', quote: '"Skip the chaos. One idea that\'s worth a walk."' }
    ];
    
    let moodIndex = 1; // Start with skeptical (already active)
    
    setInterval(() => {
        moodIndex = (moodIndex + 1) % moods.length;
        const current = moods[moodIndex];
        
        moodBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mood === current.mood);
        });
        
        moodQuote.textContent = current.quote;
    }, 4000);
}

function startChannelCarousel() {
    const cards = document.querySelectorAll('.channel-card');
    if (!cards.length) return;
    
    let activeIndex = 0;
    
    setInterval(() => {
        cards.forEach((card, i) => {
            card.classList.toggle('active', i === activeIndex);
        });
        activeIndex = (activeIndex + 1) % cards.length;
    }, 3000);
}

function initFlashcardFlip() {
    const flashcard = document.querySelector('.flashcard');
    if (!flashcard) return;
    
    flashcard.addEventListener('click', () => {
        // Toggle the animation
        if (flashcard.style.animationPlayState === 'paused') {
            flashcard.style.animationPlayState = 'running';
        } else {
            flashcard.style.animationPlayState = 'paused';
        }
    });
}

function observeFutureBands() {
    // Observe the section header
    const header = document.querySelector('.future-header');
    if (header) {
        const headerObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.2 });
        headerObserver.observe(header);
    }
    
    // Observe each band for staggered entrance
    const bands = document.querySelectorAll('.future-band');
    
    const bandObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Also trigger card animations with stagger
                const cards = entry.target.querySelectorAll('.future-card');
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.opacity = '1';
                    }, index * 150);
                });
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
    
    bands.forEach(band => bandObserver.observe(band));
}

function sendLearningPrompt(type) {
    queryInput = document.getElementById('queryInput');
    if (!queryInput) return;

    if (type === 'quiz') {
        queryInput.value = "Quiz me on this episode.";
    } else if (type === 'self_explain') {
        queryInput.value = "Let me explain this in my own words; tell me if I got it right: ";
        queryInput.focus();
        return;
    }
    handleSend();
}

async function handleSend() {
    chatArea = document.getElementById('chatArea');
    queryInput = document.getElementById('queryInput');

    if (!queryInput || !chatArea) {
        console.error("Chat area or input not found");
        return;
    }

    const query = queryInput.value.trim();
    if (!query) return;

    const sendBtn = document.querySelector('.send-btn');
    if (sendBtn) {
        sendBtn.classList.add('loading');
        sendBtn.disabled = true;
    }

    try {
        addMessage(query, 'user');
        queryInput.value = '';
        const typingIndicator = showTypingIndicator();

        if (!apiClient) apiClient = new APIClient();

        const response = await apiClient.query({
            message: query,
            mode: currentMode,
            episode_id: EPISODE_ID,
            user_profile: {
                role: window.userRoleInput ? window.userRoleInput.value.trim() : '',
                domain: window.userDomainInput ? window.userDomainInput.value.trim() : ''
            }
        });

        if (typingIndicator) typingIndicator.remove();
        addMessage(response.answer, 'agent');

        if (response.metadata && response.metadata.episode_time_hint) {
            const hint = response.metadata.episode_time_hint;
            if (hint.start_human && hint.end_human) {
                addMessage(`⏱ This part is around ${hint.start_human}–${hint.end_human} in the episode.`, 'system');
            }
        }

        if (response.metadata && response.metadata.suggested_followups) {
            renderFollowups(response.metadata.suggested_followups);
        }

    } catch (error) {
        const typingIndicator = chatArea.querySelector('.typing-indicator');
        if (typingIndicator) typingIndicator.remove();

        const errorMessage = error instanceof APIError
            ? error.getUserFriendlyMessage()
            : `Error: ${error.message}`;
        addMessage(errorMessage, 'agent');
        console.error('Query error:', error);
    } finally {
        if (sendBtn) {
            sendBtn.classList.remove('loading');
            sendBtn.disabled = false;
        }
    }
}

// --- Helper Functions ---

function addMessage(text, sender) {
    if (!chatArea) return;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    if (sender === 'agent') {
        messageDiv.innerHTML = text;
        addCopyButtonsToCodeBlocks(messageDiv);
    } else {
        messageDiv.textContent = text;
    }
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function addCopyButtonsToCodeBlocks(messageElement) {
    const codeBlocks = messageElement.querySelectorAll('pre.response-code-block');
    codeBlocks.forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.innerHTML = '📋 Copy';
        button.onclick = () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                button.innerHTML = '✅ Copied!';
                setTimeout(() => button.innerHTML = '📋 Copy', 2000);
            });
        };
        block.style.position = 'relative';
        block.appendChild(button);
    });
}

function showTypingIndicator() {
    if (!chatArea) return null;
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatArea.appendChild(indicator);
    chatArea.scrollTop = chatArea.scrollHeight;
    return indicator;
}

function renderFollowups(followups) {
    if (!followups || !chatArea) return;
    const container = document.createElement('div');
    Object.assign(container.style, { display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px', marginLeft: '16px' });

    followups.forEach(question => {
        const chip = document.createElement('div');
        chip.className = 'mode-chip';
        Object.assign(chip.style, { fontSize: '0.75rem', padding: '6px 12px', cursor: 'pointer' });
        chip.textContent = question;
        chip.onclick = () => {
            if (queryInput) {
                queryInput.value = question;
                handleSend();
                container.remove();
            }
        };
        container.appendChild(chip);
    });
    chatArea.appendChild(container);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function renderSmsRitualPhones(scenes, container) {
    const positionClasses = ['phone-left', 'phone-center', 'phone-right'];
    scenes.forEach((scene, index) => {
        const phone = document.createElement('div');
        phone.className = `kochi-ritual-phone ${positionClasses[index] || ''}`;
        phone.innerHTML = `
            <div class="phone-notch"></div>
            <div class="phone-header">
                <div class="phone-header-left">
                    <div class="phone-emoji-icon">${scene.emoji}</div>
                    <div class="phone-label-block">
                        <div class="phone-label">${scene.label}</div>
                        <div class="phone-tagline">${scene.tagline}</div>
                    </div>
                </div>
                <div class="phone-badge">SMS · Live</div>
            </div>
            <div class="phone-chat-body"></div>
        `;
        const chatBody = phone.querySelector('.phone-chat-body');
        container.appendChild(phone);
        startPhoneMessageCycle(chatBody, scene.messages);
    });
}

function startPhoneMessageCycle(chatBody, messages) {
    const render = () => {
        chatBody.innerHTML = '';
        messages.forEach((msg, index) => {
            setTimeout(() => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `phone-message ${msg.from === 'user' ? 'user-msg' : 'kochi-msg'}${msg.emphasis ? ' emphasis' : ''}`;
                msgDiv.textContent = msg.text;
                chatBody.appendChild(msgDiv);
                chatBody.scrollTop = chatBody.scrollHeight;
            }, index * 500);
        });
        setTimeout(() => {
            const typing = document.createElement('div');
            typing.className = 'phone-typing-indicator';
            typing.innerHTML = '<div class="typing-dots"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div><span class="typing-label">kochi is typing…</span>';
            chatBody.appendChild(typing);
            chatBody.scrollTop = chatBody.scrollHeight;
        }, messages.length * 500 + 1000);
    };
    render();
    setInterval(render, 15000);
}

// --- Initialization ---

function bindInteractiveButton(retryCount = 0) {
    const maxRetries = 10;
    const interactiveBtn = document.getElementById('interactiveBtn');

    if (interactiveBtn) {
        console.log('✅ Interactive button found, wiring click → openModal');
        interactiveBtn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('🎯 Interactive button clicked!');
            openModal();
        });
        return true;
    } else {
        if (retryCount < maxRetries) {
            console.log(`⏳ Interactive button not found, retrying... (${retryCount + 1}/${maxRetries})`);
            setTimeout(() => bindInteractiveButton(retryCount + 1), 100);
        } else {
            console.error('❌ Interactive button not found after ' + maxRetries + ' retries!');
        }
        return false;
    }
}

function initApp() {
    console.log('🛠 initApp called');
    apiClient = new APIClient();

    modal = document.getElementById('modalOverlay');
    chatArea = document.getElementById('chatArea');
    queryInput = document.getElementById('queryInput');
    window.userRoleInput = document.getElementById('userRoleInput');
    window.userDomainInput = document.getElementById('userDomainInput');

    // Try to bind the interactive button with retry logic
    bindInteractiveButton();

    if (window.kochiConfig) {
        populateContent();
    } else {
        console.warn('⚠️ window.kochiConfig is undefined');
    }

    setupEventListeners();
    setupScrollAnimations();
    initEpisodeCard();
    initFutureDemos();

    console.log('✅ Episode Companion initialized');
}

function populateContent() {
    const config = window.kochiConfig;
    if (!config) return;

    // SMS Pill
    const smsPill = document.getElementById('smsPill');
    if (smsPill) smsPill.innerHTML = config.KOCHI_SMS_NUMBER.replace('AI DAILY', '<span>AI DAILY</span>').replace('+1 (555) 000-0000', '<span>+1 (555) 000-0000</span>');

    // Audio
    const audio = document.getElementById('episodeAudio');
    if (audio) audio.innerHTML = `<source src="${config.AUDIO_FILE_PATH}" type="audio/mpeg">`;

    // Papers
    const papersList = document.getElementById('papersList');
    if (papersList && config.episodePapers) {
        papersList.innerHTML = config.episodePapers.map(p => `<li><span>${p.tag}</span> ${p.title} — <em style="opacity: 0.7">${p.authors}</em></li>`).join('');
    }

    // SMS Phones
    const smsCluster = document.getElementById('smsPhoneCluster');
    if (smsCluster && config.smsScenes) renderSmsRitualPhones(config.smsScenes, smsCluster);

    // Future Groups - Now using static HTML with live demos
    // The new "Future of Kochi" section is rendered statically in index.html
    // with animated demo containers for each card

    // Lens Conversations
    const lensCards = document.getElementById('lensConversationCards');
    if (lensCards && config.lensConversations) {
        lensCards.innerHTML = config.lensConversations.map(l => `
            <div class="kochi-conversation-card">
                <div class="kochi-conversation-header">
                    <div class="kochi-conversation-icon">${l.icon}</div>
                    <div class="kochi-conversation-title-block">
                        <div class="kochi-conversation-mode">${l.mode}</div>
                        <div class="kochi-conversation-oneliner">${l.oneLiner}</div>
                    </div>
                </div>
                <div class="kochi-transcript">
                    ${l.transcript.map(m => `<div class="kochi-transcript-bubble ${m.from === 'user' ? 'user-bubble' : 'kochi-bubble'}">${m.text}</div>`).join('')}
                </div>
                <div class="kochi-mode-tags">${l.modeTags.map(t => `<div class="kochi-mode-tag">${t}</div>`).join('')}</div>
            </div>
        `).join('');
    }
}

function setupEventListeners() {
    if (queryInput) {
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') closeModal();
    });
}

function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animated-section').forEach(s => observer.observe(s));
}

// --- Expose to Window ---
window.openModal = openModal;
window.closeModal = closeModal;
window.setMode = setMode;
window.handleSend = handleSend;
window.askAboutPaper = askAboutPaper;
window.sendLearningPrompt = sendLearningPrompt;
window.sendQuickPrompt = sendQuickPrompt;

// --- Run Init AFTER everything is fully loaded ---
console.log('📜 app.js loaded, waiting for page to be fully ready...');

// Use window.load instead of DOMContentLoaded to ensure EVERYTHING is loaded
window.addEventListener('load', function () {
    console.log('🚀 Window load event fired, calling initApp...');
    initApp();
});


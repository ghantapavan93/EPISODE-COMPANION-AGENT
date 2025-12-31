/**
 * Kochi Content Configuration
 * Centralized content for SMS scenes, future feature cards, and episode data
 */

// Configuration constants
const KOCHI_SMS_NUMBER = "Text AI DAILY to +1 (555) 000-0000";
const AUDIO_FILE_PATH = "/static/audio/ai-research-daily-sample.mp3";

// Episode papers configuration
const episodePapers = [
    {
        tag: "[Diffusion]",
        title: "Back to Basics: Let Denoising Generative Models Denoise",
        authors: "Tianhong Li, Kaiming He"
    },
    {
        tag: "[Multi-agent]",
        title: "Cost-Effective Communication",
        authors: "Yijia Fan, Keze Wang, et al."
    },
    {
        tag: "[Spatial]",
        title: "Scaling Spatial Intelligence",
        authors: "Zhongang Cai, et al."
    }
];

// SMS conversation scenes for ritual phones
const smsScenes = [
    {
        emoji: "🚇",
        label: "Commute ping",
        tagline: "Daily brief for your ride.",
        messages: [
            { from: "user", text: "ai daily", emphasis: true },
            { from: "kochi", text: "Here's today's 60-sec brief + audio link." },
            {
                from: "kochi",
                text: "Episode: \"Agents that don't melt at scale.\" Tap to listen, then text \"founder mode tldr\" or \"quiz me\"."
            },
            { from: "user", text: "founder mode tldr", emphasis: true },
            {
                from: "kochi",
                text: "One idea, who might pay, and a v0 spec you could ship this month."
            }
        ]
    },
    {
        emoji: "🌙",
        label: "Late-night build",
        tagline: "Keep your \"I'll ship it\" promise.",
        messages: [
            { from: "user", text: "just one idea today", emphasis: true },
            {
                from: "kochi",
                text: "Got it. I'll pick the most builder-friendly paper from this week."
            },
            {
                from: "kochi",
                text: "Idea: a \"research recap\" bot for your team Slack that turns today's paper into one concrete experiment."
            },
            { from: "user", text: "quiz me on the RL part", emphasis: true },
            {
                from: "kochi",
                text: "Okay, 5 questions. Let's see what stuck. (Q1/5)…"
            }
        ]
    },
    {
        emoji: "🧪",
        label: "Paper → prototype",
        tagline: "Weekend project starter.",
        messages: [
            {
                from: "user",
                text: "spin up a FastAPI starter from today's comms paper",
                emphasis: true
            },
            {
                from: "kochi",
                text: "Here's a tiny API skeleton + test data. Perfect weekend project."
            },
            {
                from: "kochi",
                text: "Includes: endpoints, sample payloads, and a 5-step README."
            },
            { from: "user", text: "send me a sanity-check checklist" },
            {
                from: "kochi",
                text: "Deal: 1) Does it run end-to-end? 2) Can you demo in 2 minutes? 3) Did you log at least one metric that matters?"
            }
        ]
    }
];

// Lens conversation examples
const lensConversations = [
    {
        icon: "🎙",
        mode: "Plain English",
        oneLiner: "Explain this like a 5-minute radio host. No math, just intuition.",
        transcript: [
            { from: "user", text: "I'm on a walk. Just tell me what this paper is about in normal words." },
            { from: "kochi", text: "Short version? They teach an AI to solve tough physics problems the way an Olympiad nerd would — but faster and without needing hints." },
            { from: "user", text: "Okay, what's the one idea I should remember after the walk?" },
            { from: "kochi", text: "Remember this: \"We can get competition-level problem solving out of models without making them huge — if we train them like students, not just giant calculators.\"" }
        ],
        modeTags: ["TL;DR", "Quiz"]
    },
    {
        icon: "🪐",
        mode: "Founder",
        oneLiner: "What could I build? Who pays? What's the moat and wedge?",
        transcript: [
            { from: "user", text: "Pretend I'm a scrappy founder. What's the smallest product I could ship from this paper?" },
            { from: "kochi", text: "A \"physics TA in a tab\" for competitive students: upload problems, get step-by-step hints instead of full solutions." },
            { from: "user", text: "Who actually pays for that?" },
            { from: "kochi", text: "Parents + schools with olympiad programs. Your wedge is \"fewer burnt-out tutors, more consistent practice\" —priced per student per season." },
            { from: "user", text: "What's the non-obvious moat if it works?" },
            { from: "kochi", text: "The dataset of real student mistakes and hint paths — not the model itself." }
        ],
        modeTags: ["Build", "Critique"]
    },
    {
        icon: "🧱",
        mode: "Engineer",
        oneLiner: "What code or architecture is worth stealing for a v0 implementation?",
        transcript: [
            {
                from: "user", text:

                    "I don't care about the storytelling. What's worth stealing in the actual setup?"
            },
            { from: "kochi", text: "They mix a small \"reasoning head\" with a larger base model, then only train the small head on competition problems — cheap but high impact." },
            { from: "user", text: "How would you implement a v0 of that with off-the-shelf models?" },
            { from: "kochi", text: "Start with a mid-sized open model, add a tiny classifier head that decides which scratch-pad steps to keep, and train it on curated Olympiad traces. No custom tokenizer, just smart data filters." },
            { from: "user", text: "If I only have a weekend, what part should I prototype?" },
            { from: "kochi", text: "Just the scratch-pad filter + evaluation. Prove you can beat \"plain CoT\" on 20–30 hand-picked problems." }
        ],
        modeTags: ["Build", "TL;DR"]
    }
];

// Power prompts
const powerPrompts = [
    { text: "Give me a 3-bullet TL;DR.", icon: "🎙" },
    { text: "What should I build from this?", icon: "🪐" },
    { text: "Quiz me on this episode.", icon: "🎙" },
    { text: "Let me explain, then critique me.", icon: "🧱" },
    { text: "Tell me what's actually new here.", icon: "🪐" },
    { text: "Compare this to last week's paper.", icon: "🧱" }
];

// Future feature groups
const futureGroups = [
    {
        title: "AFTER-SHOW PLAYGROUND",
        cards: [
            {
                tag: "Builder question",
                emoji: "🚀",
                title: "What should I build today?",
                description:
                    "Type one prompt. Kochi surfaces a single paper from this week and hands you a tiny, weekend-able v0 spec."
            },
            {
                tag: "Team share",
                emoji: "📨",
                title: "Send this to my team",
                description:
                    "Auto-compress an episode into a Slack/Discord-ready blurb with 3 bullets for founders, engineers, or researchers."
            },
            {
                tag: "Explain like I'm 15",
                emoji: "🧠",
                title: "No-math intuition mode",
                description:
                    "Turn any episode into a story you could tell a younger sibling — keeping the real insight, dropping the jargon."
            }
        ]
    },
    {
        title: "BUILDER TRACK",
        cards: [
            {
                tag: "Micro-prototype",
                emoji: "🛠️",
                title: "Build this idea",
                description:
                    "Once a week, Kochi spins up a tiny FastAPI + Next.js starter from one paper, with copy-paste deploy instructions."
            },
            {
                tag: "Playful UI",
                emoji: "🎛️",
                title: "Paper speed dating",
                description:
                    "Swipe through today's papers. Skip, get the 1-minute pitch, deep dive, or follow the author for future drops."
            },
            {
                tag: "Web toys",
                emoji: "🃏",
                title: "Flashcards & diagrams",
                description:
                    "Turn an episode into flashcards, quick diagrams, or memes you can drop into group chats and study notes."
            }
        ]
    },
    {
        title: "MEMORY & FOLLOW-THROUGH",
        cards: [
            {
                tag: "Signals",
                emoji: "🔔",
                title: "Follow this researcher",
                description:
                    "Tap an author. Kochi watches arXiv/X/Substack and pings you with a 2-minute breakdown when they publish."
            },
            {
                tag: "Taste profile",
                emoji: "🧬",
                title: "Your brain on Kochi",
                description:
                    "Kochi quietly learns what you skip, replay, and ask about, then tilts future episodes toward your obsessions."
            },
            {
                tag: "Mood",
                emoji: "🌡️",
                title: "Daily research mood",
                description:
                    "Choose Hype / Skeptical / Just one idea, and Kochi changes the tone and density of what it sends."
            }
        ]
    },
    {
        title: "CHANNELS & PLAYLISTS",
        cards: [
            {
                tag: "Channels",
                emoji: "📡",
                title: "More than one show",
                description:
                    "AI Research Daily today. Soon: Agents Underground, Crypto Risk Daily, Founder Memos — each with its own agent."
            },
            {
                tag: "Playlists",
                emoji: "🎧",
                title: "Spotify-for-research",
                description:
                    "Hit play on arcs like 'Efficiency Week', 'Benchmarks That Actually Mattered', or 'MoE Only'."
            },
            {
                tag: "Creator tools",
                emoji: "🧪",
                title: "Channel builder",
                description:
                    "Labs, funds, and writers plug in an RSS or arXiv feed and get their own Kochi show + after-show agent in minutes."
            }
        ]
    },
    {
        title: "KOCHI LABS EXPERIMENTS",
        cards: [
            {
                tag: "Voice",
                emoji: "📞",
                title: "Phone-in voice chat",
                description:
                    "Call a number and talk live with the agent while the episode plays in the background."
            },
            {
                tag: "Live",
                emoji: "🎥",
                title: "Watch-party mode",
                description:
                    "Listen to an episode with friends while Kochi drops questions and polls into the chat."
            },
            {
                tag: "Spice",
                emoji: "🔥",
                title: "Peer-review drama",
                description:
                    "A tongue-in-cheek mode that surfaces hot takes, critiques, and follow-ups to spicy new papers."
            }
        ]
    }
];

// Export for use in HTML
if (typeof window !== 'undefined') {
    window.kochiConfig = {
        KOCHI_SMS_NUMBER,
        AUDIO_FILE_PATH,
        episodePapers,
        smsScenes,
        futureGroups,
        lensConversations,
        powerPrompts
    };
}

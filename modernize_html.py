#!/usr/bin/env python3
"""
Script to create a streamlined index.html that uses external CSS/JS files
"""

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI Research Daily - Kochi Episode Companion">
    <title>Kochi | AI Research Daily</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
    
    <!-- External Stylesheets -->
    <link rel="stylesheet" href="/static/css/design-system.css">
    <link rel="stylesheet" href="/static/css/components.css">
    
    <!-- Page-Specific Styles (Minimal) -->
    <style>
        body {
            font-family: var(--font-sans);
            background-color: var(--neutral-50);
            color: var(--neutral-900);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 700px;
            padding: var(--space-10) var(--space-5);
            box-sizing: border-box;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: var(--space-10);
        }

        .header-subtitle {
            font-size: var(--text-xs);
            text-transform: uppercase;
            letter-spacing: var(--tracking-wider);
            color: var(--neutral-500);
            margin-bottom: var(--space-2);
            font-weight: var(--font-semibold);
        }

        h1 {
            font-family: var(--font-display);
            font-size: var(--text-4xl);
            margin: 0 0 var(--space-2) 0;
            color: var(--neutral-900);
        }

        .date {
            color: var(--neutral-500);
            font-size: var(--text-base);
        }

        /* Episode Card */
        .episode-card {
            background: white;
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-2xl);
            padding: var(--space-8);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--space-8);
        }

        .episode-title {
            font-family: var(--font-display);
            font-size: var(--text-2xl);
            margin-bottom: var(--space-4);
        }

        .episode-summary {
            line-height: var(--leading-relaxed);
            color: var(--neutral-600);
            margin-bottom: var(--space-6);
        }

        .player-controls {
            display: flex;
            align-items: center;
            gap: var(--space-4);
            margin-top: var(--space-6);
            padding-top: var(--space-6);
            border-top: 1px solid var(--neutral-200);
        }

        .play-btn {
            width: 48px;
            height: 48px;
            border-radius: var(--radius-full);
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-500) 100%);
            color: white;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: var(--text-xl);
            transition: all var(--duration-200) var(--ease-smooth);
        }

        .play-btn:hover {
            transform: scale(1.05);
            box-shadow: var(--shadow-primary);
        }

        .interactive-btn {
            flex: 1;
            background: var(--neutral-100);
            border: 1px solid var(--neutral-200);
            border-radius: var(--radius-xl);
            padding: var(--space-3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-2);
            cursor: pointer;
            font-weight: var(--font-medium);
            color: var(--neutral-900);
            transition: all var(--duration-200) var(--ease-smooth);
        }

        .interactive-btn:hover {
            background: var(--neutral-200);
            transform: translateY(-1px);
        }

        /* Papers Section */
        .section-title {
            font-family: var(--font-display);
            font-size: var(--text-xl);
            margin-bottom: var(--space-4);
            margin-top: var(--space-10);
        }

        .paper-item {
            margin-bottom: var(--space-6);
            padding-bottom: var(--space-6);
            border-bottom: 1px solid var(--neutral-200);
        }

        .paper-item:last-child {
            border-bottom: none;
        }

        .paper-title {
            font-weight: var(--font-semibold);
            margin-bottom: var(--space-1);
            color: var(--primary-600);
            text-decoration: none;
            display: block;
            transition: color var(--duration-200) var(--ease-smooth);
        }

        .paper-title:hover {
            color: var(--primary-700);
            text-decoration: underline;
        }

        .paper-meta {
            font-size: var(--text-sm);
            color: var(--neutral-500);
            margin-bottom: var(--space-2);
        }

        .paper-desc {
            font-size: var(--text-base);
            line-height: var(--leading-normal);
            color: var(--neutral-700);
        }
    </style>
</head>

<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-subtitle">Daily Report</div>
            <h1>ai-research-daily</h1>
            <div class="date">Mon 11/18/2025</div>
        </div>

        <!-- Episode Card -->
        <div class="episode-card">
            <h2 class="episode-title">AI Research Daily 11/18</h2>
            <div class="episode-summary">
                🎙️ Learn how reinforcement learning masters Physics Olympiads in "P1"! Stay tuned for more AI insights
                and research summaries in today's AI Papers Daily.
            </div>

            <div class="player-controls">
                <button class="play-btn" aria-label="Play episode">▶</button>
                <div style="flex: 1; height: 4px; background: #eee; border-radius: 2px; position: relative;">
                    <div style="width: 30%; height: 100%; background: #ccc; border-radius: 2px;"></div>
                </div>
                <div style="font-size: 0.8rem; color: #666;">04:28</div>
            </div>

            <div style="margin-top: 16px;">
                <button class="interactive-btn" onclick="openModal()" aria-label="Open interactive mode">
                    <span>🎤</span> Interactive mode
                </button>
            </div>
        </div>

        <!-- Papers Section -->
        <h3 class="section-title">Papers Covered in Today's Episode</h3>

        <div class="paper-item">
            <a href="javascript:void(0)"
                onclick="askAboutPaper('Back to Basics: Let Denoising Generative Models Denoise')"
                class="paper-title">1. Back to Basics: Let Denoising Generative Models Denoise</a>
            <div class="paper-meta">Tianhong Li, Kaiming He</div>
            <div class="paper-desc">
                Kaiming He challenges the fundamental paradigm of diffusion models, arguing we should predict clean data
                directly.
            </div>
        </div>

        <div class="paper-item">
            <a href="javascript:void(0)" onclick="askAboutPaper('Cost-Effective Communication')" class="paper-title">2.
                Cost-Effective Communication</a>
            <div class="paper-meta">Yijia Fan, Keze Wang, et al.</div>
            <div class="paper-desc">
                Novel economic framework treats communication bandwidth as a scarce resource in multi-agent systems.
            </div>
        </div>

        <div class="paper-item">
            <a href="javascript:void(0)" onclick="askAboutPaper('Scaling Spatial Intelligence')" class="paper-title">3.
                Scaling Spatial Intelligence</a>
            <div class="paper-meta">Zhongang Cai, et al.</div>
            <div class="paper-desc">
                Systematic approach to cultivating spatial reasoning through principled data curation.
            </div>
        </div>
    </div>

    <!-- Interactive Modal -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Interactive Mode</div>
                <button class="close-btn" onclick="closeModal()" aria-label="Close modal">×</button>
            </div>

            <div class="chat-area" id="chatArea" role="log" aria-live="polite" aria-label="Chat messages">
                <!-- Messages will be dynamically added here -->
            </div>

            <div class="input-area">
                <div class="mode-selector" role="radiogroup" aria-label="Select response mode">
                    <div class="mode-chip active" onclick="setMode('plain_english', this)" role="radio" aria-checked="true" tabindex="0">Plain English</div>
                    <div class="mode-chip" onclick="setMode('founder_takeaway', this)" role="radio" aria-checked="false" tabindex="0">Founder</div>
                    <div class="mode-chip" onclick="setMode('engineer_angle', this)" role="radio" aria-checked="false" tabindex="0">Engineer</div>
                </div>
                <div class="input-row">
                    <input type="text" id="queryInput" placeholder="Ask about this episode..." aria-label="Type your question">
                    <button class="send-btn" onclick="handleSend()" aria-label="Send message">↑</button>
                </div>
            </div>
        </div>
    </div>

    <!-- External JavaScript (must be in order) -->
    <script src="/static/js/api-client.js"></script>
    <script src="/static/js/app.js"></script>
</body>

</html>'''

def create_new_html():
    """Write the new streamlined HTML file"""
    
    file_path = r'c:\Users\Pavan Kalyan\.gemini\antigravity\playground\metallic-kilonova\episode-companion-agent\static\index.html'
    
    try:
        # Create backup
        import shutil
        shutil.copy(file_path, file_path + '.before-phase2')
        print("✓ Created backup: index.html.before-phase2")
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(HTML_CONTENT)
        
        print(f"✓ Created streamlined HTML file")
        print(f"   - Removed ~400 lines of embedded CSS/JS")
        print(f"   - Added links to external files")
        print(f"   - Added ARIA accessibility attributes")
        print(f"\n✅ index.html has been modernized!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("HTML MODERNIZATION SCRIPT")
    print("=" * 60)
    print()
    
    success = create_new_html()
    
    print()
    if success:
        print("🎉 SUCCESS! Refresh browser to see modern design.")
    else:
        print("⚠️  FAILED! Check the error messages above.")

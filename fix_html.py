#!/usr/bin/env python3
"""
Fix script for corrupted index.html
Rebuilds the file with proper modal structure
"""

# The correct HTML for the modal section (lines 397-end before </body>)
CORRECT_MODAL_HTML = '''    <!-- Interactive Modal -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Interactive Mode</div>
                <button class="close-btn" onclick="closeModal()">×</button>
            </div>

            <div class="chat-area" id="chatArea">
                <!-- Messages will be dynamically added here -->
            </div>

            <div class="input-area">
                <div class="mode-selector">
                    <div class="mode-chip active" onclick="setMode('plain_english', this)">Plain English</div>
                    <div class="mode-chip" onclick="setMode('founder_takeaway', this)">Founder</div>
                    <div class="mode-chip" onclick="setMode('engineer_angle', this)">Engineer</div>
                </div>
                <div class="input-row">
                    <input type="text" id="queryInput" placeholder="Ask about this episode...">
                    <button class="send-btn" onclick="handleSend()">↑</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Episode ID from the current page
        const EPISODE_ID = 'ai-research-daily-2025-11-18';
        
        // Current selected mode
        let currentMode = 'plain_english';

        // DOM elements
        const modal = document.getElementById('modalOverlay');
        const chatArea = document.getElementById('chatArea');
        const queryInput = document.getElementById('queryInput');

        // Open modal
        function openModal() {
            modal.style.display = 'flex';
            queryInput.focus();
        }

        // Close modal
        function closeModal() {
            modal.style.display = 'none';
        }

        // Ask about a specific paper
        function askAboutPaper(paperTitle) {
            openModal();
            queryInput.value = `Tell me more about "${paperTitle}"`;
            handleSend();
        }

        // Set mode and update UI
        function setMode(mode, element) {
            currentMode = mode;

            // Update UI: remove 'active' from all chips, add to clicked one
            document.querySelectorAll('.mode-chip').forEach(chip => {
                chip.classList.remove('active');
            });
            element.classList.add('active');
        }

        // Add message to chat area
        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.textContent = text;
            chatArea.appendChild(div);

            // Auto-scroll to bottom
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        // Render suggested follow-ups
        function renderFollowups(followups) {
            if (!followups || followups.length === 0) return;

            const container = document.createElement('div');
            container.style.display = 'flex';
            container.style.gap = '8px';
            container.style.flexWrap = 'wrap';
            container.style.marginTop = '8px';
            container.style.marginLeft = '16px'; // Align with agent message

            followups.forEach(q => {
                const chip = document.createElement('div');
                chip.className = 'mode-chip'; // Reuse chip style
                chip.style.fontSize = '0.75rem';
                chip.style.padding = '4px 10px';
                chip.style.cursor = 'pointer';
                chip.textContent = q;
                chip.onclick = () => {
                    queryInput.value = q;
                    handleSend();
                    container.remove(); // Remove suggestions after clicking one
                };
                container.appendChild(chip);
            });

            chatArea.appendChild(container);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        // Handle send button click
        async function handleSend() {
            const query = queryInput.value.trim();

            if (!query) return; // Don't send empty queries

            // Add user message to UI
            addMessage(query, 'user');

            // Clear input
            queryInput.value = '';

            // Show loading message
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message agent';
            loadingDiv.textContent = '...';
            loadingDiv.id = 'loading-message';
            chatArea.appendChild(loadingDiv);
            chatArea.scrollTop = chatArea.scrollHeight;

            try {
                // Call companion API (supports mode)
                const response = await fetch('/companion/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': 'my-secret-antigravity-password' // from .env default
                    },
                    body: JSON.stringify({
                        message: query, // Note: Schema expects 'message', not 'query'
                        user_id: 'web-demo-user',
                        episode_id: EPISODE_ID,
                        mode: currentMode // Send selected mode
                    })
                });

                // Remove loading message
                const loading = document.getElementById('loading-message');
                if (loading) loading.remove();

                if (!response.ok) {
                    const error = await response.json();
                    addMessage(`Error: ${error.detail || 'Failed to get response'}`, 'agent');
                    return;
                }

                const data = await response.json();
                addMessage(data.answer, 'agent');

                // Render follow-ups if available
                if (data.metadata && data.metadata.suggested_followups) {
                    renderFollowups(data.metadata.suggested_followups);
                }

            } catch (error) {
                // Remove loading message
                const loading = document.getElementById('loading-message');
                if (loading) loading.remove();

                addMessage(`Error: ${error.message}`, 'agent');
                console.error('Query error:', error);
            }
        }

        // Handle Enter key in input
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSend();
            }
        });

        // Close modal on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    </script>
</body>

</html>'''

def fix_html_file():
    """Rebuild the HTML file with correct structure"""
    
    file_path = r'c:\Users\Pavan Kalyan\.gemini\antigravity\playground\metallic-kilonova\episode-companion-agent\static\index.html'
    
    try:
        # Read the corrupted file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ Read file: {len(content)} characters")
        
        # Find where the first modal-overlay comment appears
        modal_comment = '<!-- Interactive Modal -->'
        first_modal_idx = content.find(modal_comment)
        
        if first_modal_idx == -1:
            print("ERROR: Could not find modal comment marker")
            return False
        
        print(f"✓ Found modal marker at position {first_modal_idx}")
        
        # Extract everything BEFORE the first modal comment
        # This should be all the good HTML up to line 396
        clean_content = content[:first_modal_idx]
        
        print(f"✓ Extracted clean content: {len(clean_content)} characters")
        
        # Append the correct modal HTML
        final_content = clean_content + CORRECT_MODAL_HTML
        
        print(f"✓ Built final content: {len(final_content)} characters")
        
        # Write the fixed file
        with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(final_content)
        
        print(f"✓ File written successfully!")
        print(f"\n✅ HTML file has been fixed!")
        print(f"   - Removed duplicates")
        print(f"   - Added proper modal structure")
        print(f"   - Ready to use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("HTML FIX SCRIPT")
    print("=" * 60)
    print()
    
    success = fix_html_file()
    
    print()
    if success:
        print("🎉 SUCCESS! Refresh your browser to see the fixed modal.")
    else:
        print("⚠️  FAILED! Check the error messages above.")

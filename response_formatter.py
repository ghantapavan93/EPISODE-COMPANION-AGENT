"""
Response Formatting Utility
Converts markdown responses to beautifully formatted HTML
"""
import re
import html
from typing import Dict, List, Tuple
import markdown
from markdown.extensions import fenced_code, tables, nl2br


class ResponseFormatter:
    """Formats agent responses with markdown support and enhanced styling"""
    
    def __init__(self):
        # Initialize markdown parser with extensions
        self.md = markdown.Markdown(
            extensions=[
                'fenced_code',
                'tables',
                'nl2br',
                'sane_lists'
            ],
            extension_configs={
                'fenced_code': {
                    'lang_prefix': 'language-'
                }
            }
        )
    
    def format_response(self, text: str) -> str:
        """
        Main formatting pipeline
        
        Args:
            text: Raw markdown text from agent
            
        Returns:
            Formatted HTML ready for frontend display
        """
        # Step 1: Remove old-style separators
        text = self._remove_separators(text)
        
        # Step 2: Enhanced citation formatting
        text = self._format_citations(text)
        
        # Step 3: Add proper spacing
        text = self._add_spacing(text)
        
        # Step 4: Convert markdown to HTML
        html_content = self.md.convert(text)
        
        # Step 5: Sanitize and add classes
        html_content = self._add_classes(html_content)
        
        # Reset markdown parser for next use
        self.md.reset()
        
        return html_content
    
    def _remove_separators(self, text: str) -> str:
        """Remove asterisk separators and other legacy formatting"""
        # Remove lines with only asterisks or dashes
        text = re.sub(r'^\*{3,}\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^-{3,}\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^={3,}\s*$', '', text, flags=re.MULTILINE)
        
        # Remove excessive blank lines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _format_citations(self, text: str) -> str:
        """
        Format citations with enhanced styling
        Converts [Paper Name] to styled citation badges
        """
        # Pattern to match citations: [Paper Name] or [Paper Name](source)
        citation_pattern = r'\[([^\]]+)\](?:\(source\))?'
        
        def citation_replacer(match):
            paper_name = match.group(1)
            # Create a styled citation badge
            return f'<span class="citation" title="Source: {paper_name}">[{paper_name}]</span>'
        
        text = re.sub(citation_pattern, citation_replacer, text)
        
        return text
    
    def _add_spacing(self, text: str) -> str:
        """Add proper spacing around sections"""
        # Add space before headers (if not at start)
        text = re.sub(r'(?<!\n)\n(#{1,6}\s)', r'\n\n\1', text)
        
        # Ensure proper spacing after headers
        text = re.sub(r'(#{1,6}\s[^\n]+)\n(?!\n)', r'\1\n\n', text)
        
        return text
    
    def _add_classes(self, html_content: str) -> str:
        """Add CSS classes to HTML elements for styling"""
        # Add classes to headers
        html_content = re.sub(r'<h2>', '<h2 class="response-heading">', html_content)
        html_content = re.sub(r'<h3>', '<h3 class="response-subheading">', html_content)
        html_content = re.sub(r'<h4>', '<h4 class="response-minor-heading">', html_content)
        
        # Add classes to lists
        html_content = re.sub(r'<ul>', '<ul class="response-list">', html_content)
        html_content = re.sub(r'<ol>', '<ol class="response-ordered-list">', html_content)
        
        # Add classes to code blocks
        html_content = re.sub(r'<pre>', '<pre class="response-code-block">', html_content)
        html_content = re.sub(r'<code>', '<code class="response-code">', html_content)
        
        # Add classes to paragraphs
        html_content = re.sub(r'<p>', '<p class="response-paragraph">', html_content)
        
        return html_content
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract named sections from formatted response
        Useful for rendering collapsible sections
        """
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in text.split('\n'):
            # Check if line is a header
            header_match = re.match(r'^(#{2,4})\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = header_match.group(2).lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections


def format_for_display(agent_response: str) -> str:
    """
    Convenience function to format agent response
    
    Args:
        agent_response: Raw text from agent
        
    Returns:
        Formatted HTML
    """
    formatter = ResponseFormatter()
    return formatter.format_response(agent_response)


if __name__ == "__main__":
    # Test formatting
    test_response = """
## Big Idea
This is a test response with **bold text** and *italic text*.

### Key Points
- First point with [Paper Name] citation
- Second point with details
- Third point

***

### Code Example
```python
def hello():
    print("Hello, World!")
```

According to [Kandinsky 5.0], this approach works well.
"""
    
    formatter = ResponseFormatter()
    formatted = formatter.format_response(test_response)
    print(formatted)

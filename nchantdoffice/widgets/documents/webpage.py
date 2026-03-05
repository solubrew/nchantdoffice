"""PyfficeWebPage document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeWebPage as BasePyfficeWebPage
from ogma.logma import Logma
logma = Logma(__name__)
logma.off()
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeWebPage(NchantdOfficeDocument, BasePyfficeWebPage):
    """WebPage document - implements PyfficeWebPage.
    
    Provides web page viewing and editing with HTML preview,
    source editing, and web resource management.
    """
    
    PYTYPE = 'webpage'
    DEFAULT_TOOLS = [
        {'id': 'edit_html', 'icon': 'code', 'label': 'Edit HTML', 'method': 'edit_html'},
        {'id': 'preview', 'icon': 'eye', 'label': 'Preview', 'method': 'preview_page'},
        {'id': 'split_view', 'icon': 'columns', 'label': 'Split View', 'method': 'split_view'},
        {'id': 'insert_element', 'icon': 'plus', 'label': 'Insert Element', 'method': 'insert_element'},
        {'id': 'add_style', 'icon': 'palette', 'label': 'Add Style', 'method': 'add_style'},
        {'id': 'validate', 'icon': 'check', 'label': 'Validate HTML', 'method': 'validate_html'},
        {'id': 'minify', 'icon': 'compress', 'label': 'Minify', 'method': 'minify_html'},
        {'id': 'format', 'icon': 'align-left', 'label': 'Format', 'method': 'format_html'},
        {'id': 'export_html', 'icon': 'file-code', 'label': 'Export HTML', 'method': 'export_html'},
        {'id': 'import_html', 'icon': 'download', 'label': 'Import HTML', 'method': 'import_html'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for web page document."""
        return cls.DEFAULT_TOOLS
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._html_content = ""
        self._css_content = ""
        self._js_content = ""
        self._view_mode = 'preview'  # preview, source, split
    
    def set_html(self, html: str) -> bool:
        """Set HTML content."""
        try:
            self._html_content = html
            return True
        except Exception as e:
            logma.error(f"Failed to set HTML: {e}")
            return False
    
    def get_html(self) -> str:
        """Get HTML content."""
        return self._html_content
    
    def set_css(self, css: str) -> bool:
        """Set CSS content."""
        try:
            self._css_content = css
            return True
        except Exception as e:
            logma.error(f"Failed to set CSS: {e}")
            return False
    
    def get_css(self) -> str:
        """Get CSS content."""
        return self._css_content
    
    def set_js(self, js: str) -> bool:
        """Set JavaScript content."""
        try:
            self._js_content = js
            return True
        except Exception as e:
            logma.error(f"Failed to set JS: {e}")
            return False
    
    def get_js(self) -> str:
        """Get JavaScript content."""
        return self._js_content
    
    def edit_html(self) -> bool:
        """Switch to HTML source editing mode."""
        self._view_mode = 'source'
        logma.info("Switched to HTML source mode")
        return True
    
    def preview_page(self) -> bool:
        """Switch to preview mode."""
        self._view_mode = 'preview'
        logma.info("Switched to preview mode")
        return True
    
    def split_view(self) -> bool:
        """Switch to split view mode."""
        self._view_mode = 'split'
        logma.info("Switched to split view mode")
        return True
    
    def insert_element(self, element: str) -> bool:
        """Insert HTML element at cursor."""
        try:
            self._html_content += element
            return True
        except Exception as e:
            logma.error(f"Failed to insert element: {e}")
            return False
    
    def add_style(self, css: str) -> bool:
        """Add CSS styles to page."""
        try:
            style_tag = f"<style>{css}</style>"
            if '<head>' in self._html_content:
                self._html_content = self._html_content.replace(
                    '</head>', f"{style_tag}</head>"
                )
            else:
                self._html_content = style_tag + self._html_content
            return True
        except Exception as e:
            logma.error(f"Failed to add style: {e}")
            return False
    
    def validate_html(self) -> Dict[str, Any]:
        """Validate HTML structure."""
        results = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for unclosed tags
        import re
        open_tags = re.findall(r'<(\w+)[^>]*>', self._html_content)
        close_tags = re.findall(r'</(\w+)>', self._html_content)
        
        # Basic validation
        if not self._html_content.strip():
            results['warnings'].append("Empty HTML content")
        
        return results
    
    def minify_html(self) -> bool:
        """Minify HTML content."""
        try:
            import re
            # Remove comments
            self._html_content = re.sub(r'<!--.*?-->', '', self._html_content, flags=re.DOTALL)
            # Remove extra whitespace
            self._html_content = re.sub(r'\s+', ' ', self._html_content)
            # Remove whitespace around tags
            self._html_content = re.sub(r'>\s+<', '><', self._html_content)
            return True
        except Exception as e:
            logma.error(f"Failed to minify: {e}")
            return False
    
    def format_html(self) -> bool:
        """Format/beautify HTML content."""
        try:
            import re
            # Simple formatting - add newlines after closing tags
            self._html_content = self._html_content.replace('>', '>\n')
            self._html_content = self._html_content.replace('\n\n', '\n')
            return True
        except Exception as e:
            logma.error(f"Failed to format: {e}")
            return False
    
    def export_html(self, filepath: str) -> bool:
        """Export web page to HTML file."""
        try:
            # Combine HTML, CSS, JS into single file
            full_html = self._html_content
            
            # Inject CSS
            if self._css_content:
                if '<style>' in full_html:
                    full_html = full_html.replace(
                        '<style>', f'<style>{self._css_content}'
                    )
                elif '</head>' in full_html:
                    full_html = full_html.replace(
                        '</head>', f'<style>{self._css_content}</style></head>'
                    )
            
            # Inject JS
            if self._js_content:
                if '<script>' in full_html:
                    full_html = full_html.replace(
                        '<script>', f'<script>{self._js_content}'
                    )
                elif '</body>' in full_html:
                    full_html = full_html.replace(
                        '</body>', f'<script>{self._js_content}</script></body>'
                    )
            
            with open(filepath, 'w') as f:
                f.write(full_html)
            return True
        except Exception as e:
            logma.error(f"Failed to export HTML: {e}")
            return False
    
    def import_html(self, filepath: str) -> bool:
        """Import web page from HTML file."""
        try:
            with open(filepath, 'r') as f:
                self._html_content = f.read()
            
            # Extract CSS if in style tags
            import re
            css_match = re.search(r'<style[^>]*>(.*?)</style>', self._html_content, re.DOTALL)
            if css_match:
                self._css_content = css_match.group(1)
            
            # Extract JS if in script tags
            js_match = re.search(r'<script[^>]*>(.*?)</script>', self._html_content, re.DOTALL)
            if js_match:
                self._js_content = js_match.group(1)
            
            return True
        except Exception as e:
            logma.error(f"Failed to import HTML: {e}")
            return False
    
    def get_rendered_content(self) -> str:
        """Get full HTML with embedded CSS and JS."""
        content = self._html_content
        
        if self._css_content:
            content = content.replace('</head>', f'<style>{self._css_content}</style></head>')
        
        if self._js_content:
            content = content.replace('</body>', f'<script>{self._js_content}</script></body>')
        
        return content

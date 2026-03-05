"""PyfficeBibliography document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeBibliography as BasePyfficeBibliography
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeBibliography(NchantdOfficeDocument, BasePyfficeBibliography):
    """Bibliography document - implements PyfficeBibliography.
    
    Provides bibliography/reference management with citation
    styles, import/export, and organization features.
    """
    
    PYTYPE = 'bibliography'
    DEFAULT_TOOLS = [
        {'id': 'add_reference', 'icon': 'plus', 'label': 'Add Reference', 'method': 'add_reference'},
        {'id': 'remove_reference', 'icon': 'minus', 'label': 'Remove', 'method': 'remove_reference'},
        {'id': 'edit_reference', 'icon': 'edit', 'label': 'Edit', 'method': 'edit_reference'},
        {'id': 'import_bibtex', 'icon': 'import', 'label': 'Import BibTeX', 'method': 'import_bibtex'},
        {'id': 'export_bibtex', 'icon': 'export', 'label': 'Export BibTeX', 'method': 'export_bibtex'},
        {'id': 'import_ris', 'icon': 'download', 'label': 'Import RIS', 'method': 'import_ris'},
        {'id': 'export_ris', 'icon': 'save', 'label': 'Export RIS', 'method': 'export_ris'},
        {'id': 'set_style', 'icon': 'text', 'label': 'Citation Style', 'method': 'set_citation_style'},
        {'id': 'generate_citation', 'icon': 'quote', 'label': 'Generate Citation', 'method': 'generate_citation'},
        {'id': 'search', 'icon': 'search', 'label': 'Search', 'method': 'search_references'},
    ]
    
    # Citation styles
    CITATION_STYLES = ['apa', 'mla', 'chicago', 'ieee', 'harvard', 'vancouver']
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for bibliography document."""
        return cls.DEFAULT_TOOLS
    
    def add_reference(self, ref_type: str, **kwargs) -> Optional[str]:
        """Add a new reference entry."""
        try:
            ref_id = f"ref_{len(self._references)}"
            self._references[ref_id] = {
                'type': ref_type,
                'data': kwargs,
            }
            return ref_id
        except Exception as e:
            logma.error(f"Failed to add reference: {e}")
            return None
    
    def remove_reference(self, ref_id: str) -> bool:
        """Remove a reference entry."""
        try:
            if ref_id in self._references:
                del self._references[ref_id]
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove reference: {e}")
            return False
    
    def edit_reference(self, ref_id: str, **kwargs) -> bool:
        """Edit a reference entry."""
        try:
            if ref_id in self._references:
                self._references[ref_id]['data'].update(kwargs)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to edit reference: {e}")
            return False
    
    def import_bibtex(self, filepath: str) -> bool:
        """Import references from BibTeX file."""
        try:
            import bibtexparser
            with open(filepath, 'r') as f:
                bib_db = bibtexparser.load(f)
            for entry in bib_db.entries:
                ref_type = entry.get('ENTRYTYPE', 'misc')
                self.add_reference(ref_type, **entry)
            return True
        except Exception as e:
            logma.error(f"Failed to import BibTeX: {e}")
            return False
    
    def export_bibtex(self, filepath: str) -> bool:
        """Export references to BibTeX file."""
        try:
            import bibtexparser
            entries = []
            for ref_id, ref in self._references.items():
                entry = ref['data'].copy()
                entry['ENTRYTYPE'] = ref['type']
                entry['ID'] = ref_id
                entries.append(entry)
            bib_db = bibtexparser.bibdatabase.BibDatabase()
            bib_db.entries = entries
            with open(filepath, 'w') as f:
                bibtexparser.dump(bib_db, f)
            return True
        except Exception as e:
            logma.error(f"Failed to export BibTeX: {e}")
            return False
    
    def import_ris(self, filepath: str) -> bool:
        """Import references from RIS file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            # Parse RIS format (simplified)
            current_ref = {}
            for line in content.split('\n'):
                if line.startswith('TY  -'):
                    current_ref = {'type': line[5:].strip()}
                elif line.startswith('ER  -'):
                    if current_ref:
                        self.add_reference(current_ref.get('type', 'misc'), **current_ref)
                        current_ref = {}
                elif ' - ' in line:
                    tag, value = line.split('-', 1)
                    current_ref[tag.strip()] = value.strip()
            return True
        except Exception as e:
            logma.error(f"Failed to import RIS: {e}")
            return False
    
    def export_ris(self, filepath: str) -> bool:
        """Export references to RIS file."""
        try:
            with open(filepath, 'w') as f:
                for ref_id, ref in self._references.items():
                    for key, value in ref['data'].items():
                        f.write(f"{key}  - {value}\n")
                    f.write("TY  - " + ref['type'] + "\n")
                    f.write("ER  - \n\n")
            return True
        except Exception as e:
            logma.error(f"Failed to export RIS: {e}")
            return False
    
    def set_citation_style(self, style: str) -> bool:
        """Set citation style."""
        if style.lower() in self.CITATION_STYLES:
            self._citation_style = style.lower()
            return True
        return False
    
    def generate_citation(self, ref_id: str) -> Optional[str]:
        """Generate formatted citation for a reference."""
        try:
            if ref_id not in self._references:
                return None
            ref = self._references[ref_id]['data']
            style = getattr(self, '_citation_style', 'apa')
            
            if style == 'apa':
                authors = ref.get('author', 'Unknown')
                title = ref.get('title', 'Untitled')
                year = ref.get('year', 'n.d.')
                return f"{authors} ({year}). {title}."
            elif style == 'mla':
                authors = ref.get('author', 'Unknown')
                title = ref.get('title', 'Untitled')
                return f"{authors}. \"{title}.\""
            # Add more styles as needed
            return str(ref)
        except Exception as e:
            logma.error(f"Failed to generate citation: {e}")
            return None
    
    def search_references(self, query: str) -> List[str]:
        """Search references by query."""
        results = []
        query_lower = query.lower()
        for ref_id, ref in self._references.items():
            ref_text = ' '.join(str(v) for v in ref['data'].values()).lower()
            if query_lower in ref_text:
                results.append(ref_id)
        return results

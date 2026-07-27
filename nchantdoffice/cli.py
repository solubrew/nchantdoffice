# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name: NchantdOffice CLI
	description: >
		Command-line interface for NchantdOffice
	version: 0.0.0.0.0.0
	authority: filesystem
	security: seclvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*
import click
import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@click.group()
@click.version_option(version="0.0.1")
def cli():
    """NchantdOffice - Document Management System"""
    pass


# Document type mapping
DOCUMENT_TYPES = {
    'text': 'note',
    'spreadsheet': 'spreadsheet',
    'notebook': 'notebook',
    'calendar': 'calendar',
    'chart': 'chart',
    'pdf': 'pdf',
    'image': 'image',
    'video': 'video',
    'audio': 'audio',
    'contact': 'contact',
    'form': 'form',
    'survey': 'survey',
    'presentation': 'presentation',
    'table': 'table',
    'matrix': 'matrix',
    'script': 'script',
    'webbrowser': 'browser',
    'webpage': 'webpage',
}


def get_documents_dir():
    """Get the documents directory path."""
    home = Path.home()
    docs_dir = home / ".nchantdoffice" / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir


def get_recent_files_path():
    """Get the recent files list path."""
    config_dir = Path.home() / ".nchantdoffice"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "recent_files.json"


def load_recent_files():
    """Load recent files list."""
    path = get_recent_files_path()
    if path.exists():
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_recent_file(filepath):
    """Add a file to the recent files list."""
    recent = load_recent_files()
    
    # Remove if already exists
    recent = [f for f in recent if f['path'] != filepath]
    
    # Add to front
    stat = os.stat(filepath)
    recent.insert(0, {
        'path': filepath,
        'name': os.path.basename(filepath),
        'accessed': datetime.now().isoformat(),
        'size': stat.st_size,
    })
    
    # Keep only last 50
    recent = recent[:50]
    
    with open(get_recent_files_path(), 'w') as f:
        json.dump(recent, f, indent=2)


def calculate_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None


def create_document_file(filepath, doc_type):
    """Create a new .pyof document file."""
    doc_type_key = doc_type.lower()
    doc_type_value = DOCUMENT_TYPES.get(doc_type_key, 'note')
    
    doc_data = {
        'version': '1.0',
        'type': doc_type_value,
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'content': {
            'data': '',
            'format': doc_type_key,
        },
        'metadata': {},
    }
    
    with open(filepath, 'w') as f:
        json.dump(doc_data, f, indent=2)
    
    return doc_data


@cli.command()
@click.argument('filepath', required=False)
@click.option('--type', '-t', 'doc_type', default='text', help='Document type: text, spreadsheet, notebook, calendar, chart, pdf, image, video, audio, contact, form, survey, presentation, table, matrix, script, webbrowser, webpage')
@click.option('--template', help='Use a template')
def new(filepath, doc_type, template):
    """Create a new document"""
    if not filepath:
        # Generate a default name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"untitled_{timestamp}.pyof"
    else:
        # Ensure .pyof extension
        if not filepath.endswith('.pyof'):
            filepath += '.pyof'
    
    # Get full path
    docs_dir = get_documents_dir()
    full_path = docs_dir / filepath
    
    click.echo(f"Creating new {doc_type} document: {full_path}")
    
    try:
        # Check if file already exists
        if full_path.exists():
            click.echo(f"Error: File already exists: {full_path}", err=True)
            sys.exit(1)
        
        # Handle template if provided
        if template:
            template_path = Path(template)
            if template_path.exists():
                shutil.copy(template_path, full_path)
                click.echo(f"Created from template: {full_path}")
            else:
                click.echo(f"Template not found: {template}", err=True)
                sys.exit(1)
        else:
            # Create new document
            create_document_file(full_path, doc_type)
            click.echo(f"Created: {full_path}")
        
        # Add to recent files
        save_recent_file(str(full_path))
        click.echo("Document created successfully!")
        
    except PermissionError:
        click.echo(f"Error: Permission denied: {full_path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error creating document: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('filepath')
@click.option('--readonly', is_flag=True, help='Open in read-only mode')
def open(filepath, readonly):
    """Open an existing document"""
    # Resolve path
    path = Path(filepath)
    
    # If relative path, check in documents directory
    if not path.is_absolute():
        docs_dir = get_documents_dir()
        potential_path = docs_dir / path
        if potential_path.exists():
            path = potential_path
        elif not path.exists():
            # Try with .pyof extension
            path = Path(f"{filepath}.pyof")
            if not path.exists():
                path = docs_dir / f"{filepath}.pyof"
    
    click.echo(f"Opening: {path}")
    
    try:
        if not path.exists():
            click.echo(f"Error: File not found: {path}", err=True)
            sys.exit(1)
        
        # Validate file format
        if not path.suffix == '.pyof':
            click.echo(f"Warning: File does not have .pyof extension", err=True)
        
        # Read and validate document
        with open(path, 'r') as f:
            doc_data = json.load(f)
        
        # Check required fields
        required_fields = ['version', 'type', 'created', 'modified', 'content']
        for field in required_fields:
            if field not in doc_data:
                click.echo(f"Warning: Document missing field: {field}", err=True)
        
        # Add to recent files
        save_recent_file(str(path))
        
        click.echo(f"Document type: {doc_data.get('type', 'unknown')}")
        click.echo(f"Created: {doc_data.get('created', 'unknown')}")
        click.echo(f"Modified: {doc_data.get('modified', 'unknown')}")
        
        if readonly:
            click.echo("Mode: Read-only")
        
        click.echo("Document opened successfully!")
        
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in document: {e}", err=True)
        sys.exit(1)
    except PermissionError:
        click.echo(f"Error: Permission denied: {path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error opening document: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('filepath')
@click.option('--format', '-f', 'export_format', default='pdf', help='Export format: pdf, html, docx, txt, md, json')
@click.option('--output', '-o', help='Output file path')
def export(filepath, export_format, output):
    """Export document to different format"""
    # Resolve path
    path = Path(filepath)
    
    if not path.exists():
        docs_dir = get_documents_dir()
        path = docs_dir / filepath
        if not path.exists():
            path = docs_dir / f"{filepath}.pyof"
    
    click.echo(f"Exporting {path} to {export_format}")
    
    try:
        if not path.exists():
            click.echo(f"Error: File not found: {path}", err=True)
            sys.exit(1)
        
        # Read source document
        with open(path, 'r') as f:
            doc_data = json.load(f)
        
        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = path.with_suffix(f'.{export_format}')
        
        # Export based on format
        content = doc_data.get('content', {}).get('data', '')
        
        if export_format in ['txt', 'md']:
            # Plain text export
            if isinstance(content, dict):
                content = json.dumps(content, indent=2)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(content))
        
        elif export_format == 'html':
            # HTML export
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{doc_data.get('type', 'Document')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .metadata {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{doc_data.get('type', 'Document')}</h1>
    <div class="metadata">
        <p>Created: {doc_data.get('created', 'N/A')}</p>
        <p>Modified: {doc_data.get('modified', 'N/A')}</p>
    </div>
    <hr>
    <pre>{content if isinstance(content, str) else json.dumps(content, indent=2)}</pre>
</body>
</html>"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif export_format == 'json':
            # JSON export (full document)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, indent=2)
        
        else:
            click.echo(f"Error: Unsupported export format: {export_format}", err=True)
            click.echo("Supported formats: txt, md, html, json", err=True)
            sys.exit(1)
        
        click.echo(f"Exported to: {output_path}")
        click.echo("Export completed successfully!")
        
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid source document: {e}", err=True)
        sys.exit(1)
    except PermissionError:
        click.echo(f"Error: Permission denied for output: {output_path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error exporting document: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('filepath')
@click.option('--backup', is_flag=True, help='Create backup before saving')
def save(filepath, backup):
    """Save the document"""
    path = Path(filepath)
    
    # Resolve path
    if not path.is_absolute():
        docs_dir = get_documents_dir()
        if not path.exists():
            path = docs_dir / filepath
            if not path.exists():
                path = docs_dir / f"{filepath}.pyof"
    
    click.echo(f"Saving: {path}")
    
    try:
        if not path.exists():
            click.echo(f"Error: File not found: {path}", err=True)
            sys.exit(1)
        
        # Create backup if requested
        if backup:
            backup_dir = path.parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{path.stem}_{timestamp}{path.suffix}"
            shutil.copy2(path, backup_path)
            click.echo(f"Backup created: {backup_path}")
        
        # Update modified timestamp
        with open(path, 'r') as f:
            doc_data = json.load(f)
        
        doc_data['modified'] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(doc_data, f, indent=2)
        
        click.echo("Document saved successfully!")
        
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid document format: {e}", err=True)
        sys.exit(1)
    except PermissionError:
        click.echo(f"Error: Permission denied: {path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error saving document: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--limit', '-n', default=10, help='Maximum number of documents to show')
def list(limit):
    """List recent documents"""
    click.echo("Recent documents:")
    click.echo("-" * 60)
    
    recent = load_recent_files()
    
    if not recent:
        click.echo("  (none)")
        return
    
    for i, doc in enumerate(recent[:limit]):
        path = Path(doc['path'])
        name = doc.get('name', path.name)
        size = doc.get('size', 0)
        accessed = doc.get('accessed', 'Unknown')
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        # Format date
        try:
            dt_obj = datetime.fromisoformat(accessed)
            date_str = dt_obj.strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            date_str = accessed[:16] if accessed else 'Unknown'
        
        # Check if file exists
        exists_str = "✓" if path.exists() else "✗"
        
        click.echo(f"{i+1:2}. [{exists_str}] {name}")
        click.echo(f"    Path: {doc['path']}")
        click.echo(f"    Size: {size_str} | Accessed: {date_str}")
        click.echo("")




@cli.command()
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
def models(quiet):
    """Inspect the data models (NchantdOfficeCloakModel, NchantdOfficeSettingsModel, etc.)."""
    if not quiet:
        click.echo("Loading NchantdOffice data models...")
    try:
        from nchantdoffice.models import (
            NchantdOfficeCloakModel,
            NchantdOfficeSettingsModel,
            NchantdOfficeStore,
        )
        click.echo("Models:")
        click.echo("  - NchantdOfficeCloakModel")
        click.echo("  - NchantdOfficeSettingsModel")
        click.echo("  - NchantdOfficeStore")
        return 0
    except ImportError as e:
        click.echo(f"Failed to import models: {e}", err=True)
        return 1


@cli.command()
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
def views(quiet):
    """Inspect the view layer (Qt windows, panes, dialogs)."""
    if not quiet:
        click.echo("Loading NchantdOffice views...")
    try:
        from nchantdoffice import views
        click.echo("Views module loaded successfully")
        click.echo("Provides: document, spreadsheet, presentation, drawing panes")
        return 0
    except ImportError as e:
        click.echo(f"Failed to import views: {e}", err=True)
        return 1


@cli.command(name="nchantdoffice")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
def nchantdoffice_cmd(quiet):
    """Inspect the main NchantdOffice application module."""
    if not quiet:
        click.echo("Loading NchantdOffice application module...")
    try:
        from nchantdoffice import nchantdoffice as ncd
        click.echo("NchantdOffice application module loaded")
        click.echo(f"  version: {getattr(ncd, '__version__', 'unknown')}")
        return 0
    except ImportError as e:
        click.echo(f"Failed to import nchantdoffice module: {e}", err=True)
        return 1


@cli.command(name="__main__")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
def main_module_cmd(quiet):
    """Inspect the __main__ entry point (python -m nchantdoffice)."""
    if not quiet:
        click.echo("__main__ entry point information")
    try:
        import runpy
        sys.path.insert(0, str(Path(__file__).parent.parent))
        # Don't actually run the module, just verify it's importable
        import nchantdoffice.__main__
        click.echo("__main__ module loaded successfully")
        return 0
    except Exception as e:
        click.echo(f"Failed to inspect __main__: {e}", err=True)
        return 1

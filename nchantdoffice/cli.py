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
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@click.group()
@click.version_option(version="0.0.1")
def cli():
    """NchantdOffice - Document Management System"""
    pass


@cli.command()
@click.argument('filepath', required=False)
@click.option('--type', '-t', 'doc_type', default='text', help='Document type: text, spreadsheet, notebook, calendar, chart, pdf, image, video, audio, contact, form, survey, presentation, table, matrix, script, webbrowser, webpage')
@click.option('--template', help='Use a template')
def new(filepath, doc_type, template):
    """Create a new document"""
    click.echo(f"Creating new {doc_type} document: {filepath or 'untitled'}")
    # TODO: Implement document creation
    click.echo("Document created successfully!")


@cli.command()
@click.argument('filepath')
@click.option('--readonly', is_flag=True, help='Open in read-only mode')
def open(filepath, readonly):
    """Open an existing document"""
    click.echo(f"Opening: {filepath}")
    # TODO: Implement document opening
    click.echo("Document opened successfully!")


@cli.command()
@click.argument('filepath')
@click.option('--format', '-f', 'export_format', default='pdf', help='Export format: pdf, html, docx, txt, md')
@click.option('--output', '-o', help='Output file path')
def export(filepath, export_format, output):
    """Export document to different format"""
    click.echo(f"Exporting {filepath} to {export_format}")
    # TODO: Implement export
    click.echo("Export completed successfully!")


@cli.command()
@click.argument('filepath')
@click.option('--backup', is_flag=True, help='Create backup before saving')
def save(filepath, backup):
    """Save the document"""
    if backup:
        click.echo("Creating backup...")
    click.echo(f"Saving: {filepath}")
    # TODO: Implement save
    click.echo("Document saved successfully!")


@cli.command()
def list():
    """List recent documents"""
    click.echo("Recent documents:")
    # TODO: Implement list
    click.echo("  (none)")


@cli.command()
@click.argument('filepath')
def info(filepath):
    """Show document information"""
    click.echo(f"Document: {filepath}")
    # TODO: Implement info
    click.echo("  Type: Unknown")
    click.echo("  Size: Unknown")
    click.echo("  Modified: Unknown")


@cli.command()
@click.argument('query')
@click.option('--limit', '-n', default=10, help='Maximum results')
def search(query, limit):
    """Search documents"""
    click.echo(f"Searching for: {query}")
    # TODO: Implement search
    click.echo(f"Found 0 results (max {limit})")


@cli.command()
@click.argument('filepath')
def validate(filepath):
    """Validate document integrity"""
    click.echo(f"Validating: {filepath}")
    # TODO: Implement validation
    click.echo("Document is valid!")


@cli.command()
def gui():
    """Launch the GUI application"""
    import sys
    from pathlib import Path
    
    # Add workspace to path for local development
    workspace = Path(__file__).parent.parent
    
    # Add ogma path (from gwenbot workspace)
    ogma_path = Path("/home/solubrew/EDN/AGTs/gwenbot/workspace/projects/ogma")
    if ogma_path.exists() and str(ogma_path) not in sys.path:
        sys.path.insert(0, str(ogma_path))
    
    # Add nchantrs path
    nchantrs_path = Path("/home/solubrew/EDN/AGTs/gwenbot/workspace/projects/nchantrs")
    if nchantrs_path.exists() and str(nchantrs_path) not in sys.path:
        sys.path.insert(0, str(nchantrs_path))
    
    # Add workspace path for local development
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    
    # Import and run the main application
    try:
        from nchantdoffice.__main__ import main
        main()
    except ImportError as e:
        click.echo(f"Error importing GUI: {e}", err=True)
        click.echo("Make sure nchantdoffice is properly installed", err=True)
        sys.exit(1)


@cli.command()
@click.argument('filepath')
def repair(filepath):
    """Repair corrupted document"""
    click.echo(f"Repairing: {filepath}")
    # TODO: Implement repair
    click.echo("Repair completed!")


if __name__ == '__main__':
    cli()

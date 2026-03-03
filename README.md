# NchantdOffice

NchantdOffice is a Python module that combines the Nchantrs platform and the Pyffice module to create an interactive GUI-based Python office suite. It leverages Nchantrs for rapid development of PyQt5/PySide2 applications with YAML configurations and Python widget files, integrated with a SQLite backend via FxSQuiRL. Pyffice provides the core office document handling through YAML-driven wrappers for open-source tools, enabling seamless creation, editing, and management of office documents within a graphical user interface.

## Features

- **Integrated GUI and Office Tools**: Build desktop applications for word processing, web browsing, prompts, filesystems, pdfs, and more using a unified GUI framework.
- **YAML Configurations**: Define UI layouts, document types, styles, and database schemas in YAML for easy customization.
- **Python Widget Extensions**: Add custom logic, events, and interactions via Python files for widgets.
- **SQLite Backend with SQuiRL**: Handle data storage and retrieval for documents and application state across one or more SQLite databases.
- **Cross-Platform Support**: Compatible with Windows, macOS, and Linux using PyQt5/PySide2.
- **Document Manipulation**: Create, edit, and export various document formats (.ctd, .csv, .py, .txt, etc.) directly from the GUI.
- **Rapid Development**: Combine declarative YAML setups with programmatic Python code for quick prototyping and deployment.
- **Multi-Document Interface**: Support for handling multiple documents and databases in a single application session.

## Installation

You can install NchantdOffice via pip:

```bash
pip install nchantdoffice
```

Alternatively, clone the repository and install from source:

```bash
git clone https://github.com/<USER_OR_ORG>/nchantdoffice.git
cd nchantdoffice
pip install -e .
```

### Requirements

- Python 3.12 or higher
- Dependencies: nchantrs, pyffice, pyyaml, PySide6, squirl, sqlite3 (automatically installed via pip where applicable)

## Quick Start

Import the module, load configurations, and launch the office suite application:

```python
import nchantdoffice

# Load YAML config for the application and documents
app_config = nchantdoffice.load_app_config('path/to/app.yaml')
doc_config = nchantdoffice.load_doc_config('path/to/word.yaml')

# Initialize the application with widgets, database, and document handler
app = nchantdoffice.OfficeApp(app_config, widget_dir='path/to/widgets', doc_config=doc_config)

# Connect to SQLite database
app.init_database('path/to/office.db')

# Run the GUI application
app.run()
```

## Usage

### Loading Configurations

NchantdOffice uses separate YAML files for application UI and document handling. A sample app YAML might include:

```yaml
app_name: OfficeSuite
ui:
  main_window:
    title: NchantdOffice
    menus:
      - file: [New, Open, Save]
    widgets:
      - type: document_viewer
        integration: pyffice
database:
  connections:
    - name: documents
      file: office.db
```

Document configs follow Pyffice structure, e.g.:

```yaml
document_type: word
engine: <LIB_WORD>
styles:
  default_font: Arial
```

Use `nchantdoffice.load_app_config(yaml_path)` and `nchantdoffice.load_doc_config(yaml_path)` to load them.

### Creating and Editing Documents via GUI

```python
# Within the app initialization
app = nchantdoffice.OfficeApp(app_config, widget_dir='widgets/', doc_config=doc_config)

# Initialize database
app.init_database('office.db')

# In widget logic or event handlers
def on_new_document():
    doc = app.create_document('word')
    doc.add_text('New Document Content')
    app.display_document(doc)
```

### Database Interactions

Use SQuiRL for storing document metadata or content:

```python
# Save document state
app.insert('INSERT INTO documents (name, content) VALUES (?, ?)', ('report.docx', doc.serialize()))

# Load from database
data = app.fetch('SELECT content FROM documents WHERE name = ?', ('report.docx',))
loaded_doc = app.load_document(data[0])
```

### Supported Document Types

- Word Processing: .docx, .odt
- Spreadsheets: .xlsx, .ods
- Presentations: .pptx, .odp
- Others: <ADDITIONAL_TYPES> (configurable via Pyffice YAML)

## Configuration Guide

Combine Nchantrs app configs with Pyffice document configs:

- `app_name`: Application identifier
- `ui`: UI definitions including widgets integrated with Pyffice operations
- `database`: SQLite connections via FxSQuiRL
- Document YAMLs: As per Pyffice, with `document_type`, `engine`, `styles`, `operations`

For advanced customization, refer to the [docs/config-reference.md](docs/config-reference.md).

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/<FEATURE_NAME>`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/<FEATURE_NAME>`).
5. Open a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under the <LICENSE_TYPE> License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built upon Nchantrs for GUI development and Pyffice for office tools.
- Thanks to contributors of underlying libraries like <PYQT_LIB>, FxSQuiRL, <LIB_WORD>, <LIB_SPREAD>.
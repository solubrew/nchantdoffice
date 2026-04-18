# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name:
    description: >
    version: 0.0.0.0.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join, exists

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma

from nchantdoffice.widgets.documents.atnrg.browsers.browsers import NchantdOfficeWebBrowser
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.annotations import NchantdLabel

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "notebooks.yaml")


class NchantdOfficeNotebook(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        icfg = {}
        super().__init__("Nchantd Notebook", parent, icfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNotebook").override(cfg))
        self.jupyter_process = None
        self.server_port = 8888
        self.server_url = f"http://localhost:{self.server_port}"
        self.server_running = False

        # Kernel management
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel_name = "python3"
        self.kernel_running = False
        self.current_notebook_path = None

    def initModel(self):
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_notebook()
        self.document.load_document()
        self.context_menu.get_menu("context.document.notebook")
        return self

    def initView(self, cfg=None):
        """"""
        if not cfg:
            cfg = {}
        if "buttons" not in cfg:
            cfg["buttons"] = {}
        cfg["buttons"][0] = {"action": "start_server", "handler": self.cmd_start_server}
        cfg["buttons"][1] = {"action": "restart_server", "handler": self.cmd_restart_server}
        cfg["buttons"][2] = {"action": "stop_server", "handler": self.cmd_stop_server}
        cfg["buttons"][3] = {"action": "new_notebook", "handler": self.cmd_new_notebook}
        cfg["buttons"][4] = {"action": "start_kernel", "handler": self.cmd_start_kernel}
        cfg["buttons"][5] = {"action": "interrupt_kernel", "handler": self.cmd_interrupt_kernel}
        cfg["buttons"][8] = "_insert_stretch"
        cfg["buttons"][9] = {"action": "open_local", "handler": self.cmd_open_local_file}
        super().initView(cfg)
        cfg = {"url": self.server_url, "is_app": True}
        self.browser = NchantdWebViewer(self, cfg).initView()
        self.layout.addWidget(self.browser)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Server Port: ",
            "layout": "horizontal",
            "range": [8000, 9999],
            "default": self.server_port,
            "handler": self.cmd_set_server_port,
        }
        self.port_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        items[cnt]["widget"] = self.port_spin
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Kernel: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_available_kernels()},
            "handler": self.cmd_select_kernel,
        }
        self.kernel_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.kernel_select
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "text": "Auto-start Server",
            "layout": "horizontal",
            "handler": self.cmd_toggle_autostart,
        }
        self.autostart_checkbox = NchantdCheckbox(self, cfg).initWidget()
        items[cnt]["widget"] = self.autostart_checkbox
        cnt += 1

        return items

    def init_drawer_selection_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Server Status: ", "layout": "horizontal"}
        self.server_status_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = self.server_status_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Kernel Status: ", "layout": "horizontal"}
        self.kernel_status_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = self.kernel_status_label
        cnt += 1

        return items

    def init_drawer_object_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Cell Type: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": ["Code", "Markdown", "Raw"]},
        }
        self.cell_type_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.cell_type_select
        cnt += 1

        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Quick Start Guide", "layout": "horizontal"}
        quickstart_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = quickstart_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "1. Click 'Start Server' to launch Jupyter", "layout": "horizontal"}
        step1_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step1_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "2. Click 'New Notebook' to create a notebook", "layout": "horizontal"}
        step2_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step2_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "3. Or 'Open Local' to load existing .ipynb file", "layout": "horizontal"}
        step3_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step3_label
        cnt += 1

        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    # ========== Command Handlers ==========

    def cmd_start_server(self, event=None, *args, **kwargs):
        """Start Jupyter notebook server"""
        if not self.server_running:
            self.start_jupyter_server()
        else:
            logma.info("Jupyter server is already running")
        return self

    def cmd_restart_server(self, event=None, *args, **kwargs):
        """Restart Jupyter notebook server"""
        self.stop_jupyter_server()
        import time

        time.sleep(1)  # Wait for server to fully stop
        self.start_jupyter_server()
        return self

    def cmd_stop_server(self, event=None, *args, **kwargs):
        """Stop Jupyter notebook server"""
        self.stop_jupyter_server()
        return self

    def cmd_new_notebook(self, event=None, *args, **kwargs):
        """Create a new notebook"""
        self.create_new_notebook()
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """Open a local notebook file"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file and exists(self.local_file):
            self.load_notebook_file(self.local_file)
        return self

    def cmd_set_server_port(self, event=None, *args, **kwargs):
        """Set server port number"""
        if hasattr(self, "port_spin"):
            new_port = self.port_spin.value()
            if new_port != self.server_port:
                self.server_port = new_port
                self.server_url = f"http://localhost:{self.server_port}"
                logma.info(f"Server port changed to: {self.server_port}")
                # Restart server if running
                if self.server_running:
                    logma.info("Restarting server with new port...")
                    self.cmd_restart_server()
        return self

    def cmd_select_kernel(self, event=None, *args, **kwargs):
        """Select Jupyter kernel"""
        if hasattr(self, "kernel_select"):
            kernel = self.kernel_select.currentText()
            logma.info(f"Selected kernel: {kernel}")
            self.kernel_name = kernel
            # Restart kernel if running
            if self.kernel_running:
                logma.info("Restarting kernel with new kernel type...")
                self.restart_kernel()
        return self

    def cmd_start_kernel(self, event=None, *args, **kwargs):
        """Start the Jupyter kernel"""
        if not self.kernel_running:
            self.start_kernel()
        else:
            logma.info("Kernel is already running")
        return self

    def cmd_interrupt_kernel(self, event=None, *args, **kwargs):
        """Interrupt the running kernel"""
        self.interrupt_kernel()
        return self

    def cmd_toggle_autostart(self, event=None, *args, **kwargs):
        """Toggle auto-start server setting"""
        if hasattr(self, "autostart_checkbox"):
            autostart = self.autostart_checkbox.isChecked()
            logma.info(f"Auto-start server: {autostart}")
            # Save to config
            if self.config:
                self.config.dikt["autostart_server"] = autostart
        return self

    # ========== Server Management Methods ==========

    def start_jupyter_server(self, port=None):
        """Start the Jupyter notebook server"""
        import subprocess

        if port is None:
            port = self.server_port

        try:
            # Check if server is already running
            if self.is_server_running():
                logma.info(f"Jupyter server already running on port {port}")
                self.server_running = True
                return self

            # Build command to start Jupyter
            cmd = [
                "jupyter",
                "notebook",
                "--no-browser",
                f"--port={port}",
                "--NotebookApp.token=''",
                "--NotebookApp.password=''",
                "--NotebookApp.disable_check_xsrf=True",
            ]

            # Start notebook in specific directory if file_path is set
            cwd = None
            if self.file_path and exists(dirname(self.file_path)):
                cwd = dirname(self.file_path)

            # Start the subprocess
            self.jupyter_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

            # Wait a bit for server to start
            import time

            time.sleep(2)

            self.server_running = True
            self.server_url = f"http://localhost:{port}"

            # Update browser URL
            if self.browser:
                self.browser.load_url(self.server_url)

            logma.info(f"Jupyter server started on {self.server_url}")

        except Exception as e:
            logma.error(f"Error starting Jupyter server: {e}")
            self.server_running = False

        return self

    def stop_jupyter_server(self):
        """Stop the Jupyter notebook server"""
        try:
            if self.jupyter_process:
                self.jupyter_process.terminate()
                try:
                    self.jupyter_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.jupyter_process.kill()
                    self.jupyter_process.wait()

                self.jupyter_process = None
                self.server_running = False
                logma.info("Jupyter server stopped")
            else:
                logma.info("No Jupyter server process to stop")
        except Exception as e:
            logma.error(f"Error stopping Jupyter server: {e}")

        return self

    def is_server_running(self):
        """Check if Jupyter server is running"""
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", self.server_port))
            sock.close()
            return result == 0
        except Exception:
            return False

    # ========== Notebook Management Methods ==========

    def create_new_notebook(self, notebook_name=None):
        """Create a new Jupyter notebook"""
        try:
            import nbformat
            from nbformat.v4 import new_notebook, new_code_cell

            # Create a new notebook
            nb = new_notebook()

            # Add a welcome cell
            nb.cells.append(new_code_cell("# New Notebook\nprint('Hello, World!')"))

            # Save the notebook
            if notebook_name is None:
                notebook_name = "Untitled.ipynb"

            save_path = join(dirname(self.file_path) if self.file_path else ".", notebook_name)

            with open(save_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

            logma.info(f"Created new notebook: {save_path}")

            # Open the new notebook in browser
            if self.browser and self.server_running:
                notebook_url = f"{self.server_url}/notebooks/{notebook_name}"
                self.browser.load_url(notebook_url)

        except Exception as e:
            logma.error(f"Error creating new notebook: {e}")

        return self

    def load_notebook_file(self, file_path):
        """Load a notebook file"""
        try:
            if not exists(file_path):
                logma.error(f"Notebook file not found: {file_path}")
                return self

            self.file_path = file_path

            # If server is running, open the notebook
            if self.server_running and self.browser:
                from os.path import basename

                notebook_url = f"{self.server_url}/notebooks/{basename(file_path)}"
                self.browser.load_url(notebook_url)
                logma.info(f"Loaded notebook: {file_path}")
            else:
                logma.warning("Jupyter server not running. Start server to view notebook.")

        except Exception as e:
            logma.error(f"Error loading notebook file: {e}")

        return self

    def save_notebook(self, file_path=None):
        """Save the current notebook"""
        # Note: Jupyter handles saving internally through the web interface
        # This method is mainly for setting the file path
        if file_path:
            self.file_path = file_path
            logma.info(f"Notebook file path set to: {file_path}")
        return self

    def execute_cell(self, cell_code, timeout=60):
        """Execute a specific cell code in the kernel

        Args:
            cell_code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            dict with 'output', 'error', 'status' keys
        """
        if not self.kernel_running or not self.kernel_client:
            logma.error("Kernel not running. Start kernel first.")
            return {"output": "", "error": "Kernel not running", "status": "error"}

        try:
            # Execute the code
            msg_id = self.kernel_client.execute(cell_code)

            # Collect output
            output = []
            error = None
            status = "ok"

            import time

            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    logma.error(f"Cell execution timeout after {timeout}s")
                    return {"output": "\n".join(output), "error": "Execution timeout", "status": "timeout"}

                try:
                    msg = self.kernel_client.get_iopub_msg(timeout=1)

                    if msg["parent_header"].get("msg_id") == msg_id:
                        msg_type = msg["header"]["msg_type"]
                        content = msg["content"]

                        if msg_type == "stream":
                            output.append(content["text"])
                        elif msg_type == "execute_result":
                            output.append(str(content["data"]))
                        elif msg_type == "display_data":
                            output.append(str(content["data"]))
                        elif msg_type == "error":
                            error = "\n".join(content["traceback"])
                            status = "error"
                        elif msg_type == "status" and content["execution_state"] == "idle":
                            break

                except Exception as e:
                    # Check if execution is complete
                    if self.kernel_client.is_alive():
                        continue
                    else:
                        break

            result = {"output": "\n".join(output), "error": error, "status": status}

            logma.info(f"Cell executed with status: {status}")
            return result

        except Exception as e:
            logma.error(f"Error executing cell: {e}")
            return {"output": "", "error": str(e), "status": "error"}

    def execute_all_cells(self, notebook_path=None):
        """Execute all cells in the notebook

        Args:
            notebook_path: Path to .ipynb file, or uses current_notebook_path
        """
        if notebook_path is None:
            notebook_path = self.current_notebook_path

        if not notebook_path or not exists(notebook_path):
            logma.error("No notebook file specified or file not found")
            return self

        try:
            import nbformat

            # Read the notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            # Start kernel if not running
            if not self.kernel_running:
                self.start_kernel()

            # Execute each code cell
            results = []
            for idx, cell in enumerate(nb.cells):
                if cell.cell_type == "code":
                    logma.info(f"Executing cell {idx + 1}/{len(nb.cells)}")
                    result = self.execute_cell(cell.source)
                    results.append(result)

                    # Update cell outputs
                    if result["status"] == "ok":
                        cell.outputs = [{"output_type": "stream", "name": "stdout", "text": result["output"]}]
                    elif result["error"]:
                        cell.outputs = [
                            {
                                "output_type": "error",
                                "ename": "Error",
                                "evalue": result["error"],
                                "traceback": [result["error"]],
                            }
                        ]

            # Save notebook with outputs
            with open(notebook_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

            logma.info(f"Executed {len(results)} cells")

        except Exception as e:
            logma.error(f"Error executing all cells: {e}")

        return self

    def restart_kernel(self):
        """Restart the notebook kernel"""
        try:
            if self.kernel_manager:
                logma.info("Restarting kernel...")
                self.stop_kernel()
                import time

                time.sleep(1)
                self.start_kernel()
                logma.info("Kernel restarted successfully")
            else:
                logma.warning("No kernel manager found")
        except Exception as e:
            logma.error(f"Error restarting kernel: {e}")
        return self

    def shutdown(self):
        """Shutdown the notebook and clean up"""
        self.stop_kernel()
        self.stop_jupyter_server()
        return self

    # ========== Kernel Management Methods ==========

    def start_kernel(self, kernel_name=None):
        """Start a Jupyter kernel for code execution

        Args:
            kernel_name: Name of kernel to start (e.g., 'python3', 'ir', 'julia')
        """
        try:
            from jupyter_client import KernelManager

            if kernel_name is None:
                kernel_name = self.kernel_name

            logma.info(f"Starting kernel: {kernel_name}")

            # Create kernel manager
            self.kernel_manager = KernelManager(kernel_name=kernel_name)
            self.kernel_manager.start_kernel()

            # Create kernel client
            self.kernel_client = self.kernel_manager.client()
            self.kernel_client.start_channels()

            # Wait for kernel to be ready
            import time

            time.sleep(2)

            # Check if kernel is alive
            if self.kernel_client.is_alive():
                self.kernel_running = True
                self.kernel_name = kernel_name
                logma.info(f"Kernel {kernel_name} started successfully")
                self.update_status_labels()
            else:
                logma.error("Kernel failed to start")
                self.kernel_running = False

        except Exception as e:
            logma.error(f"Error starting kernel: {e}")
            self.kernel_running = False

        return self

    def stop_kernel(self):
        """Stop the running kernel"""
        try:
            if self.kernel_client:
                self.kernel_client.stop_channels()
                self.kernel_client = None

            if self.kernel_manager:
                self.kernel_manager.shutdown_kernel()
                self.kernel_manager = None

            self.kernel_running = False
            logma.info("Kernel stopped")
            self.update_status_labels()

        except Exception as e:
            logma.error(f"Error stopping kernel: {e}")

        return self

    def interrupt_kernel(self):
        """Interrupt the running kernel (like Ctrl+C)"""
        try:
            if self.kernel_manager and self.kernel_running:
                self.kernel_manager.interrupt_kernel()
                logma.info("Kernel interrupted")
            else:
                logma.warning("No running kernel to interrupt")
        except Exception as e:
            logma.error(f"Error interrupting kernel: {e}")
        return self

    def get_kernel_info(self):
        """Get information about the running kernel"""
        if not self.kernel_running or not self.kernel_client:
            return None

        try:
            # Request kernel info
            msg_id = self.kernel_client.kernel_info()

            # Wait for response
            import time

            timeout = 5
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        return msg["content"]
                except:
                    continue

            logma.warning("Timeout waiting for kernel info")
            return None

        except Exception as e:
            logma.error(f"Error getting kernel info: {e}")
            return None

    def check_kernel_alive(self):
        """Check if kernel is alive and responsive"""
        if self.kernel_client:
            return self.kernel_client.is_alive()
        return False

    def execute_code_interactive(self, code):
        """Execute code and return output for interactive use

        Args:
            code: Python code to execute

        Returns:
            Formatted output string
        """
        result = self.execute_cell(code)

        output_parts = []
        if result["output"]:
            output_parts.append(result["output"])
        if result["error"]:
            output_parts.append(f"ERROR:\n{result['error']}")

        return "\n".join(output_parts) if output_parts else "Execution completed (no output)"

    def get_completions(self, code, cursor_pos):
        """Get code completions at cursor position

        Args:
            code: Code string
            cursor_pos: Cursor position in code

        Returns:
            List of completion matches
        """
        if not self.kernel_running or not self.kernel_client:
            return []

        try:
            msg_id = self.kernel_client.complete(code, cursor_pos)

            import time

            timeout = 3
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        content = msg["content"]
                        return content.get("matches", [])
                except:
                    continue

            return []

        except Exception as e:
            logma.error(f"Error getting completions: {e}")
            return []

    def inspect_object(self, code, cursor_pos, detail_level=0):
        """Get object inspection/documentation

        Args:
            code: Code string
            cursor_pos: Cursor position
            detail_level: 0 for brief, 1 for detailed

        Returns:
            Inspection data dict
        """
        if not self.kernel_running or not self.kernel_client:
            return None

        try:
            msg_id = self.kernel_client.inspect(code, cursor_pos, detail_level=detail_level)

            import time

            timeout = 3
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        return msg["content"]
                except:
                    continue

            return None

        except Exception as e:
            logma.error(f"Error inspecting object: {e}")
            return None

    # ========== Helper Methods ==========

    def get_available_kernels(self):
        """Get list of available Jupyter kernels"""
        try:
            import subprocess
            import json

            result = subprocess.run(
                ["jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                kernel_data = json.loads(result.stdout)
                kernels = list(kernel_data.get("kernelspecs", {}).keys())
                return kernels if kernels else ["python3"]
            else:
                return ["python3"]

        except Exception as e:
            logma.error(f"Error getting kernels: {e}")
            return ["python3"]

    def update_status_labels(self):
        """Update server and kernel status labels"""
        if hasattr(self, "server_status_label"):
            status = "Running" if self.server_running else "Stopped"
            self.server_status_label.setText(f"Server Status: {status}")

        if hasattr(self, "kernel_status_label"):
            if self.kernel_running:
                kernel_status = f"Running ({self.kernel_name})"
            else:
                kernel_status = "Stopped"
            self.kernel_status_label.setText(f"Kernel Status: {kernel_status}")

        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

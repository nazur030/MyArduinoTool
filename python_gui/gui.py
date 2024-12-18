from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QTextEdit, QLabel, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import serial.tools.list_ports
import subprocess
import json
import os
from serial_monitor import SerialMonitor

SETTINGS_FILE = "settings.json"

# Helper Functions for Settings Management
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Arduino IDE Tool")
        self.setGeometry(300, 100, 800, 600)

        # Main Layout
        main_layout = QVBoxLayout()

        # Top Controls Layout
        top_controls = QHBoxLayout()

        # Board Selector
        self.board_selector = QComboBox()
        self.board_selector.addItems(["esp32:esp32:esp32", "esp32:esp32:esp32dev"])
        top_controls.addWidget(QLabel("Board:"))
        top_controls.addWidget(self.board_selector)

        # COM Port Selector
        self.port_selector = QComboBox()
        self.refresh_ports()
        top_controls.addWidget(QLabel("COM Port:"))
        top_controls.addWidget(self.port_selector)

        # Action Buttons
        self.compile_button = QPushButton("Verify")
        self.compile_button.clicked.connect(self.compile_code)
        top_controls.addWidget(self.compile_button)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_code)
        top_controls.addWidget(self.upload_button)

        self.serial_button = QPushButton("Open Serial Monitor")
        self.serial_button.clicked.connect(self.open_serial_monitor)
        top_controls.addWidget(self.serial_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        top_controls.addWidget(self.save_button)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file)
        top_controls.addWidget(self.open_button)

        # Code Editor
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Courier", 10))
        self.code_editor.setPlaceholderText("Write your Arduino code here...")

        # Console Output (Read-Only)
        self.console_output = QTextEdit()
        self.console_output.setFont(QFont("Courier", 10))
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("Console output will appear here...")

        # Add Widgets to Layouts
        main_layout.addLayout(top_controls)
        main_layout.addWidget(self.code_editor)
        main_layout.addWidget(QLabel("Console Output:"))
        main_layout.addWidget(self.console_output)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Load Previous Settings
        settings = load_settings()
        if "board" in settings:
            index = self.board_selector.findText(settings["board"])
            if index >= 0:
                self.board_selector.setCurrentIndex(index)

        if "port" in settings:
            index = self.port_selector.findText(settings["port"])
            if index >= 0:
                self.port_selector.setCurrentIndex(index)

    def refresh_ports(self):
        """ Refresh COM Ports """
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def log_to_console(self, message, error=False):
        """ Log messages to the console """
        if error:
            self.console_output.append(f"<span style='color:red;'>[ERROR] {message}</span>")
        else:
            self.console_output.append(f"<span style='color:green;'>[INFO] {message}</span>")

    def compile_code(self):
        """ Verify (Compile) the Code """
        board = self.board_selector.currentText()
        code = self.code_editor.toPlainText()

        # Create the sketch folder if it doesn't exist
        sketch_folder = "sketch"
        os.makedirs(sketch_folder, exist_ok=True)

        # Ensure only one file exists
        sketch_file = os.path.join(sketch_folder, "sketch.ino")

        # Remove any conflicting files
        for file in os.listdir(sketch_folder):
            if file.endswith(".ino") and file != "sketch.ino":
                os.remove(os.path.join(sketch_folder, file))

        # Save the code to sketch.ino
        with open(sketch_file, "w") as f:
            f.write(code)

        cmd = ["arduino-cli", "compile", "--fqbn", board, sketch_folder]
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            self.log_to_console("Compilation Successful!")
        else:
            self.log_to_console(process.stderr, error=True)

        self.console_output.append(process.stdout)


    def upload_code(self):
        """ Verify and Upload the Code """
        board = self.board_selector.currentText()
        port = self.port_selector.currentText()

        # Call compile_code() to verify before uploading
        self.compile_code()

        # Ensure correct sketch path
        sketch_folder = "sketch"

        cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", board, sketch_folder]
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            self.log_to_console("Upload Successful!")
        else:
            self.log_to_console(process.stderr, error=True)

        self.console_output.append(process.stdout)


    def save_file(self):
        """ Save Sketch to a File """
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Arduino Files (*.ino);;All Files (*)")
        if filename:
            with open(filename, "w") as f:
                f.write(self.code_editor.toPlainText())
            self.log_to_console(f"File saved: {filename}")

    def open_file(self):
        """ Open an Existing Sketch """
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Arduino Files (*.ino);;All Files (*)")
        if filename:
            with open(filename, "r") as f:
                content = f.read()
            self.code_editor.setPlainText(content)
            self.log_to_console(f"File opened: {filename}")

    def open_serial_monitor(self):
        """ Launch Serial Monitor """
        port = self.port_selector.currentText()
        if port:
            self.serial_monitor = SerialMonitor(port)
            self.serial_monitor.show()
        else:
            self.log_to_console("No COM Port Selected!", error=True)

    def closeEvent(self, event):
        """ Save Settings on Close """
        settings = {
            "board": self.board_selector.currentText(),
            "port": self.port_selector.currentText(),
        }
        save_settings(settings)

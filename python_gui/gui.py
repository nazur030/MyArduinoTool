from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QComboBox, QLabel, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import serial.tools.list_ports
import subprocess
import os
from serial_monitor import SerialMonitor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ESP32 GPIO Tool")
        self.setGeometry(300, 100, 800, 600)

        # Main Layout
        main_layout = QVBoxLayout()

        # Top Controls
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
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        top_controls.addWidget(self.add_row_button)

        self.upload_button = QPushButton("Generate & Upload")
        self.upload_button.clicked.connect(self.generate_and_upload)
        top_controls.addWidget(self.upload_button)

        # GPIO Table
        self.gpio_table = QTableWidget()
        self.gpio_table.setColumnCount(2)
        self.gpio_table.setHorizontalHeaderLabels(["GPIO Pin", "Delay (ms)"])
        self.gpio_table.setFont(QFont("Courier", 10))

        # Console Output
        self.console_output = QLabel("Console Output will appear here...")
        self.console_output.setWordWrap(True)

        # Add Widgets to Layouts
        main_layout.addLayout(top_controls)
        main_layout.addWidget(self.gpio_table)
        main_layout.addWidget(self.console_output)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.serial_button = QPushButton("Open Serial Monitor")
        self.serial_button.clicked.connect(self.open_serial_monitor)
        top_controls.addWidget(self.serial_button)

    def open_serial_monitor(self):
        """ Launch Serial Monitor Window """
        port = self.port_selector.currentText()
        if port:
            self.serial_monitor = SerialMonitor(port)
            self.serial_monitor.show()
        else:
            self.console_output.setText("No COM Port Selected!")

    def refresh_ports(self):
        """ Refresh COM Ports """
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def add_row(self):
        """ Add a new row to the GPIO table """
        row = self.gpio_table.rowCount()
        self.gpio_table.insertRow(row)

    def generate_and_upload(self):
        """ Generate Arduino Code and Upload """
        board = self.board_selector.currentText()
        port = self.port_selector.currentText()

        # Generate Arduino Code
        code = """
void setup() {
"""

        # Generate the pinMode setup
        for row in range(self.gpio_table.rowCount()):
            gpio_pin = self.gpio_table.item(row, 0)
            if gpio_pin:
                code += f"  pinMode({gpio_pin.text()}, OUTPUT);\n"

        code += "}\n\nvoid loop() {\n"

        # Generate the loop logic
        for row in range(self.gpio_table.rowCount()):
            gpio_pin = self.gpio_table.item(row, 0)
            delay_ms = self.gpio_table.item(row, 1)

            if gpio_pin and delay_ms:
                code += f"  digitalWrite({gpio_pin.text()}, HIGH);\n"
                code += f"  delay({delay_ms.text()});\n"
                code += f"  digitalWrite({gpio_pin.text()}, LOW);\n"
                code += f"  delay({delay_ms.text()});\n"

        code += "}\n"

        # Save Arduino Sketch
        sketch_folder = "sketch"
        os.makedirs(sketch_folder, exist_ok=True)
        sketch_file = os.path.join(sketch_folder, "sketch.ino")

        with open(sketch_file, "w") as f:
            f.write(code)

        # Compile and Upload
        compile_cmd = ["arduino-cli", "compile", "--fqbn", board, sketch_folder]
        upload_cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", board, sketch_folder]

        compile_process = subprocess.run(compile_cmd, capture_output=True, text=True)
        if compile_process.returncode == 0:
            self.console_output.setText("Compilation Successful!")
        else:
            self.console_output.setText(f"Compile Error:\n{compile_process.stderr}")
            return

        upload_process = subprocess.run(upload_cmd, capture_output=True, text=True)
        if upload_process.returncode == 0:
            self.console_output.setText("Upload Successful!")
        else:
            self.console_output.setText(f"Upload Error:\n{upload_process.stderr}")

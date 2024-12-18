import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QApplication
from PyQt5.QtCore import QTimer
import serial
import serial.tools.list_ports


class SerialMonitor(QMainWindow):
    def __init__(self, port, baudrate=115200):
        super().__init__()

        self.setWindowTitle(f"Serial Monitor - {port}")
        self.setGeometry(300, 100, 600, 400)

        # Initialize Serial Connection
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)

        # Create Widgets
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.refresh_button = QPushButton("Clear Screen")
        self.refresh_button.clicked.connect(self.clear_screen)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.refresh_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for Reading Data
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(500)  # Update every 500ms

    def read_serial_data(self):
        """ Read data from the serial port """
        if self.serial_conn.in_waiting:
            data = self.serial_conn.readline().decode("utf-8").strip()
            self.text_area.append(data)

    def clear_screen(self):
        """ Clear the console output """
        self.text_area.clear()

    def closeEvent(self, event):
        """ Close the serial port on exit """
        self.serial_conn.close()

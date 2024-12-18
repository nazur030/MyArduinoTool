from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
import serial
import threading
import time


class SerialMonitor(QDialog):
    def __init__(self, port, baudrate=115200, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Monitor")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        # Text Output
        self.text_output = QTextEdit(self)
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        # Close Button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close_monitor)
        layout.addWidget(self.close_button)

        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.running = True

        # Start Reading Thread
        self.thread = threading.Thread(target=self.read_from_serial)
        self.thread.start()

    def read_from_serial(self):
        while self.running:
            if self.serial_port.in_waiting:
                line = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                self.text_output.append(line)
            time.sleep(0.1)

    def close_monitor(self):
        self.running = False
        self.serial_port.close()
        self.close()

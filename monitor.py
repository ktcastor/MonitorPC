import sys
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint, QSettings

class KawaiiMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kawaii Monitor 💖")
        self.resize(400, 400)

        # Quitar botones → tipo widget flotante
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Opacidad al 80%
        self.setWindowOpacity(0.8)

        # Fondo kawaii pastel
        self.setStyleSheet("background-color: #ffe6f9; border-radius: 15px;")

        # Layout
        layout = QVBoxLayout()

        # CPU
        self.cpu_label = QLabel("CPU: 0%", self)
        self.cpu_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff69b4;")
        self.cpu_bar = QProgressBar(self)
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ffb6c1;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #ff69b4;
                width: 20px;
            }
        """)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)

        # RAM
        self.ram_label = QLabel("RAM: 0%", self)
        self.ram_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ba55d3;")
        self.ram_bar = QProgressBar(self)
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dda0dd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #ba55d3;
                width: 20px;
            }
        """)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.ram_bar)

        # Discos
        self.disk_labels = []
        self.disk_bars = []
        colors = ["#ff7f50", "#87cefa", "#98fb98", "#ffd700", "#ff1493"]

        partitions = psutil.disk_partitions()
        for i, part in enumerate(partitions):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue

            label = QLabel(f"Disco {part.device} ({part.mountpoint}): {usage.percent}%", self)
            label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
            bar = QProgressBar(self)
            bar.setRange(0, 100)
            color = colors[i % len(colors)]
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid {color};
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    width: 20px;
                }}
            """)

            layout.addWidget(label)
            layout.addWidget(bar)

            self.disk_labels.append(label)
            self.disk_bars.append(bar)

        self.setLayout(layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_usage)
        self.timer.start(1000)

        # Variables para arrastrar
        self.dragging = False
        self.drag_position = QPoint()

        # Restaurar posición guardada
        self.settings = QSettings("MiEmpresa", "KawaiiMonitor")
        pos = self.settings.value("pos", None)
        if pos:
            self.move(pos)

    def update_usage(self):
        # CPU
        cpu_usage = psutil.cpu_percent(interval=0.5)
        self.cpu_bar.setValue(int(cpu_usage))
        self.cpu_label.setText(f"CPU: {cpu_usage}%")

        # RAM
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        self.ram_bar.setValue(int(ram_usage))
        self.ram_label.setText(f"RAM: {ram_usage}%")

        # Discos
        partitions = psutil.disk_partitions()
        for i, part in enumerate(partitions):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue
            if i < len(self.disk_labels):
                self.disk_bars[i].setValue(int(usage.percent))
                self.disk_labels[i].setText(f"Disco {part.device} ({part.mountpoint}): {usage.percent}%")

    # Eventos para arrastrar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            # Guardar posición
            self.settings.setValue("pos", self.pos())
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KawaiiMonitor()
    window.show()
    sys.exit(app.exec())

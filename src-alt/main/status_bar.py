from PySide6.QtWidgets import (
    QLabel, QStatusBar, QHBoxLayout, QWidget
)
from PySide6.QtGui import QMovie


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_label = QLabel("Ready")
        self.spinner = QLabel(self)

        self.animation = QMovie("spinner.gif")
        self.spinner.setFixedSize(16, 16)
        self.spinner.setMovie(self.animation)
        self.spinner.setVisible(False)

        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.spinner)
        self.status_layout.setContentsMargins(10, 5, 0, 5)
        self.status_layout.addStretch()

        container_widget = QWidget()
        container_widget.setLayout(self.status_layout)
        self.addWidget(container_widget)

    def toggle_spinner(self, button):
        if self.spinner.isVisible():
            self.update_status(working=False)
            button.setText("Run clustering")
        else:
            self.update_status("Clustering...", working=True)
            button.setText("Stop clustering")

    def update_status(self, message="Ready", working=True):
        self.status_label.setText(message)
        if working:
            self.spinner.setVisible(True)
            self.animation.start()
        else:
            self.spinner.setVisible(False)
            self.animation.stop()

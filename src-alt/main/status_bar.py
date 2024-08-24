from PySide6.QtWidgets import (
    QLabel, QStatusBar, QHBoxLayout, QWidget
)
from PySide6.QtGui import QMovie


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statusLabel = QLabel("Ready")
        self.spinner = QLabel(self)

        self.animation = QMovie("spinner.gif")
        self.spinner.setFixedSize(16, 16)
        self.spinner.setMovie(self.animation)
        self.spinner.setVisible(False)

        self.statusLayout = QHBoxLayout()
        self.statusLayout.addWidget(self.statusLabel)
        self.statusLayout.addWidget(self.spinner)
        self.statusLayout.setContentsMargins(10, 5, 0, 5)
        self.statusLayout.addStretch()

        containerWidget = QWidget()
        containerWidget.setLayout(self.statusLayout)
        self.addWidget(containerWidget)

    def toggleSpinner(self, button):
        if self.spinner.isVisible():
            self.updateStatus(working=False)
            button.setText("Run clustering")
        else:
            self.updateStatus("Clustering...", working=True)
            button.setText("Stop clustering")

    def updateStatus(self, message="Ready", working=True):
        self.statusLabel.setText(message)
        if working:
            self.spinner.setVisible(True)
            self.animation.start()
        else:
            self.spinner.setVisible(False)
            self.animation.stop()

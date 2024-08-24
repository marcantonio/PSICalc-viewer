from PySide6.QtWidgets import QMessageBox, QPlainTextEdit
from PySide6.QtGui import QFont


class ErrorDialog(QMessageBox):
    def __init__(self, parent, title, message, details):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Critical)
        self.setText(message)
        self.setStandardButtons(QMessageBox.Ok)

        if details:
            textEdit = QPlainTextEdit()
            textEdit.setPlainText(details)
            textEdit.setReadOnly(True)
            textEdit.setMinimumSize(400, 200)

            font = QFont("Courier")
            font.setStyleHint(QFont.Monospace)
            font.setFixedPitch(True)
            font.setWeight(QFont.Normal)
            textEdit.setFont(font)

            layout = self.layout()
            layout.addWidget(textEdit, layout.rowCount(), 0, 1, layout.columnCount())

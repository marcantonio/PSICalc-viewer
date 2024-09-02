import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from model.merged_msa import MergedMsa
from view.main import MainWindow

import resources  # noqa: F401

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(":icons/icon.ico"))

# Start with a dummy row to calculate the row height
mergedMsa = MergedMsa()
window = MainWindow(mergedMsa)
window.show()

app.exec()

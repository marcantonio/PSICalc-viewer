from PySide6.QtWidgets import QApplication
import sys

from model.merged_msa import MergedMsa
from view.main import MainWindow

app = QApplication(sys.argv)

# Start with a dummy row to calculate the row height
mergedMsa = MergedMsa()
window = MainWindow(mergedMsa)
window.show()

app.exec()

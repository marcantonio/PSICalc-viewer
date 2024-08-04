from PySide6.QtWidgets import QApplication, QMainWindow
from msa_table_view import MsaTableView
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSICalc Viewer")
        self.resize(700, 500)

        # Initial data
        data = [
            ["Label1", "file1.txt", "Align1", "A: T\nG: F\nT: F", ""],
            ["Label2", "file2.txt", "Align2", "A: T\nG: F\nT: F", ""],
        ]

        msa_table = MsaTableView(data)
        self.setCentralWidget(msa_table)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QGroupBox
import sys

from main.clustering_params import ClusteringParams
from main.msa_table_view import MsaTableView
from main.status_bar import StatusBar
from msa_files import MsaFiles


class MainWindow(QMainWindow):
    def __init__(self, view_model):
        super().__init__()
        self.setWindowTitle("PSICalc Viewer")
        self.resize(1000, 700)

        # data = [
        #     ["A", "msa_file1.txt", "None", "Columns: 3444\nSequences: 439\nLabels: A0...A3443", ""],
        #     ["B", "msa_file2.txt", "MUSCLE", "Columns: 1175\nSequences: 439\nLabels: B0...B1174", ""],
        # ]

        # Toplevel container
        container = QWidget(self)
        self.setCentralWidget(container)
        vbox = QVBoxLayout()
        container.setLayout(vbox)

        # MSA files table
        msa_groupbox = QGroupBox("MSA files")
        msa_layout = QVBoxLayout(msa_groupbox)
        msa_table = MsaTableView(self, view_model)
        msa_layout.addWidget(msa_table)
        vbox.addWidget(msa_groupbox)

        # Lower views
        hbox = QHBoxLayout()
        vbox.addLayout(hbox, 1)

        # Clustering parameters
        clustering_params = ClusteringParams()
        clustering_params_groupbox = QGroupBox("Clustering parameters")
        clustering_params_layout = QVBoxLayout()
        clustering_params_layout.addWidget(clustering_params)
        clustering_params_groupbox.setLayout(clustering_params_layout)
        hbox.addWidget(clustering_params_groupbox, 1)

        text_box = QPlainTextEdit()
        hbox.addWidget(text_box, 2)

        # Status Bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        clustering_params.runClicked.connect(self.status_bar.toggle_spinner)


msa_files = MsaFiles()

app = QApplication(sys.argv)

window = MainWindow(msa_files)
window.show()

app.exec()

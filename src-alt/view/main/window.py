from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QGroupBox

from .clustering_params import ClusteringParams
from ..error_dialog import ErrorDialog
from .msa_table_view import MsaTableView
from .status_bar import StatusBar
from model.msa_file_table import MsaFileTable


class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()

        self.model = model
        self.model.error.connect(self.showError)

        self.setWindowTitle("PSICalc Viewer")
        self.resize(1000, 700)

        # Toplevel container
        container = QWidget(self)
        self.setCentralWidget(container)
        vbox = QVBoxLayout()
        container.setLayout(vbox)

        # MSA files table
        msaGroupbox = QGroupBox("MSA files")
        msaLayout = QVBoxLayout(msaGroupbox)
        msaTableModel = MsaFileTable(self.model)
        msaTableModel.error.connect(self.showError)
        msaTable = MsaTableView(msaTableModel, self)
        msaLayout.addWidget(msaTable)
        vbox.addWidget(msaGroupbox)

        # Lower views
        hbox = QHBoxLayout()
        vbox.addLayout(hbox, 1)

        # Clustering parameters
        clusteringParams = ClusteringParams(self.model, self)
        clusteringParamsGroupbox = QGroupBox("Clustering parameters")
        clusteringParamsLayout = QVBoxLayout()
        clusteringParamsLayout.addWidget(clusteringParams)
        clusteringParamsGroupbox.setLayout(clusteringParamsLayout)
        hbox.addWidget(clusteringParamsGroupbox, 1)

        textBox = QPlainTextEdit(self)
        hbox.addWidget(textBox, 2)

        # Status Bar
        self.statusBar = StatusBar(self)
        self.setStatusBar(self.statusBar)
        clusteringParams.runClicked.connect(self.statusBar.toggleSpinner)

    def showError(self, title, message, details):
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()

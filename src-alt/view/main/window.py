from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QGroupBox
from PySide6.QtCore import QThreadPool

from ..error_dialog import ErrorDialog
from ..worker import Worker
from model.msa_file_table import MsaFileTable
from .clustering_params import ClusteringParams
from .msa_table_view import MsaTableView
from .status_bar import StatusBar


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
        self.clusteringParams = ClusteringParams(self.model, self)
        clusteringParamsGroupbox = QGroupBox("Clustering parameters")
        clusteringParamsLayout = QVBoxLayout()
        clusteringParamsLayout.addWidget(self.clusteringParams)
        clusteringParamsGroupbox.setLayout(clusteringParamsLayout)
        hbox.addWidget(clusteringParamsGroupbox, 1)

        textBox = QPlainTextEdit(self)
        hbox.addWidget(textBox, 2)

        # Status Bar
        self.statusBar = StatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.updateRunButton.connect(self.clusteringParams.updateRunButtonText)
        self.clusteringParams.runClicked.connect(self.onRunClicked)

        self.worker = None
        self.clusteringRunning = False

    def showError(self, title, message, details):
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()

    def onRunClicked(self, button):
        if self.clusteringRunning:
            self.clusteringRunning = False
            self.statusBar.disableSpinner()
            self.worker.cancel()
        else:
            self.clusteringRunning = True
            self.statusBar.enableSpinner()
            self.worker = Worker(self.model.runClustering)
            self.worker.signals.result.connect(self.clusteringSuccess)
            self.worker.signals.finished.connect(self.finished)
            self.worker.signals.error.connect(self.clusteringError)
            QThreadPool.globalInstance().start(self.worker)

    def finished(self):
        self.clusteringRunning = False
        self.statusBar.disableSpinner()
        print("Done")

    def clusteringSuccess(self, result):
        print("result: " + result)

    def clusteringError(self, e):
        print("Error running psicalc: ")
        print(e)

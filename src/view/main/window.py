import sys

from PySide6.QtCore import QThreadPool, QObject, Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QGroupBox
from PySide6.QtGui import QTextCursor, QFont

from ..error_dialog import ErrorDialog
from model.msa_file_table import MsaFileTable
from .clustering_params import ClusteringParams
from .msa_table_view import MsaTableView
from .status_bar import StatusBar
from ..tree_view import TreeView
from worker import Worker


class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()

        self.model = model
        self.model.error.connect(self.showError)
        self.worker = None
        self.clusteringRunning = False

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
        self.msaTableModel = MsaFileTable(self.model)
        self.msaTableModel.error.connect(self.showError)
        msaTable = MsaTableView(self.msaTableModel, self)
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

        # Text box
        self.textBox = QPlainTextEdit(self)
        hbox.addWidget(self.textBox, 2)
        font = QFont("Menlo, Consolas, DejaVu Sans Mono")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.textBox.setFont(font)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        # Status Bar
        self.statusBar = StatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.updateRunButton.connect(self.clusteringParams.updateRunButtonText)
        self.clusteringParams.runClicked.connect(self.onRunClicked)

    def showError(self, title, message, details):
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()

    def onRunClicked(self, button):
        if self.clusteringRunning:
            self.clusteringRunning = False
            self.clusteringParams.enableControls()
            self.statusBar.disableSpinner()
            self.worker.cancel()
        else:
            if self.msaTableModel.rowCount() == 0:
                self.showError("Error", "Please add some files", None)
                return

            self.clusteringRunning = True
            self.clusteringParams.disableControls()
            self.statusBar.enableSpinner()

            self.worker = Worker(self.model.runClustering)
            self.worker.signals.result.connect(self.clusteringSuccess)
            self.worker.signals.finished.connect(self.finished)
            self.worker.signals.error.connect(self.clusteringError)
            QThreadPool.globalInstance().start(self.worker)

    # Called when cluster worker finishes, regardless of success
    def finished(self):
        self.clusteringParams.enableControls()
        self.clusteringRunning = False
        self.statusBar.disableSpinner()

    def clusteringSuccess(self, results):
        self.treeView = TreeView(results.clusterMap, results.mergedMsa, results.lowEntropySites, results.columnMap)
        self.treeView.show()

    def clusteringError(self, e):
        self.showError("Error", "Clustering failed", e)

    def normalOutputWritten(self, text):
        cursor = self.textBox.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textBox.setTextCursor(cursor)
        self.textBox.ensureCursorVisible()


class EmittingStream(QObject):
    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

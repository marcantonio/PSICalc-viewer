from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QGroupBox
import sys

from error_dialog import ErrorDialog
from main.clustering_params import ClusteringParams
from main.msa_table_view import MsaTableView
from main.status_bar import StatusBar
from msa_files import MsaFiles


class MainWindow(QMainWindow):
    def __init__(self, viewModel):
        super().__init__()
        self.viewModel = viewModel

        # For errors from the model
        self.viewModel.error.connect(self.showError)

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
        msaTable = MsaTableView(self, viewModel)
        msaLayout.addWidget(msaTable)
        vbox.addWidget(msaGroupbox)

        # Lower views
        hbox = QHBoxLayout()
        vbox.addLayout(hbox, 1)

        # Clustering parameters
        clusteringParams = ClusteringParams()
        clusteringParamsGroupbox = QGroupBox("Clustering parameters")
        clusteringParamsLayout = QVBoxLayout()
        clusteringParamsLayout.addWidget(clusteringParams)
        clusteringParamsGroupbox.setLayout(clusteringParamsLayout)
        hbox.addWidget(clusteringParamsGroupbox, 1)

        textBox = QPlainTextEdit()
        hbox.addWidget(textBox, 2)

        # Status Bar
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)
        clusteringParams.runClicked.connect(self.statusBar.toggleSpinner)

    def showError(self, title, message, details):
        dialog = ErrorDialog(self, title, message, details)
        dialog.exec()


app = QApplication(sys.argv)

# Start with a dummy row to calculate the row height
msa_files = MsaFiles([["", "", "None", "", ""]])
window = MainWindow(msa_files)
window.show()
# Remove the dummy row used to calculate table height
# TODO: Don't do this if real data is passed in
window.viewModel.removeFile(0)

app.exec()

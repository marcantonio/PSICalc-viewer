from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QStatusBar,
    QDoubleSpinBox, QPlainTextEdit, QGroupBox, QFormLayout, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QMovie

from msa_table_view import MsaTableView
import sys


class ClusteringParams(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QFormLayout(self)

        durston_labeling = QRadioButton("Label using column:")
        deweese_labeling = QRadioButton("Label using first row mapping")
        labeling_buttongroup = QButtonGroup(self)
        labeling_buttongroup.addButton(durston_labeling)
        labeling_buttongroup.addButton(deweese_labeling)

        durston_layout = QHBoxLayout()
        durston_layout.addStretch(1)
        durston_layout.setAlignment(Qt.AlignLeft)
        durston_labeling.setChecked(True)
        durston_layout.addWidget(durston_labeling)
        durston_layout.addWidget(QSpinBox())
        durston_layout.addStretch(3)
        layout.addRow(durston_layout)

        deweese_layout = QHBoxLayout()
        deweese_layout.addStretch(5)
        deweese_layout.addWidget(deweese_labeling)
        deweese_layout.addStretch(12)
        layout.addRow(deweese_layout)

        insertion_layout = QHBoxLayout()
        insertion_spinbox = QSpinBox()
        insertion_spinbox.setRange(0, 100)
        insertion_spinbox.setSuffix("%")
        insertion_layout.addWidget(insertion_spinbox)
        layout.addRow(QLabel("Non-insertion percentage:"), insertion_layout)

        spread_spinbox = QSpinBox()
        layout.addRow(QLabel("Spread:"), spread_spinbox)

        entropy_cutoff_spinbox = QDoubleSpinBox()
        entropy_cutoff_spinbox.setDecimals(2)
        entropy_cutoff_spinbox.setRange(0.0, 0.25)
        entropy_cutoff_spinbox.setSingleStep(0.01)

        layout.addRow(QLabel("Entropy cutoff:"), entropy_cutoff_spinbox)

        run_button_layout = QHBoxLayout()
        run_button = QPushButton("Run clustering")
        run_button_layout.setAlignment(Qt.AlignCenter)
        run_button_layout.addWidget(run_button)
        run_button.clicked.connect(self.toggle_spinner)
        layout.addRow(run_button_layout)

    def toggle_spinner(self):
        self.main_window.toggle_spinner(self.sender())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSICalc Viewer")
        self.resize(1000, 700)

        data = [
            ["A", "msa_file1.txt", "None", "Columns: 3444\nSequences: 439\nLabels: A0...A3443", ""],
            ["B", "msa_file2.txt", "MUSCLE", "Columns: 1175\nSequences: 439\nLabels: B0...B1174", ""],
        ]

        # Toplevel container
        container = QWidget(self)
        self.setCentralWidget(container)

        vbox = QVBoxLayout()
        container.setLayout(vbox)

        # File table
        msa_groupbox = QGroupBox("MSA files")
        msa_layout = QVBoxLayout(msa_groupbox)
        msa_table = MsaTableView(data)
        msa_layout.addWidget(msa_table)
        vbox.addWidget(msa_groupbox)

        # Lower views
        hbox = QHBoxLayout()
        vbox.addLayout(hbox, 1)

        # Clustering parameters
        clustering_params = ClusteringParams(self)
        clustering_params_groupbox = QGroupBox("Clustering parameters")
        clustering_params_layout = QVBoxLayout()
        clustering_params_layout.addWidget(clustering_params)
        clustering_params_groupbox.setLayout(clustering_params_layout)
        hbox.addWidget(clustering_params_groupbox, 1)

        text_box = QPlainTextEdit()
        hbox.addWidget(text_box, 2)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.spinner = QLabel(self)

        self.animation = QMovie("spinner.gif")
        self.spinner.setFixedSize(16, 16)
        self.spinner.setMovie(self.animation)
        self.spinner.setVisible(False)

        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.spinner)
        self.status_layout.setContentsMargins(10, 5, 0, 5)
        self.status_layout.addStretch()

        container_widget = QWidget()
        container_widget.setLayout(self.status_layout)
        self.status_bar.addWidget(container_widget)

        self.setStatusBar(self.status_bar)

    def toggle_spinner(self, button):
        if self.spinner.isVisible():
            self.update_status(working=False)
            button.setText("Run clustering")
        else:
            self.update_status("Clustering...", working=True)
            button.setText("Stop clustering")

    def update_status(self, message="Ready", working=True):
        self.status_label.setText(message)
        if working:
            self.spinner.setVisible(True)
            self.animation.start()
        else:
            self.spinner.setVisible(False)
            self.animation.stop()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

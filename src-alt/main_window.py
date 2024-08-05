from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSpinBox, QSlider, QPushButton, QPlainTextEdit, QGroupBox, QFormLayout, QRadioButton, QButtonGroup
)
from msa_table_view import MsaTableView
import sys


class ClusteringParams(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout(self)

        deweese_labeling = QRadioButton("Label using first row mapping")
        durston_labeling = QRadioButton("Label using column:")
        labeling_buttongroup = QButtonGroup(self)
        labeling_buttongroup.addButton(deweese_labeling)
        labeling_buttongroup.addButton(durston_labeling)
        labeling_vbox = QVBoxLayout()
        labeling_vbox.addWidget(deweese_labeling)
        labeling_hbox = QHBoxLayout()
        labeling_hbox.addWidget(durston_labeling)
        labeling_hbox.addWidget(QSpinBox())
        labeling_hbox.addStretch()
        labeling_vbox.addLayout(labeling_hbox)
        layout.addRow(labeling_vbox)

        insertion_removal_layout = QHBoxLayout()
        insertion_removal_slider = QSlider(Qt.Horizontal)
        self.insertion_removal_label = QLabel("0%")
        insertion_removal_layout.addWidget(insertion_removal_slider)
        insertion_removal_layout.addWidget(self.insertion_removal_label)
        insertion_removal_layout.addStretch()  # Ensure label is right-aligned
        layout.addRow(QLabel("Non-insertion percentage:"), insertion_removal_layout)
        insertion_removal_slider.valueChanged.connect(self.update_insertion_removal_label)

        spread_spinbox = QSpinBox()
        layout.addRow(QLabel("Spread:"), spread_spinbox)

        entropy_cutoff_spinbox = QSpinBox()
        layout.addRow(QLabel("Entropy cutoff:"), entropy_cutoff_spinbox)

        run_clustering_button = QPushButton("Run clustering")
        layout.addRow(run_clustering_button)

    def update_insertion_removal_label(self, value):
        self.insertion_removal_label.setText(f"{value}%")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSICalc Viewer")
        self.resize(1000, 700)

        data = [
            ["Label1", "file1.txt", "Align1", "A: T\nG: F\nT: F", ""],
            ["Label2", "file2.txt", "Align2", "A: T\nG: F\nT: F", ""],
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

        # Lower viewes
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


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

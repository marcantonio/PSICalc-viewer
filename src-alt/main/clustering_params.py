from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QFormLayout, QRadioButton, QButtonGroup


class ClusteringParams(QWidget):
    runClicked = Signal(QObject)

    def __init__(self):
        super().__init__()
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
        run_button.clicked.connect(lambda: self.on_run_button_clicked(run_button))
        layout.addRow(run_button_layout)

    def on_run_button_clicked(self, button):
        self.runClicked.emit(button)

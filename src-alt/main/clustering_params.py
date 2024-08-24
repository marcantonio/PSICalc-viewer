from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QFormLayout, QRadioButton, QButtonGroup


class ClusteringParams(QWidget):
    runClicked = Signal(QObject)

    def __init__(self, viewModel, parent=None):
        super().__init__(parent)
        self.viewModel = viewModel

        layout = QFormLayout(self)

        # Durston radio button
        durstonLayout = QHBoxLayout()
        durstonLayout.addStretch(1)
        durstonLayout.setAlignment(Qt.AlignLeft)
        durstonRowLabeling = QRadioButton("Label using column:")
        durstonRowLabeling.setChecked(True)
        durstonRowLabeling.toggled.connect(lambda checked: durstonColumnSpinBox.setEnabled(checked))
        durstonLayout.addWidget(durstonRowLabeling)

        # Durston column spinbox
        durstonColumnSpinBox = QSpinBox()
        durstonColumnSpinBox.valueChanged.connect(self.viewModel.updateDurstonColumn)
        durstonLayout.addWidget(durstonColumnSpinBox)
        durstonLayout.addStretch(3)
        layout.addRow(durstonLayout)

        # Deweese radio button
        deweeseLayout = QHBoxLayout()
        deweeseLayout.addStretch(5)
        deweeseRowLabeling = QRadioButton("Label using first row mapping")
        deweeseLayout.addWidget(deweeseRowLabeling)
        deweeseLayout.addStretch(12)
        layout.addRow(deweeseLayout)

        # Button group for both
        rowLabelingButtonGroup = QButtonGroup(self)
        rowLabelingButtonGroup.addButton(durstonRowLabeling, 1)
        rowLabelingButtonGroup.addButton(deweeseRowLabeling, 2)
        rowLabelingButtonGroup.idToggled.connect(self.onRowLabelingClicked)

        # Insertion spinbox
        insertionLayout = QHBoxLayout()
        insertionSpinbox = QSpinBox()
        insertionSpinbox.setRange(0, 100)
        insertionSpinbox.setSuffix("%")
        insertionSpinbox.valueChanged.connect(self.viewModel.updateInsertion)
        insertionLayout.addWidget(insertionSpinbox)
        layout.addRow(QLabel("Non-insertion percentage:"), insertionLayout)

        # Spread spinbox
        spreadSpinbox = QSpinBox()
        spreadSpinbox.setRange(1, 99)
        spreadSpinbox.valueChanged.connect(self.viewModel.updateSpread)
        layout.addRow(QLabel("Spread:"), spreadSpinbox)

        # Entropy cutoff spinbox
        entropyCutoffSpinbox = QDoubleSpinBox()
        entropyCutoffSpinbox.setDecimals(2)
        entropyCutoffSpinbox.setRange(0.0, 0.25)
        entropyCutoffSpinbox.setSingleStep(0.01)
        entropyCutoffSpinbox.valueChanged.connect(self.viewModel.updateEntropyCutoff)
        layout.addRow(QLabel("Entropy cutoff:"), entropyCutoffSpinbox)

        # Run button
        runButtonLayout = QHBoxLayout()
        runButton = QPushButton("Run clustering")
        runButtonLayout.setAlignment(Qt.AlignCenter)
        runButtonLayout.addWidget(runButton)
        runButton.clicked.connect(lambda: self.onRunButtonClicked(runButton))
        layout.addRow(runButtonLayout)

    def onRunButtonClicked(self, button):
        self.runClicked.emit(button)

    def onRowLabelingClicked(self, id, checked):
        if checked:
            self.viewModel.updateRowLabelingMethod("durston" if id == 1 else "deweese")

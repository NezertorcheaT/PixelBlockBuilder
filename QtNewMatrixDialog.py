from PyQt6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
)

from QtVecEntry import *

styleN = '''
border-style: outset;
border-width: 1px;
border-radius: 10px;
border-color: gray;
'''


class CreateNewMatrixDialog(QDialog):
    def __init__(self, title="Create New Matrix", message="Input for new size:"):
        super().__init__()

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.vec = VecEntry(3)
        self.vec.setValue((1, 1, 1))
        self.vec.setMinimum((1, 1, 1))
        self.layout.addWidget(message)
        self.layout.addWidget(self.vec)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.setMinimumSize(250, 120)
        self.setMaximumSize(650, 120)

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Matrix")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Select new size")
        self.vec = Vec3Entry()
        self.vec.setValue((1, 1, 1))
        self.vec.setMinimum((1, 1, 1))
        self.layout.addWidget(message)
        self.layout.addWidget(self.vec)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.setMinimumSize(250, 120)
        self.setMaximumSize(650, 120)
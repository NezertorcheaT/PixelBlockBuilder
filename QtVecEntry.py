import os

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QLabel,
    QSpinBox,
    QHBoxLayout,
    QSizePolicy
)

styleQl = '''
QLabel {
border-style: solid;
border-width: 1px;
border-radius: 10px;
border-color: gray;
}
'''
with open(f'{os.path.dirname(__file__)}\\style.qss', 'r') as f:
    style = f.read()


class VecEntry(QLabel):
    valueChanged = pyqtSignal()

    @pyqtSlot()
    def valueChangedSlot(status, source):
        pass

    def __init__(self, size: int):
        super().__init__()
        self.setStyleSheet(style + styleQl)
        self.lay = QHBoxLayout()
        self.setLayout(self.lay)
        self.vec_size = size

        self.__Entries = [QSpinBox() for _ in range(self.vec_size)]
        self.__textLabel = QLabel(f"Vec{self.vec_size}:")

        for i in self.__Entries:
            i.valueChanged.connect(self.valueChanged.emit)

        self.lay.addWidget(self.__textLabel)
        for i in self.__Entries:
            self.lay.addWidget(i)

        # self.setFixedSize(200, 40)
        self.setMinimumSize(200, 40)

        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed
        )

    def get(self):
        return tuple(i.value() for i in self.__Entries)

    def setMaximum(self, size: tuple):
        if len(size) < self.vec_size:
            raise Exception(f"Length of inputted value {size} less than {self.vec_size}. ({len(size)}<{self.vec_size})")
        for ind, i in enumerate(self.__Entries):
            i.setMaximum(size[ind])

    def setMinimum(self, size: tuple):
        if len(size) < self.vec_size:
            raise Exception(f"Length of inputted value {size} less than {self.vec_size}. ({len(size)}<{self.vec_size})")
        for ind, i in enumerate(self.__Entries):
            i.setMinimum(size[ind])

    def setValue(self, val: tuple):
        if len(val) < self.vec_size:
            raise Exception(f"Length of inputted value {val} less than {self.vec_size}. ({len(val)}<{self.vec_size})")
        for ind, i in enumerate(self.__Entries):
            i.setValue(val[ind])

    def setText(self, a0: str):
        self.__textLabel.setText(a0)

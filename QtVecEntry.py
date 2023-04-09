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

class Vec3Entry(QLabel):
    valueChanged = pyqtSignal()

    @pyqtSlot()
    def valueChangedSlot(status, source):
        pass

    def __init__(self):
        super().__init__()
        self.setStyleSheet(style+styleQl)
        self.lay = QHBoxLayout()
        self.setLayout(self.lay)

        self.__XEntry = QSpinBox()
        self.__YEntry = QSpinBox()
        self.__ZEntry = QSpinBox()
        self.__textLabel = QLabel("Vec3:")

        self.__XEntry.valueChanged.connect(self.valueChanged.emit)
        self.__YEntry.valueChanged.connect(self.valueChanged.emit)
        self.__ZEntry.valueChanged.connect(self.valueChanged.emit)

        self.lay.addWidget(self.__textLabel)
        self.lay.addWidget(self.__XEntry)
        self.lay.addWidget(self.__YEntry)
        self.lay.addWidget(self.__ZEntry)

        # self.setFixedSize(200, 40)
        self.setMinimumSize(200, 40)

        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed
        )

    def get(self):
        return self.__XEntry.value(), self.__YEntry.value(), self.__ZEntry.value()

    def setMaximum(self, size: tuple[int, int, int]):
        self.__XEntry.setMaximum(size[0])
        self.__YEntry.setMaximum(size[1])
        self.__ZEntry.setMaximum(size[2])

    def setMinimum(self, size: tuple[int, int, int]):
        self.__XEntry.setMinimum(size[0])
        self.__YEntry.setMinimum(size[1])
        self.__ZEntry.setMinimum(size[2])

    def setValue(self, val: tuple[int, int, int]):
        self.__XEntry.setValue(val[0])
        self.__YEntry.setValue(val[1])
        self.__ZEntry.setValue(val[2])

    def setText(self, a0: str):
        self.__textLabel.setText(a0)


class Vec4Entry(Vec3Entry):
    def __init__(self):
        super().__init__()
        self.__WEntry = QSpinBox()
        self.__WEntry.valueChanged.connect(self.valueChanged.emit)

        self.lay.addWidget(self.__WEntry)

        self.setText('Vec4: ')

    def get(self):
        return super(Vec4Entry, self).get() + (self.__WEntry.value())

    def setMaximum(self, size: tuple[int, int, int, int]):
        super(Vec4Entry, self).setMaximum(size)
        self.__WEntry.setMaximum(size[3])

    def setMinimum(self, size: tuple[int, int, int, int]):
        super(Vec4Entry, self).setMinimum(size)
        self.__WEntry.setMinimum(size[3])

    def setValue(self, val: tuple[int, int, int, int]):
        super(Vec4Entry, self).setValue(val)
        self.__WEntry.setValue(val[2])

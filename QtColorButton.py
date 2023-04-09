from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPushButton


class ColorButton(QPushButton):
    '''
    Custom QtWidget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    '''

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.setColor(self._default)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            c = QColor(self._color)
            c = (255 - c.red(), 255 - c.green(), 255 - c.blue())
            self.setStyleSheet('ColorButton{'+f"background-color: {self._color};color: {rgb_to_hex(c[0], c[1], c[2])};"+'}')
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        dlg = QtWidgets.QColorDialog(self)
        dlg.setStyleSheet("ColorButton{background-color: #ffffff;color: #000000;}")
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec():
            self.setColor(dlg.currentColor().name())

            c = QColor(self._color)
            c = (255 - c.red(), 255 - c.green(), 255 - c.blue())
            self.setStyleSheet('ColorButton{'+f"background-color: {self._color};color: {rgb_to_hex(c[0], c[1], c[2])};"+'}')

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)
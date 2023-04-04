import sys

from PIL.Image import Resampling
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QSpinBox,
    QHBoxLayout,
    QSizePolicy,
    QPushButton,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QCheckBox,
    QSlider
)

import main as PBB

style = '''
border-style: outset;
border-width: 1px;
border-radius: 10px;
border-color: gray;
'''


class Vec3Entry(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"QWidget {'{'}{style}{'}'}")
        lay = QHBoxLayout()
        self.setLayout(lay)

        self.XEntry = QSpinBox()
        self.YEntry = QSpinBox()
        self.ZEntry = QSpinBox()

        lay.addWidget(QLabel("Vec3:"))
        lay.addWidget(self.XEntry)
        lay.addWidget(self.YEntry)
        lay.addWidget(self.ZEntry)

        # self.setFixedSize(200, 40)
        self.setMinimumSize(200, 40)

        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Fixed
        )

    def get(self):
        return self.XEntry.value(), self.YEntry.value(), self.ZEntry.value()

    def setMaximum(self, size: tuple[int, int, int]):
        self.XEntry.setMaximum(size[0])
        self.YEntry.setMaximum(size[1])
        self.ZEntry.setMaximum(size[2])

    def setMinimum(self, size: tuple[int, int, int]):
        self.XEntry.setMinimum(size[0])
        self.YEntry.setMinimum(size[1])
        self.ZEntry.setMinimum(size[2])

    def setValue(self, val: tuple[int, int, int]):
        self.XEntry.setValue(val[0])
        self.YEntry.setValue(val[1])
        self.ZEntry.setValue(val[2])


class MainWindow(QMainWindow):
    def update_image(self):
        bim = self.blocksMatrix.render()
        bim_size = bim.size

        # bim.crop((bim_size[0], bim_size[1], bim_size[0], bim_size[1]))

        self.setMinimumSize(
            bim_size[0] * 2 + 50,
            bim_size[1] * 2 + 187 + 46 * 2
        )

        self.position_to_place.setMaximum(
            (self.blocksMatrix.maxx - 1, self.blocksMatrix.maxy - 1, self.blocksMatrix.maxz - 1))

        self.size_label.setText(
            f"Size: ({self.blocksMatrix.maxx}, {self.blocksMatrix.maxy}, {self.blocksMatrix.maxz})")

        self.axis_matrix = PBB.BlocksMatrix("", self.blocksMatrix.size)
        self.axis_matrix.place_id("selector", self.position_to_place.get())

        if self.show_cursor.isChecked():
            bim.alpha_composite(self.axis_matrix.render())

        bim = bim.resize((int(bim_size[0] * self.image_size_slider.value()),
                          int(bim_size[1] * self.image_size_slider.value())), Resampling.NEAREST)

        im = ImageQt(bim)
        self.rendered_image = QPixmap.fromImage(im)
        self.render_label.setMinimumSize(
            bim_size[0] * 2,
            bim_size[1] * 2
        )
        self.render_label.setPixmap(self.rendered_image)

    def place_block(self):
        self.blocksMatrix.place_id(self.id_selector.currentText(), self.position_to_place.get())

    def save_matrix(self):
        filename = QFileDialog.getSaveFileName(
            self,
            "Open .pbn File",
            "new pixel matrix",
            "All Files (*.*);; Pixel Block Files (*.pbn);; Portable Network Graphics (*.png)",
            "Pixel Block Files (*.pbn)"
        )[0]

        if filename == '':
            return
        if '.png' in filename:
            self.blocksMatrix.render().save(filename)
            return

        f = open(filename, "w")
        f.write(self.blocksMatrix.topbn())
        f.close()

    def open_matrix(self):
        filename = QFileDialog.getOpenFileName(
            self,
            "Open .pbn File",
            "",
            "All Files (*.*);; Pixel Block Files (*.pbn)",
            "Pixel Block Files (*.pbn)"
        )[0]
        self.open_matrix_by_path(filename)

    def open_matrix_by_path(self, path: str):
        if path == '':
            return

        self.blocksMatrix = PBB.BlocksMatrix(path)

    def new_matrix(self):
        marixDialog = CreateNewMatrixDialog()

        if marixDialog.exec():
            self.blocksMatrix = PBB.BlocksMatrix(size=marixDialog.vec.get())

    def __init__(self):
        super().__init__()

        self.rendered_image: QPixmap = QPixmap()
        self.setWindowTitle("Pixel Block Builder by NezertorcheaT")
        self.setWindowIcon(QIcon('icon.ico'))

        layout = QVBoxLayout()

        self.blocksMatrix = PBB.BlocksMatrix("", (5, 5, 5))
        self.blocksMatrix.place_id("pbb.box", (0, 0, 0))
        self.blocksMatrix.place_id("pbb.box", (1, 0, 0))
        self.blocksMatrix.place_id("pbb.box", (0, 1, 0))
        self.blocksMatrix.place_id("pbb.box", (0, 0, 1))

        self.axis_matrix = PBB.BlocksMatrix("", self.blocksMatrix.size)

        self.render_label = QLabel()
        self.render_label.setPixmap(self.rendered_image)
        # self.render_label.setStyleSheet("border: 2px solid black;")
        self.render_label.setStyleSheet(f"QLabel {'{'}{style}{'}'}")
        # self.render_label.setScaledContents(True)
        self.render_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_size_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.image_size_slider.setMinimum(1)
        self.image_size_slider.setMaximum(20)
        self.image_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.image_size_slider.setTickInterval(1)
        self.image_size_slider.setValue(4)
        self.image_size_slider.valueChanged.connect(self.update_image)

        self.id_selector = QComboBox()
        self.id_selector.addItems(PBB.idsHandler.all_ids_to_ui)
        self.id_selector.setStyleSheet(f"QWidget {'{'}{style}{'}'}")

        self.position_to_place = Vec3Entry()
        self.position_to_place.setMaximum(
            (self.blocksMatrix.maxx - 1, self.blocksMatrix.maxy - 1, self.blocksMatrix.maxz - 1))
        self.position_to_place.XEntry.valueChanged.connect(self.update_image)
        self.position_to_place.YEntry.valueChanged.connect(self.update_image)
        self.position_to_place.ZEntry.valueChanged.connect(self.update_image)

        self.place_button = QPushButton()
        self.place_button.setText("Place")
        self.place_button.clicked.connect(self.place_block)
        self.place_button.clicked.connect(self.update_image)

        self.update_button = QPushButton()
        self.update_button.setText("Update")
        self.update_button.clicked.connect(self.update_image)

        openSaveNewlayout = QHBoxLayout()

        self.save_button = QPushButton()
        self.save_button.setText("Open")
        self.save_button.clicked.connect(self.open_matrix)
        self.save_button.clicked.connect(self.update_image)

        self.open_button = QPushButton()
        self.open_button.setText("Save")
        self.open_button.clicked.connect(self.save_matrix)
        self.open_button.clicked.connect(self.update_image)

        self.new_button = QPushButton()
        self.new_button.setText("New")
        self.new_button.clicked.connect(self.new_matrix)
        self.new_button.clicked.connect(self.update_image)

        params_layout = QHBoxLayout()
        params_Widget = QWidget()
        params_Widget.setLayout(params_layout)
        params_Widget.setMaximumSize(1000000, 35)

        self.size_label = QLabel()
        self.size_label.setStyleSheet(f"qproperty-alignment: {int(Qt.AlignmentFlag.AlignLeft)};")
        self.size_label.setMaximumSize(1000000, 13)

        self.show_cursor = QCheckBox()
        self.show_cursor.setText("Show cursor")
        self.show_cursor.toggled.connect(self.update_image)

        openSaveNewWidget = QWidget()
        openSaveNewWidget.setLayout(openSaveNewlayout)
        openSaveNewWidget.setFixedSize(200, 40)
        openSaveNewlayout.addWidget(self.save_button)
        openSaveNewlayout.addWidget(self.open_button)
        openSaveNewlayout.addWidget(self.new_button)

        params_layout.addWidget(self.size_label)
        params_layout.addWidget(self.show_cursor)

        layout.addWidget(openSaveNewWidget)
        layout.addWidget(params_Widget)
        layout.addWidget(self.render_label)
        layout.addWidget(self.id_selector)
        layout.addWidget(self.place_button)
        layout.addWidget(self.image_size_slider)
        layout.addWidget(self.position_to_place)
        layout.addWidget(self.update_button)

        widget = QWidget()
        widget.setLayout(layout)

        if len(sys.argv) == 2 and '.pbn' in sys.argv[-1]:
            self.open_matrix_by_path(sys.argv[-1])

        self.update_image()

        self.setCentralWidget(widget)


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


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()

import sys

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPixmap, QIcon, QAction, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QComboBox,
    QFileDialog,
    QCheckBox,
    QSlider,
    QMessageBox, QToolBar
)

import main as PBB
from QtColorButton import *
from QtNewMatrixDialog import *


class MainWindow(QMainWindow):
    def update_image(self):
        self.bim = self.blocksMatrix.render(shadows=self.shadows.isChecked(), scale=self.pix_scale.value())
        bim_size = self.bim.size
        # self.data_layout_widget.setMaximumWidth(self.width()//4)

        # bim.crop((bim_size[0], bim_size[1], bim_size[0], bim_size[1]))
        # self.setMinimumSize(
        #    bim_size[0] * 2 + 50 + 26 + 20,
        #    bim_size[1] * 2 + 187 + 46 * 3 + 13
        # )

        self.position_to_place.setMaximum(
            (self.blocksMatrix.maxx - 1, self.blocksMatrix.maxy - 1, self.blocksMatrix.maxz - 1))

        self.size_label.setText(
            f"Size: ({self.blocksMatrix.maxx}, {self.blocksMatrix.maxy}, {self.blocksMatrix.maxz})")

        self.axis_matrix = PBB.BlocksMatrix("", self.blocksMatrix.size)
        self.axis_matrix.place_id("selector", self.position_to_place.get())

        if self.show_cursor.isChecked():
            self.bim.alpha_composite(self.axis_matrix.render(shadows=False, scale=self.pix_scale.value()))

        bim = self.bim.resize((int(bim_size[0] * self.image_size_slider.value()),
                          int(bim_size[1] * self.image_size_slider.value())), Image.NEAREST)

        self.render_painter=QPainter()

        im = ImageQt(bim)
        self.rendered_image = QPixmap.fromImage(im)
        # self.render_label.setMinimumSize(
        #    bim_size[0],
        #    bim_size[1]
        # )
        self.render_label.setPixmap(self.rendered_image)
        # self.render_label.setMaximumWidth(self.width()//4*3)
        self.setWindowTitle(f'{self.normalWindowTitle} - {self.path_to_saved}')

    def paintEvent(self, a0: QPaintEvent) -> None:
        p=QPainter()
        p.drawPixmap(QPoint(0,0),self.rendered_image.scaled(int(self.bim.size[0] * self.image_size_slider.value()),
                          int(self.bim.size[1] * self.image_size_slider.value())))


    def place_block(self):
        ID = self.id_selector.currentText()
        if self.rotation_size_slider.isEnabled():
            ID = PBB.Block.get_param_from_id(ID, 'variants')[self.rotation_size_slider.value()]

        t = (QColor(self.color_picker.color()).toRgb().red(),
             QColor(self.color_picker.color()).toRgb().green(),
             QColor(self.color_picker.color()).toRgb().blue(),
             255)
        self.blocksMatrix.place_id(ID, self.position_to_place.get(), t)

    def save_matrix_as(self):
        filename = QFileDialog.getSaveFileName(
            self,
            "Save .pbn File",
            "new pixel matrix",
            "All Files (*.*);; Pixel Block Files (*.pbn)",
            "Pixel Block Files (*.pbn)"
        )[0]

        if filename == '':
            return

        f = open(filename, "w")
        f.write(self.blocksMatrix.topbn())
        self.path_to_saved = filename
        f.close()

    def save_matrix(self):
        if self.path_to_saved != self.NEW:
            f = open(self.path_to_saved, "w")
            f.write(self.blocksMatrix.topbn())
            f.close()

    def export_as_png(self):
        filename = QFileDialog.getSaveFileName(
            self,
            "Export as .png",
            "render.png",
            "All Files (*.*);; Portable Network Graphics (*.png)",
            "Portable Network Graphics (*.png)"
        )[0]

        if '.png' in filename:
            self.update_image()
            self.rendered_image.save(filename)
            return

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
        self.path_to_saved = path

    def new_matrix(self):
        marixDialog = CreateNewMatrixDialog()
        marixDialog.setStyleSheet(style)

        if marixDialog.exec():
            self.blocksMatrix = PBB.BlocksMatrix(size=marixDialog.vec.get())
            self.path_to_saved = self.NEW

    def crop_matrix(self):
        marixDialog = CreateNewMatrixDialog('Crop Matrix')
        marixDialog.vec.setMaximum(self.blocksMatrix.size)
        marixDialog.setStyleSheet(style)

        if marixDialog.exec():
            self.blocksMatrix.crop(marixDialog.vec.get())

    def expand_matrix(self):
        marixDialog = CreateNewMatrixDialog('Expand Matrix')
        marixDialog.vec.setMinimum(self.blocksMatrix.size)
        marixDialog.setStyleSheet(style)

        if marixDialog.exec():
            self.blocksMatrix.expand(marixDialog.vec.get())

    def rotation_changed(self, s):
        if PBB.idsHandler.full[s].get("variants", None):
            self.rotation_size_slider.setEnabled(True)
        else:
            self.rotation_size_slider.setEnabled(False)

    def export_as_sequence(self):
        filename = str(QFileDialog.getExistingDirectory(self, "Select Render Directory", ))

        if filename == '':
            return

        try:
            self.blocksMatrix.render(True, filename, shadows=self.shadows.isChecked(), scale=self.pix_scale.value())
        except Exception as e:
            QMessageBox.critical(
                self,
                "Render Error!",
                f"Something went very wrong. This is Error message:\n{e}",
                buttons=QMessageBox.StandardButton.Ok
            )
            return
        QMessageBox.information(
            self,
            "Render is Done!",
            f"You render at folder:\n{filename}",
            buttons=QMessageBox.StandardButton.Ok
        )

    def rsssm(self):
        self.rotation_size_slider.setMaximum(len(PBB.Block.get_param_from_id(self.id_selector.currentText(),
                                                                             'variants') if PBB.Block.get_param_from_id(
            self.id_selector.currentText(),
            'variants') is not None else [0]) - 1 if self.rotation_size_slider.isEnabled() else 1)

    def __init__(self):
        super().__init__()

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        self.normalWindowTitle = "Pixel Block Builder by NezertorcheaT"
        self.NEW = 'New File'
        self.path_to_saved = self.NEW
        self.setWindowTitle(f'{self.normalWindowTitle} - {self.path_to_saved}')

        self.rendered_image: QPixmap = QPixmap()
        self.setWindowIcon(QIcon('icon.ico'))

        layout = QHBoxLayout()
        data_layout = QVBoxLayout()
        self.data_layout_widget = QWidget()
        self.data_layout_widget.setLayout(data_layout)
        self.data_layout_widget.setMaximumWidth(self.width() // 4)

        self.blocksMatrix = PBB.BlocksMatrix("", (5, 5, 5))
        self.blocksMatrix.place_id("pbb.box", (0, 0, 0))
        self.blocksMatrix.place_id("pbb.box", (1, 0, 0))
        self.blocksMatrix.place_id("pbb.box", (0, 1, 0))
        self.blocksMatrix.place_id("pbb.box", (0, 0, 1))

        self.axis_matrix = PBB.BlocksMatrix("", self.blocksMatrix.size)

        self.render_label = QLabel()
        self.render_label.setPixmap(self.rendered_image)
        # self.render_label.setStyleSheet("border: 2px solid black;")
        # self.render_label.setScaledContents(True)
        self.render_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.render_label.setStyleSheet('border-style: solid;border-width: 1px;border-radius: 10px;border-color: gray;')

        self.image_size_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.image_size_slider.setMinimum(1)
        self.image_size_slider.setMaximum(20)
        self.image_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.image_size_slider.setTickInterval(1)
        self.image_size_slider.setValue(4)
        self.image_size_slider.valueChanged.connect(self.update_image)

        self.id_selector = QComboBox()
        self.id_selector.addItems(PBB.idsHandler.all_ids_to_ui)
        self.id_selector.currentTextChanged.connect(self.rotation_changed)
        self.id_selector.currentTextChanged.connect(self.rsssm)
        self.id_selector.currentTextChanged.connect(lambda: rotation_label.setText(
            f'Variant: {(j if (j := PBB.Block.get_param_from_id(self.id_selector.currentText(), "variants")) and j is not None else ["null"])[self.rotation_size_slider.value() if j is not None else 0]}'))

        self.position_to_place = VecEntry(3)
        self.position_to_place.setMaximum(
            (self.blocksMatrix.maxx - 1, self.blocksMatrix.maxy - 1, self.blocksMatrix.maxz - 1))
        self.position_to_place.valueChanged.connect(self.update_image)

        '''
        self.place_button = QPushButton()
        self.place_button.setText("Place")
        self.place_button.clicked.connect(self.place_block)
        self.place_button.clicked.connect(self.update_image)
        '''
        self.place_button_action = QAction("Place", self)
        self.place_button_action.setStatusTip("This is your button")
        self.place_button_action.triggered.connect(self.place_block)
        self.place_button_action.triggered.connect(self.update_image)

        '''
        self.update_button = QPushButton()
        self.update_button.setText("Update")
        self.update_button.clicked.connect(self.update_image)
        '''
        self.update_button_action = QAction("Update", self)
        self.update_button_action.setStatusTip("This is your button")
        self.update_button_action.triggered.connect(self.update_image)

        openSaveNewlayout = QHBoxLayout()
        '''
        self.open_button = QPushButton()
        self.open_button.setText("Open")
        self.open_button.clicked.connect(self.open_matrix)
        self.open_button.clicked.connect(self.update_image)
        '''
        self.open_button_action = QAction("Open File", self)
        self.open_button_action.triggered.connect(self.open_matrix)
        self.open_button_action.triggered.connect(self.update_image)

        '''
        self.save_button = QPushButton()
        self.save_button.setText("Save")
        self.save_button.clicked.connect(self.save_matrix_as)
        self.save_button.clicked.connect(self.update_image)
        '''
        self.save_as_button_action = QAction("Save as", self)
        self.save_as_button_action.triggered.connect(self.save_matrix_as)
        self.save_as_button_action.triggered.connect(self.update_image)
        self.save_button_action = QAction("Save", self)
        self.save_button_action.triggered.connect(self.save_matrix)
        self.save_button_action.triggered.connect(self.update_image)

        '''
        self.new_button = QPushButton()
        self.new_button.setText("New")
        self.new_button.clicked.connect(self.new_matrix)
        self.new_button.clicked.connect(self.update_image)
        '''
        self.new_button_action = QAction("New File", self)
        self.new_button_action.triggered.connect(self.new_matrix)
        self.new_button_action.triggered.connect(self.update_image)

        '''
        self.render_button = QPushButton()
        self.render_button.setText("Render")
        self.render_button.clicked.connect(self.export_as_sequence)
        self.render_button.clicked.connect(self.update_image)
        '''
        self.render_button_action = QAction("Image Sequence", self)
        self.render_button_action.triggered.connect(self.export_as_sequence)
        self.render_button_action.triggered.connect(self.update_image)

        self.export_as_png_action = QAction(".png", self)
        self.export_as_png_action.triggered.connect(self.update_image)
        self.export_as_png_action.triggered.connect(self.export_as_png)

        self.size_label = QLabel()
        self.size_label.setStyleSheet(
            f"border-style: outset;border-width: 1px;border-radius: 10px;border-color: gray;qproperty-alignment: {int(Qt.AlignmentFlag.AlignCenter)};")

        self.show_cursor = QCheckBox()
        self.show_cursor.setText("Show cursor")
        self.show_cursor.toggled.connect(self.update_image)

        self.shadows = QCheckBox()
        self.shadows.setText("Shadows")
        self.shadows.toggled.connect(self.update_image)

        rotation_label = QLabel()
        rotation_label.setText('Variant: null')

        zoom_label = QLabel()
        zoom_label.setText('Zoom')

        self.rotation_size_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.rotation_size_slider.setMinimum(0)
        self.rsssm()
        self.rotation_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rotation_size_slider.setTickInterval(1)
        self.rotation_size_slider.setValue(1)
        self.rotation_size_slider.valueChanged.connect(lambda: rotation_label.setText(
            f'Variant: {(j if (j := PBB.Block.get_param_from_id(self.id_selector.currentText(), "variants")) and j is not None else ["null"])[self.rotation_size_slider.value() if j is not None else 0]}'))

        self.color_picker = ColorButton()
        self.color_picker.setText("Color")
        self.color_picker.setColor('#ffffff')

        self.pix_scale = QSpinBox()
        self.pix_scale.setMinimum(16)
        self.pix_scale.valueChanged.connect(self.update_image)

        layout.addWidget(self.render_label)
        layout.addWidget(self.data_layout_widget)
        data_layout.addWidget(self.id_selector)
        # layout.addWidget(self.place_button)
        data_layout.addWidget(zoom_label)
        data_layout.addWidget(self.image_size_slider)
        data_layout.addWidget(rotation_label)
        data_layout.addWidget(self.rotation_size_slider)
        data_layout.addWidget(self.position_to_place)
        # layout.addWidget(self.update_button)
        # layout.addWidget(self.color_picker)
        data_layout.addWidget(self.pix_scale)

        toolbar.addAction(self.place_button_action)
        toolbar.addAction(self.update_button_action)
        toolbar.addWidget(self.color_picker)
        toolbar.addSeparator()
        toolbar.addWidget(self.show_cursor)
        toolbar.addWidget(self.shadows)
        toolbar.addSeparator()
        toolbar.addWidget(self.size_label)

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        file_menu.addAction(self.new_button_action)
        file_menu.addAction(self.save_button_action)
        file_menu.addAction(self.save_as_button_action)
        file_menu.addAction(self.open_button_action)

        file_submenu = file_menu.addMenu("Export")
        file_submenu.addAction(self.render_button_action)
        file_submenu.addAction(self.export_as_png_action)

        edit_menu = menu.addMenu("Edit")

        rotX_action = QAction("Rotate X", self)
        rotX_action.triggered.connect(
            lambda: self.blocksMatrix.rotate_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.X_rotation))
        rotX_action.triggered.connect(self.update_image)
        edit_menu.addAction(rotX_action)

        rotY_action = QAction("Rotate Y", self)
        rotY_action.triggered.connect(
            lambda: self.blocksMatrix.rotate_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.Y_rotation))
        rotY_action.triggered.connect(self.update_image)
        edit_menu.addAction(rotY_action)

        rotZ_action = QAction("Rotate Z", self)
        rotZ_action.triggered.connect(
            lambda: self.blocksMatrix.rotate_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.Z_rotation))
        rotZ_action.triggered.connect(self.update_image)
        edit_menu.addAction(rotZ_action)

        edit_menu.addSeparator()

        FlipX_action = QAction("Flip X", self)
        FlipX_action.triggered.connect(
            lambda: self.blocksMatrix.flip_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.X_flip))
        FlipX_action.triggered.connect(self.update_image)
        edit_menu.addAction(FlipX_action)

        FlipY_action = QAction("Flip Y", self)
        FlipY_action.triggered.connect(
            lambda: self.blocksMatrix.flip_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.Y_flip))
        FlipY_action.triggered.connect(self.update_image)
        edit_menu.addAction(FlipY_action)

        FlipZ_action = QAction("Flip Z", self)
        FlipZ_action.triggered.connect(
            lambda: self.blocksMatrix.flip_by_ManipulationAxis(PBB.BlocksMatrix.ManipulationAxis.Z_flip))
        FlipZ_action.triggered.connect(self.update_image)
        edit_menu.addAction(FlipZ_action)

        edit_menu.addSeparator()

        Crop_action = QAction("Crop", self)
        Crop_action.triggered.connect(self.crop_matrix)
        Crop_action.triggered.connect(self.update_image)
        edit_menu.addAction(Crop_action)

        Expand_action = QAction("Expand", self)
        Expand_action.triggered.connect(self.expand_matrix)
        Expand_action.triggered.connect(self.update_image)
        # edit_menu.addAction(Expand_action)

        widget = QWidget()
        widget.setLayout(layout)

        if len(sys.argv) == 2 and '.pbn' in sys.argv[-1]:
            self.open_matrix_by_path(sys.argv[-1])

        self.rotation_changed('null')
        self.update_image()

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    app.exec()

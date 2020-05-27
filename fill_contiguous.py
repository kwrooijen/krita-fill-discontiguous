from PyQt5.QtCore import pyqtSlot, Qt, QVariant, QByteArray
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog
from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase
import sys

DOCKER_NAME = 'Fill Contiguous'
DOCKER_ID = 'pykrita_fill_contiguous'

instance = Krita.instance()

def get_foreground_color():
    active_view = instance.activeWindow().activeView()
    canvas = active_view.canvas()
    return q_color_to_q_byte_array(active_view.foregroundColor().colorForCanvas(canvas))

def q_color_to_q_byte_array(color):
    name = color.name()[1:]
    color_bytes = [bytes.fromhex(name[i:i+2]) for i in range(0, len(name), 2)]
    new_color = QByteArray()
    new_color.insert(0, color_bytes[2]) # Blue
    new_color.insert(1, color_bytes[1]) # Green
    new_color.insert(2, color_bytes[0]) # Red
    new_color.insert(3, b'\xff')        # Alpha
    return new_color

def replace_color_in_node(node, from_color, to_color):
    n_x = node.bounds().x()
    n_y = node.bounds().y()
    n_width = node.bounds().width()
    n_height = node.bounds().height()
    for x in range(n_x, n_x + n_width):
        for y in range(n_y, n_y + n_height):
            if node.pixelData(x, y, 1, 1) == from_color:
                node.setPixelData(to_color, x, y, 1, 1)

def color_picker_button(self):
    button = QPushButton('Open color dialog', self)
    button.setToolTip('Opens color dialog')
    button.move(10,30)
    button.clicked.connect(self.on_click)

class Fill_contiguous(DockWidget):
    def __init__(self):
        super().__init__()
        color_picker_button(self)
        self.setWindowTitle(DOCKER_NAME)

    def canvasChanged(self, canvas):
        pass

    @pyqtSlot()
    def on_click(self):
        color = QColorDialog.getColor()
        if color.isValid():
            document = instance.activeDocument()
            active_node = document.activeNode()
            from_color = get_foreground_color()
            to_color = q_color_to_q_byte_array(color)
            replace_color_in_node(active_node, from_color, to_color)
            document.refreshProjection()

dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        Fill_contiguous)

instance.addDockWidgetFactory(dock_widget_factory)

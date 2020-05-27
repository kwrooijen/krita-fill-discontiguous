from PyQt5.QtCore import pyqtSlot, Qt, QVariant, QByteArray
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QCheckBox
from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase
import sys

DOCKER_NAME = 'Fill Contiguous'
DOCKER_ID = 'pykrita_fill_contiguous'

instance = Krita.instance()

def push_node(collection, node):
    collection.append(node)
    for child in node.childNodes():
        push_node(collection, child)

def get_nodes():
    active_view = instance.activeWindow().activeView()
    collection = []
    for node in active_view.selectedNodes():
        push_node(collection, node)
    return collection

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
    button = QPushButton('Replace foreground', self)
    button.setToolTip('Replace the forground color with a new color')
    button.resize(170,32)
    button.move(20,30)
    button.clicked.connect(self.on_click)

def undo_button(self):
    button = QPushButton('Undo', self)
    button.setToolTip('Undo the last color replacement')
    button.resize(170,32)
    button.move(20,80)
    button.clicked.connect(self.on_click_undo)

class Fill_contiguous(DockWidget):
    def __init__(self):
        super().__init__()
        self.undo_tree = {}
        self.iteration = 0
        color_picker_button(self)
        undo_button(self)
        self.setWindowTitle(DOCKER_NAME)

    def canvasChanged(self, canvas):
        pass

    @pyqtSlot()
    def on_click_undo(self):
        if self.iteration > 0:
            self.iteration = self.iteration - 1
            nodes = self.undo_tree[self.iteration]["nodes"]
            from_color = self.undo_tree[self.iteration]["from_color"]
            to_color = self.undo_tree[self.iteration]["to_color"]
            for node in nodes:
                replace_color_in_node(node, to_color, from_color)
            instance.activeDocument().refreshProjection()

    @pyqtSlot()
    def on_click(self):
        color = QColorDialog.getColor()
        if color.isValid():
            from_color = get_foreground_color()
            to_color = q_color_to_q_byte_array(color)
            active_view = instance.activeWindow().activeView()
            self.undo_tree[self.iteration] = {
                "from_color": from_color,
                "to_color": to_color,
                "nodes": get_nodes()
            }
            self.iteration = self.iteration + 1
            for node in get_nodes():
                replace_color_in_node(node, from_color, to_color)
            instance.activeDocument().refreshProjection()

dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        Fill_contiguous)

instance.addDockWidgetFactory(dock_widget_factory)

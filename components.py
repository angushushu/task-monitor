import typing
from PySide6 import QtCore
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
from PySide6.QtWidgets import QWidget

class taskRecorder(QWidget):
    def __init__(self, steps):
        super().__init__()
        hlay = QHBoxLayout(self)
        hlay.setContentsMargins(0,0,0,0)
        hlay.setSpacing(0)
        self.label = QLabel("__")
        self.label.setFixedWidth(100)
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setStyleSheet("""
            QProgressBar { border: 0px solid grey; border-radius: 0px; text-align: center; }
            QProgressBar:hover { background-color: #e3e3e3; }
            QProgressBar::chunk {background-color: #b5b5b5; width: 1px;}
            QProgressBar::chunk:hover {background-color: #8a8a8a; width: 1px;}
        """)
        # for timing
        self.steps = steps
        self.step = 0
        self.recording = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.duration = QLabel("0")
        self.duration.setFixedWidth(50)

        self.btn = QPushButton("run")
        hlay.addWidget(self.label)
        hlay.addWidget(self.progress)
        hlay.addWidget(self.duration)
        hlay.addWidget(self.btn)
        self.setLayout(hlay)
    def set_step(self, step):
        self.step = step
        self.duration.setText(str(self.step))
    def set_name(self, name):
        self.label.setText(name)
    def update_time(self):
        self.step += 1
        self.duration.setText(str(self.step))

class CheckableComboBox(QComboBox):
    popupAboutToBeShown = QtCore.Signal()
    
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = QApplication.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)
        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())
        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)
        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False
        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)
    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)
    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False
        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False
    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True
    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()
    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False
    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)
        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)
    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)
    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)
    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res
    
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(QtCore.Qt.UserRole+1000)
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = "{}%".format(progress)
        opt.textVisible = True
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
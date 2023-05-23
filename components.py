from PySide6 import QtCore
import PySide6.QtGui
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from apscheduler.schedulers.qt import QtScheduler
from datetime import timedelta
from PySide6.QtWidgets import QWidget

class taskRecorder(QWidget):
    renameTask = QtCore.Signal()
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        hlay = QHBoxLayout(self)
        hlay.setContentsMargins(0,0,0,0)
        hlay.setSpacing(0)
        self.label = QLabel("__")
        self.label.setFixedWidth(100)
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        # print(self.metaObject().className())
        # self.setProperty("class", "recorder")
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 0px solid grey;
                border-radius: 0px;
                text-align: center;
                background-color: transparent;
                padding: 0 10px;
            }
            QProgressBar::chunk {background-color: #63cf80; width: 1px;}
            QProgressBar::chunk:hover { background-color: #6ee68e; }
        """)

        # for timing
        self.step = 0
        self.recording = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.duration = QLabel("0")
        self.duration.setFixedWidth(50)

        self.btn = QPushButton("run")
        self.btn.setFlat(True)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color:transparent;
                width:40px;
                border:0px solid rgba(0,0,0,0.2);
                border-radius:2px;
                padding:0 5px;
            }
            QPushButton:pressed {
                border:0px solid rgba(0,0,0,0.5)
            }
            QPushButton:hover {
                background-color:rgba(0,0,0,0.1);
            }
        """)
        hlay.addWidget(self.label)
        hlay.addWidget(self.progress)
        hlay.addWidget(self.duration)
        hlay.addWidget(self.btn)
        self.setLayout(hlay)

        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.contextMenuEvent)
    def get_step(self):
        return self.step
    def set_step(self, step):
        self.step = step
        m, s = divmod(self.step, 60)
        h, m = divmod(m, 60)
        self.duration.setText(f'{h:02d}:{m:02d}:{s:02d}')
    def get_name(self):
        return self.label.text()
    def set_name(self, name):
        print('name',name)
        self.label.setText(name)
    def update_time(self):
        self.step += 1
        m, s = divmod(self.step, 60)
        h, m = divmod(m, 60)
        self.duration.setText(f'{h:02d}:{m:02d}:{s:02d}')
    def contextMenuEvent(self, event):
        print('menu')
        self.menu = QMenu(self)
        action1 = self.menu.addAction('Rename')
        action1.triggered.connect(self.renameTask.emit)
        self.menu.exec(event.globalPos())
        # return super().contextMenuEvent(event)

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
        # menu for clean or select all
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
    def showMenu(self, pos):
        print('showmenu')
        # self.hidePopup()
        menu = QMenu()
        clear = menu.addAction("Clear", self.clearSelection)
        all = menu.addAction("All", self.selectAll)
        action = menu.exec(self.mapToGlobal(pos))
    def clearSelection(self):
        print('clear')
        for i in range(self.model().rowCount()):
            self.model().item(i).setCheckState(Qt.Unchecked)
    def selectAll(self):
        print('all')
        self.popupAboutToBeShown.emit() # to load the tasks for the first time
        cnt = self.model().rowCount()
        for i in range(cnt):
            self.model().item(i).setCheckState(Qt.Checked)
    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)
    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                # if self.closeOnLineEditClick:
                if self.closeOnLineEditClick or event.button() == Qt.RightButton:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False
        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.RightButton: # added for menu
                    self.showMenu(event.pos())
                    return True
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
        # progress = .3
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = format(progress, '.2f')
        opt.textVisible = True
        opt.textAlignment = QtCore.Qt.AlignCenter
        # opt.palette.setBrush(QPalette.Disabled, QPalette.Base, QBrush(Qt.red))
        # QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
        # QApplication.style().drawControl(QStyle.CE_ProgressBarContents, opt, painter)
        if (progress > 0):
            progBarWidth = float((option.rect.width() * progress) / 100)
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setBrush(QColor(99,207,128,200)) #grigio molto scuro
            painter.setPen(QColor("transparent"))
            rect2=QtCore.QRect(option.rect.x(), option.rect.y(), progBarWidth,
                        option.rect.height())
            painter.drawRect(rect2)
            painter.setPen(QColor(QtCore.Qt.white))
            painter.restore()
        QApplication.style().drawControl(QStyle.CE_ProgressBarLabel, opt, painter)

class Scheduler(QtCore.QObject):
    dateChanges = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.id = 'sched'
        self.sched = QtScheduler()
    
    def start(self, hour, minute):
        self.sched.add_job(self.date_changes, 'cron', hour=hour, minute=minute)
        self.sched.start()
    
    def date_changes(self):
        self.dateChanges.emit()
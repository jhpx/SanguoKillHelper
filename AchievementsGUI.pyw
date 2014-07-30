# -*- coding: utf8 -*-
# AchievementsGUI.pyw
# Author: Jiangmf
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys


class AchievementsGUI(QMainWindow):

    def __init__(self, parent=None):
        super(AchievementsGUI, self).__init__(parent)

        QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

        self.setWindowTitle(self.tr("SanguoKillHelper"))

        self.initMenu()
        self._charaSelectTable = self.createTable()
        self._mainDisplay = self.createDisplay()

        self.setCentralWidget(self._charaSelectTable)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._mainDisplay)

    def initMenu(self):
        achievementsMenu = self.menuBar().addMenu(self.tr("成就"))

        about = QAction(self.tr("相关成就"), self)
        self.connect(about, SIGNAL("triggered()"), self, SLOT(""))
        achievementsMenu.addAction(about)

        get = QAction(self.tr("获得方法"), self)
        self.connect(get, SIGNAL("triggered()"), self, SLOT(""))
        achievementsMenu.addAction(get)

        use = QAction(self.tr("使用武将"), self)
        self.connect(use, SIGNAL("triggered()"), self, SLOT(""))
        achievementsMenu.addAction(use)

        draw = QAction(self.tr("生成成就关系图"), self)
        self.connect(draw, SIGNAL("triggered()"), self, SLOT(""))
        achievementsMenu.addAction(draw)

        adviceMenu = self.menuBar().addMenu(self.tr("推荐"))
        shouldBuy = QAction(self.tr("推荐购买武将"), self)
        self.connect(shouldBuy, SIGNAL("triggered()"), self, SLOT(""))
        adviceMenu.addAction(shouldBuy)

        shouldUse = QAction(self.tr("推荐使用武将"), self)
        self.connect(shouldUse, SIGNAL("triggered()"), self, SLOT(""))
        adviceMenu.addAction(shouldUse)

    def createTable(self):
        # 主窗口，用于展示与选择武将
        te = QTextEdit(self.tr("主窗口"))
        te.setAlignment(Qt.AlignCenter)
        return te

    def createDisplay(self):
        # 停靠窗口，用于显示成就与推荐武将
        dock3 = QDockWidget(self.tr("结果"), self)
        dock3.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        te3 = QTextEdit()
        te3.setReadOnly(True)
        dock3.setWidget(te3)
        return dock3

    def update(self, text):
        pass

app = QApplication(sys.argv)
main = AchievementsGUI()
main.show()
app.exec_()

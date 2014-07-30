# -*- coding: utf8 -*-
# AchievementsGUI.pyw
# Author: Jiangmf
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from Characters import Characters, Character, NonCharacter
from Achievements import Achievements

class AchievementsGUI(QMainWindow):

    def __init__(self, parent=None):
        super(AchievementsGUI, self).__init__(parent)
        # 中文hook
        QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))
        
        # 载入武将
        self._characters = Characters()
        
        # 载入界面控件
        self.initMenu()
        self._charaSelectTable = self.createTable()
        dock = self.createDisplayDock()
        self._mainDisplay = dock.widget()

        # 调整界面控件
        self.setWindowTitle(self.tr("SanguoKillHelper"))
        self.setCentralWidget(self._charaSelectTable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.resize(800, 600)
        
    def initMenu(self):
        """初始化菜单栏"""
        achievementsMenu = self.menuBar().addMenu(self.tr("成就"))

        about = QAction(self.tr("相关成就"), self)
        self.connect(about, SIGNAL("triggered()"), self.updateAchievementsAbout)
        achievementsMenu.addAction(about)

        how = QAction(self.tr("获得方法"), self)
        self.connect(how, SIGNAL("triggered()"), self.updateAchievementsHow)
        achievementsMenu.addAction(how)

        use = QAction(self.tr("使用武将"), self)
        self.connect(use, SIGNAL("triggered()"), self.updateAchievementsUse)
        achievementsMenu.addAction(use)

        draw = QAction(self.tr("生成成就关系图"), self)
        self.connect(draw, SIGNAL("triggered()"), self.updateAchievementsUse)
        achievementsMenu.addAction(draw)

        adviceMenu = self.menuBar().addMenu(self.tr("推荐"))
        shouldBuy = QAction(self.tr("推荐购买武将"), self)
        self.connect(shouldBuy, SIGNAL("triggered()"), self, SLOT(""))
        adviceMenu.addAction(shouldBuy)

        shouldUse = QAction(self.tr("推荐使用武将"), self)
        self.connect(shouldUse, SIGNAL("triggered()"), self, SLOT(""))
        adviceMenu.addAction(shouldUse)

    def createCell(self, content):
        """给定一个武将，创建一个带颜色的Cell"""
        if (isinstance(content,  Character)):
            return QTableWidgetItem(self.tr(content.name))
        else:
            return QTableWidgetItem(self.tr(content))
    
    def createTable(self):
        """创建主窗口，用于展示与选择武将"""
        # 仅为缩短代码
        PACK_ORD = Character.PACK_ORD
        # 卡包数为最大列数
        column = len(PACK_ORD)
        # 各卡包里武将数的最大值为最大行数
        row = 8
        
        for pack in PACK_ORD.keys():
            c = self._characters.filter(lambda x: x.pack == pack).get_character_names()
            row = len(c) > row and len(c) or row
            
        # 按所计算行列数创建表格
        tw = QTableWidget(row, column)
        
        # 列头使用卡包名
        for pack in PACK_ORD.keys():
            tw.setHorizontalHeaderItem(int(PACK_ORD[pack]),self.createCell(pack))
            
        # 内容使用武将名按卡包填充
        for pack in PACK_ORD.keys():
            i = 0
            for x in self._characters.filter(lambda x: x.pack == pack).get_character_names():
                tw.setItem(i, int(PACK_ORD[pack]), self.createCell(x))
                i += 1
        tw.resizeColumnsToContents()
        
        #注册信号关联
        return tw

    def createDisplayDock(self):
        """创建停靠窗口，用于显示成就与推荐武将"""
        dock = QDockWidget(self.tr("结果"), self)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        te3 = QTextEdit()
        te3.setReadOnly(True)
        te3.setMinimumHeight(150)
        dock.setWidget(te3)
        return dock
        
    def updateAchievementsAbout(self):   
       """显示所选武将相关所有成就"""
       achievements = Achievements(self._characters)
       text = "\n".join([str(x) for x in achievements])
       self._mainDisplay.setText(self.tr(text))
       pass
       
    def updateAchievementsHow(self):
       """显示所选武将的获得方法"""
       achievements = Achievements(self._characters).filter(
            lambda x: x.reward_node.cost == '已获得')
       text = "\n".join([str(x) for x in achievements])
       self._mainDisplay.setText(self.tr(text))
       pass
       
    def updateAchievementsUse(self):   
       """显示使用所选武将所对应的成就"""
       achievements = Achievements(self._characters).filter(
            lambda x: x.condition_node.cost == '已获得')
       text = "\n".join([str(x) for x in achievements])
       self._mainDisplay.setText(self.tr(text))
       pass

app = QApplication(sys.argv)
main = AchievementsGUI()
main.show()
app.exec_()

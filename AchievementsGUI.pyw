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

        # 载入武将与卡包
        self._characters = Characters()
        self._packs  = [0] * len(Character.PACK_ORD.keys())
        for p in Character.PACK_ORD.keys():
             self._packs[int(Character.PACK_ORD[p])] = p
        
        # 缓存所有已获得武将
#        self._owncharacters = 
        
  
        
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
        selectMenu = self.menuBar().addMenu(self.tr("选择"))
        
        own = QAction(self.tr("选中已获得武将"), self)
        self.connect(own, SIGNAL("triggered()"), self.selectOwn)
        selectMenu.addAction(own)
        
        cancel = QAction(self.tr("取消所有选中"), self)
        self.connect(cancel, SIGNAL("triggered()"), self.selectCancel)
        selectMenu.addAction(cancel)
        
        achievementsMenu = self.menuBar().addMenu(self.tr("成就"))

        about = QAction(self.tr("相关成就"), self)
        self.connect(
            about, SIGNAL("triggered()"), self.updateAchievementsAbout)
        achievementsMenu.addAction(about)

        how = QAction(self.tr("获得方法"), self)
        self.connect(how, SIGNAL("triggered()"), self.updateAchievementsHow)
        achievementsMenu.addAction(how)

        use = QAction(self.tr("使用武将"), self)
        self.connect(use, SIGNAL("triggered()"), self.updateAchievementsUse)
        achievementsMenu.addAction(use)

        draw = QAction(self.tr("生成成就关系图"), self)
        self.connect(draw, SIGNAL("triggered()"), self, SLOT(""))
        achievementsMenu.addAction(draw)

        adviceMenu = self.menuBar().addMenu(self.tr("推荐"))
        
        buy = QAction(self.tr("购买选中武将"), self)
        self.connect(buy, SIGNAL("triggered()"), self.buyCharacters)
        adviceMenu.addAction(buy)

        shouldBuy = QAction(self.tr("推荐购买武将"), self)
        self.connect(shouldBuy, SIGNAL("triggered()"), self.showShouldBuy)
        adviceMenu.addAction(shouldBuy)

        shouldUse = QAction(self.tr("推荐使用武将"), self)
        self.connect(shouldUse, SIGNAL("triggered()"), self.showShouldUse)
        adviceMenu.addAction(shouldUse)
        
    def createCell(self, character):
        """给定一个武将，创建一个带颜色的Cell"""
        item = QTableWidgetItem(self.tr(character.name))
        if (character.cost == '已获得'):
            item.setTextColor(QColor(character.color))
        else:
            item.setTextColor(QColor("grey"))
        return item

    def createTable(self):
        """创建主窗口，用于展示与选择武将"""
        # 卡包数为最大列数
        column = len(self._packs)
        # 各卡包里武将数的最大值为最大行数
        row = 8
    
        for pack in self._packs:
            c = self._characters.filter(
                lambda x: x.pack == pack).get_character_names()
            row = len(c) > row and len(c) or row

        # 按所计算行列数创建表格
        tw = QTableWidget(row, column)

        # 列头使用卡包名
        for j in range(column):
            tw.setHorizontalHeaderItem(
                j, QTableWidgetItem(self.tr(self._packs[j])))

        # 内容使用武将名按卡包填充
        for j in range(column):
            i = 0
            pack = self._packs[j]
            for c in self._characters.filter(lambda x: x.pack == pack):
                tw.setItem(i, j, self.createCell(c))
                i += 1

        tw.verticalHeader().setVisible(False)
        tw.setEditTriggers(QTableWidget.NoEditTriggers)
        tw.setSelectionMode(QTableWidget.MultiSelection)
        tw.resizeColumnsToContents()

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

    def selectOwn(self):
        """选中所有已获得武将"""
        tw = self._charaSelectTable
        for j in range(len(self._packs)):
            i = 0
            pack = self._packs[j]
            for c in self._characters.filter(lambda x: x.pack == pack):
                if(c.cost == '已获得'):
                    tw.selectionModel().select(
                        tw.model().index(i, j), QItemSelectionModel.Select)
                        
                i += 1

    def selectCancel(self):
        """取消全部武将选中"""
        self._charaSelectTable.selectionModel().clearSelection()
        pass

    def selectedCharacterItems(self):
        """获得所有选中的武将格"""
        items = []
        for idx in self._charaSelectTable.selectedIndexes():
            item = self._charaSelectTable.item(idx.row(), idx.column())
            if item:
                items.append(item)
        return items
        
    def selectedCharacterNames(self):
        """获得所有选中的武将名"""
        names = []
        for idx in self._charaSelectTable.selectedIndexes():
            item = self._charaSelectTable.item(idx.row(), idx.column())
            if item:
                names.append(unicode(item.text()).encode('utf8'))
        return names

    def updateAchievementsAbout(self):
        """显示所选武将相关所有成就"""
        selected = self.selectedCharacterNames()
        
        achievements = Achievements(self._characters).filter(
            lambda x: x.condition_node.name in selected
            or x.reward_node.name in selected
        )
        text = "\n".join([str(x) for x in achievements])
        self._mainDisplay.setText(self.tr(text))
        pass

    def updateAchievementsHow(self):
        """显示所选武将的获得方法"""
        selected = self.selectedCharacterNames()
        achievements = Achievements(self._characters).filter(
            lambda x: x.reward_node.name in selected)
        achievements.sort('cost')
        text = "\n".join([str(x) for x in achievements])
        self._mainDisplay.setText(self.tr(text))
        pass

    def updateAchievementsUse(self):
        """显示使用所选武将所对应的成就"""
        selected = self.selectedCharacterNames()
        achievements = Achievements(self._characters).filter(
            lambda x: x.condition_node.name in selected)
        text = "\n".join([str(x) for x in achievements])
        self._mainDisplay.setText(self.tr(text))
        pass

    def buyCharacters(self):
        """购买选中武将"""
        selected = self.selectedCharacterNames()
        self._characters.buy_characters(selected)
        for item in self.selectedCharacterItems():
            character = self._characters[unicode(item.text()).encode('utf8')]
            item.setTextColor(QColor(character.color))
        self.selectCancel()
        
    def showShouldBuy(self):
        """显示推荐购买武将"""
        achievements = Achievements(self._characters)
        text = "\n".join(achievements.characters_should_buy())
        self._mainDisplay.setText(self.tr(text))
        return 
        
    def showShouldUse(self):
        """显示推荐使用武将"""
        achievements = Achievements(self._characters)
        text = "\n".join(achievements.characters_should_use())
        self._mainDisplay.setText(self.tr(text))
        return
        
app = QApplication(sys.argv)
main = AchievementsGUI()
main.show()
app.exec_()

# -*- coding: utf8 -*-
# Characters.py
# Author: Jiangmf
# Date: 2014-07-08
import abc
import re
import os
import csv
import copy
import time


class Node(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def name(self):
        """节点名"""

    @abc.abstractproperty
    def color(self):
        """节点颜色"""

    @abc.abstractproperty
    def style(self):
        """节点风格"""

    @abc.abstractproperty
    def cost(self):
        """价值"""

    @abc.abstractmethod
    def cmp_cost(self, other):
        """按价值的比较函数"""
pass


class NonCharacter(Node):

    """非武将类：只包含名称、颜色、风格、价值"""

    def __init__(self, name):
        self._name = name
        m = re.search(r'\d+', name)
        if m:
            self._cost = int(m.group())
        else:
            self._cost = 10000

    @property
    def name(self):
        """返回非武将的字符串名"""
        return self._name

    @property
    def color(self):
        """节点颜色"""
        return 'grey'

    @property
    def style(self):
        """返回''"""
        return ''

    @property
    def cost(self):
        """返回不可购买"""
        return'不可购买' if self._cost > 1000 else str(self._cost) + '金币'

    def cmp_cost(self, other):
        """按价值的比较函数"""
        return -other.__cmp_cost_NonCharacter__(self)

    def __cmp_cost_NonCharacter__(x, y):
        """按价值比较非武将与非武将"""
        return cmp(x._cost, y._cost) or cmp(x._name, y._name)

    def __cmp_cost_Character__(x, y):
        """按价值比较非武将与武将"""
        return cmp(x._cost, y._cost.imag) or cmp(len(x._name), len(y._name))

pass


class Character(Node):

    """武将类：包含武将名、国别、卡包、价值、颜色、风格"""
    COUNTRY_ORD = {'蜀': 0, '魏': 1, '吴': 2, '神': 3, '群': 4}
    PACK_ORD = {'标准包': 0, 'SR标准包': 1, '天罡包': 2, '地煞包': 3, '人杰包': 4,
                '破军包': 5, '阴阳包': 6, '特别包': 7, '魂烈包': 8, '三英包': 9,
                '未发售': 10}
    COUNTRY_CLR = {
        '魏': 'blue', '蜀': 'green', '吴': 'red', '群': 'gold', '神': 'purple'}

    def __init__(self, name, country, pack, cost):
        self._name = name
        self._pack = pack
        self._country = country
        # 调用setter
        self.cost = cost

    @property
    def color(self):
        """按照国别返回武将颜色"""
        if self._country in Character.COUNTRY_CLR.keys():
            return Character.COUNTRY_CLR[self._country]
        else:
            return 'grey'

    @property
    def style(self):
        """按照卡包与价值标识出不同的画图风格"""
        if self._cost == 0j:
            return 'diagonals'
        elif self.pack == '未发售':
            return 'dotted'
        else:
            return ''

    @property
    def name(self):
        """返回该武将的名称"""
        return self._name

    @property
    def country(self):
        """返回该武将的国别"""
        return self._country

    @property
    def pack(self):
        """返回该武将的卡包"""
        return self._pack

    @property
    def cost(self):
        """以铜钱/金币形式返回该武将的价值"""
        if self._cost == 0:
            return '已获得'
        elif self._cost.imag > 1000:
            return '不可购买'
        else:
            return self._cost.real and str(int(self._cost.real)) + '铜钱' \
                or str(int(self._cost.imag)) + '金币'

    @cost.setter
    def cost(self, value):
        """以铜钱/金币设定该武将的价值"""
        if value == '已获得':
            self._cost = 0j
        else:
            list = re.split(r'(\d+)', value)
            if '铜钱' == list[-1]:
                self._cost = complex(list[1])
            elif '金币' == list[-1]:
                self._cost = complex(list[1] + 'j')
            else:
                self._cost = 10000j

    def __str__(self):
        """以字符串形式返回一个武将的所有属性"""
        return '{},{},{},{}'.format(self._name, self._country,
                                    self._pack, self.cost)

    def cmp_default(x, y):
        """按照卡包、国别、名称排序的比较函数"""
        return cmp(Character.PACK_ORD[x._pack], Character.PACK_ORD[y._pack]) \
            or cmp(Character.COUNTRY_ORD[x._country],
                   Character.COUNTRY_ORD[y._country]) \
            or cmp(x._name, y._name)

    def cmp_cost(x, y):
        """按价值的比较函数"""
        return -y.__cmp_cost_Character__(x)

    def __cmp_cost_NonCharacter__(x, y):
        """按价值比较武将与非武将"""
        return cmp(x._cost.imag, y._cost) or cmp(len(x._name), len(y._name))

    def __cmp_cost_Character__(x, y):
        """按价值比较武将与武将"""
        return cmp(x._cost.imag, y._cost.imag) \
            or cmp(x._cost.real, y._cost.real) or x.cmp_default(y)
pass


class Characters(object):

    """武将集，包含一些武将加载、处理的方法"""

    def __init__(self, characters_filename=unicode("data/各包武将.txt", 'utf8'),
                 gallery_filename=unicode("武将列表.txt", 'utf8'),
                 cost_filename=unicode("data/武将价格.txt", 'utf8'),
                 rebuild=False):
        """rebuild为True时，重建'武将列表'"""
        self._char_dic = {}
        # 强制rebuild或数据文件不存在时由程序生成成就列表并新建
        rebuild = rebuild or not os.path.exists(gallery_filename)
        if rebuild:
            self._char_dic = self.__read_characters(
                characters_filename, cost_filename)
        else:
            self._char_dic = self.__read_gallery(gallery_filename)

        self._sort_list = self._char_dic.keys()
        self.sort('default')
        if rebuild:
            self.write_characters(gallery_filename)

    def __preprocess_cost(self, cost_filename):
        """预生成价格列表数据以供解析"""
        cost = {
            '刘备': '0金币', '关羽': '0金币', '张飞': '0金币', '诸葛亮': '0金币',
            '赵云': '0金币', '马超': '0金币', '黄月英': '0金币', '曹操': '0金币',
            '司马懿': '0金币', '夏侯惇': '0金币', '张辽': '0金币', '许褚': '0金币',
            '郭嘉': '0金币', '甄姬': '0金币', '孙权': '0金币', '甘宁': '0金币',
            '吕蒙': '0金币', '黄盖': '0金币', '周瑜': '0金币', '大乔': '0金币',
            '陆逊': '0金币', '孙尚香': '0金币', '华佗': '0金币', '吕布': '0金币',
            '貂蝉': '0金币',

            'SR刘备': '0金币', 'SR黄月英': '120金币', 'SR马超': '80金币',
            'SR关羽': '120金币', 'SR诸葛亮': '120金币', 'SR张飞': '80金币',
            'SR赵云': '120金币', 'SR曹操': '0金币', 'SR郭嘉': '120金币',
            'SR许褚': '0金币', 'SR司马懿': '120金币', 'SR甄姬': '120金币',
            'SR张辽': '120金币', 'SR夏侯惇': '120金币', 'SR孙权': '80金币',
            'SR陆逊': '120金币', 'SR周瑜': '120金币', 'SR吕蒙': '80金币',
            'SR甘宁': '120金币', 'SR黄盖': '0金币', 'SR大乔': '120金币',
            'SR孙尚香': '120金币', 'SR貂蝉': '120金币', 'SR华佗': '0金币',
            'SR吕布': '80金币',

            'SP孙尚香': '59金币', '☆诸葛亮': '5000铜钱', 'SK黄月英': '198金币',
            'SP贾诩': '138金币', '☆关羽': '5000铜钱', 'SP蔡文姬': '89金币',
            'SP庞德': '89金币', '☆曹仁': '108金币', 'SP马超': '55金币',
            '☆赵云': '168金币', '☆貂蝉': '158金币',

            '黄忠': '105金币', '庞统': '4000铜钱', 'SK邓芝': '1铜钱',
            '廖化': '199金币', 'SK许攸': '59金币', '曹丕': '55金币',
            '荀攸': '158金币', '张春华': '360金币', '孙坚': '6000铜钱',
            '太史慈': '4000铜钱', '张昭': '158金币', '张角': '158金币',
            '贾诩': '1铜钱', '刘表': '199金币',

            '祝融': '4500铜钱', '孟获': '50金币', '法正': '20000铜钱',
            '荀彧': '59金币', 'SK曹仁': '3000铜钱', '张郃': '360金币',
            '小乔': '128金币', 'SK孙策': '168金币', 'SK祖茂': '1铜钱',
            '袁绍': '4500铜钱', 'SK公孙瓒': '2000铜钱', 'SK华雄': '108金币',
            'SK称衡': '25000铜钱',

            '刘禅': '158金币', '徐庶': '108金币', '姜维': '158金币',
            'SK王平': '1铜', '徐晃': '108金币', '典韦': '69金币',
            '曹植': '360金币', '鲁肃': '89金币', '徐盛': '89金币',
            'SK步鹭': '20000铜钱', '蔡文姬': '89金币', '庞德': '108金币',
            '陈宫': '89金币',

            '魏延': '20000铜钱', '关银屏': '20000铜钱', '关平': '499金币',
            '夏侯渊': '20000铜钱', '凌统': '20000铜钱', '韩当': '20000铜钱',
            '高顺': '20000铜钱',

            '陈琳': '1铜钱', 'SK管辂': '240金币', '诸葛恪': '1铜钱',
            '刘协': '300金币', 'SK王异': '300金币', '步练师': '200金币'
        }

        filedir = cost_filename[:cost_filename.rfind('/')]
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        with open(cost_filename, 'wb') as file:
            for x in cost.keys():
                csv_writer = csv.writer(file, lineterminator='\n')
                csv_writer.writerow([x, cost[x]])
        return cost

    def __preprocess_characters(self, characters_filename):
        """预生成各包武将数据以供解析"""
        text = "\n标准包；"
        text += "\n蜀：刘备、关羽、张飞、诸葛亮、赵云、马超、黄月英"
        text += "\n魏：曹操、司马懿、夏侯惇、张辽、许褚、郭嘉、甄姬"
        text += "\n吴：孙权、甘宁、吕蒙、黄盖、周瑜、大乔、陆逊、孙尚香"
        text += "\n群：华佗、吕布、貂蝉"
        text += "\nSR标准包："
        text += "\n蜀：SR刘备、SR黄月英、SR马超、SR关羽、SR诸葛亮、SR张飞、SR赵云"
        text += "\n魏：SR曹操、SR郭嘉、SR许褚、SR司马懿、SR甄姬、SR张辽、SR夏侯惇"
        text += "\n吴：SR孙权、SR陆逊、SR周瑜、SR吕蒙、SR甘宁、SR黄盖、SR大乔、SR孙尚香"
        text += "\n群：SR貂蝉、SR华佗、SR吕布"
        text += "\n特别包："
        text += "\n蜀：SP孙尚香、☆诸葛亮、SK黄月英"
        text += "\n魏：SP贾诩、☆关羽、SP蔡文姬、SP庞德、☆曹仁"
        text += "\n吴：--"
        text += "\n群：SP马超、☆赵云、☆貂蝉"
        text += "\n天罡包："
        text += "\n蜀：黄忠、庞统、SK邓芝、廖化"
        text += "\n魏：SK许攸、曹丕、荀攸、张春华"
        text += "\n吴：孙坚、太史慈、张昭"
        text += "\n群：张角、贾诩、刘表"
        text += "\n地煞包："
        text += "\n蜀：祝融、孟获、法正"
        text += "\n魏：荀彧、SK曹仁、张郃"
        text += "\n吴：小乔、SK孙策、SK祖茂"
        text += "\n群：袁绍、SK公孙瓒、SK华雄、SK称衡"
        text += "\n人杰包："
        text += "\n蜀：刘禅、徐庶、姜维、SK王平"
        text += "\n魏：徐晃、典韦、曹植"
        text += "\n吴：鲁肃、徐盛、SK步鹭"
        text += "\n群：蔡文姬、庞德、陈宫"
        text += "\n魂烈包："
        text += "\n神：SK神黄月英、SK神张角、神吕蒙、神赵云、SK神张辽、SK神陆逊、"
        text += "SK神郭嘉、神吕布、SK神关羽、SK神司马懿"
        text += "\n破军包："
        text += "\n蜀：魏延、关银屏、关平"
        text += "\n魏：夏侯渊"
        text += "\n吴：凌统、韩当"
        text += "\n群：高顺"
        text += "\n阴阳包："
        text += "\n蜀：--"
        text += "\n魏：陈琳、SK管辂、SK王异"
        text += "\n吴：诸葛恪、步练师"
        text += "\n群：刘协、SK左慈"
        text += "\n三英包："
        text += "\n神：三英神董卓、三英神吕布、三英神张角、三英神张让、三英神魏延"
        text += "\n未发售："
        text += "\n神：神周瑜、神曹操、神诸葛亮"

        filedir = characters_filename[:characters_filename.rfind('/')]
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        with open(characters_filename, 'wb') as file:
            file.write(text)
        return text

    def __read_characters(self, characters_filename, cost_filename):
        """从'各包武将'与'武将价格'读取信息，并初始化"""
        characters = {}
        cost = {}
        pack = ''

        # 优先构建价格字典
        if os.path.exists(cost_filename):
            with open(cost_filename, 'rb') as csvfile:
                for row in csv.reader(csvfile):
                    cost[row[0]] = row[1]
        else:
            cost = self.__preprocess_cost(cost_filename)

        # 构建各包武将，不存在时强制创建
        if os.path.exists(characters_filename):
            characters_text = open(characters_filename, 'r').read()
        else:
            characters_text = self.__preprocess_characters(characters_filename)

        for line in characters_text.split('\n'):
            m1 = re.search(r'.+包|未发售', line)
            if m1:
                pack = m1.group()
            elif re.search(r'^蜀|魏|吴|群|神', line):
                character_name_list_temp = line[6:].rstrip('\n').split("、")
                if '--' in character_name_list_temp:
                    continue
                for x in character_name_list_temp:
                    if x in cost.keys():
                        characters[x] = Character(x, line[0:3], pack, cost[x])
                    else:
                        characters[x] = Character(x, line[0:3], pack, '不可购买')

        return characters

    def __read_gallery(self, gallery_filename):
        """从'武将列表'读取武将以及价格等全部信息。"""
        characters = {}
        with open(gallery_filename, 'rb') as csvfile:
            for row in csv.reader(csvfile):
                # 使用变长参数调用的形式
                characters[row[0]] = Character(*tuple(row))
        return characters

    def write_characters(self, filename):
        """写回武将列表，一般仅在版本更新时使用"""
        with open(filename, 'wb') as file:
            for name in self._sort_list:
                x = self[name]
                csv_writer = csv.writer(file, lineterminator='\n')
                csv_writer.writerow([x.name, x.country, x.pack, x.cost])
        pass

    def buy_characters(self, name_list):
        """购买一个武将，即修改其价值为'已获得'"""
        for x in name_list:
            if x in self:
                self[x].cost = '已获得'
        pass

    def get_character_names(self):
        """返回目前武将集中可见的所有武将名"""
        return self._sort_list

    def __getitem__(self, name):
        """返回目前武将集中指定武将的所有信息"""
        return self._char_dic.get(name, NonCharacter(name))

    def __contains__(self, name):
        """返回目前武将集中是否包含该武将"""
        return name in self._sort_list

    def __iter__(self):
        """返回目前武将集的迭代器"""
        return (self[x] for x in self._sort_list)

    def filter(self, func):
        """按给定条件筛选"""
        tmp = self._sort_list
        self._sort_list = [x.name for x in filter(func, self)]
        new_obj = copy.copy(self)
        self._sort_list = tmp
        return new_obj

    def sort(self, sortby='default', reverse=False):
        """按照指定列排序"""
        if sortby == 'default':
            cmp = Character.cmp_default
        elif sortby == 'cost':
            cmp = Character.cmp_cost
        if cmp:
            self._sort_list = [
                x.name for x in sorted(self, cmp, reverse=reverse)]
        pass

    def get_regular(self):
        """返回武将列表的正则表达式"""
        return re.compile("(?<!主公是)(?<!对)("
                          + "|".join(self._sort_list) + "|三英模式.+$)")
pass

# 测试程序
if __name__ == "__main__":
    t1 = time.time()
    c = Characters(rebuild=True)
    c = Characters()
    c.get_character_names()
    c['孙权']
    c['姜孟冯']
    c.buy_characters(['SR孙权', 'SR黄盖', 'SR周瑜', 'SR马超',
                      'SR大乔', 'SR貂蝉', 'SR张飞', 'a'])
    c.sort('cost')
    c.filter(lambda x: x.cost == '已获得').write_characters(
        unicode("test/已获得武将列表.txt", 'utf8'))
    c.write_characters(unicode("test/全部武将列表.txt", 'utf8'))

    t2 = time.time()
    print "time:", t2 - t1

# -*- coding: utf8 -*-
# Achievements.py
# Author: Jiangmf
# Date: 2014-07-08
import re
import csv
import os
import copy
import time
from Characters import Characters, Character, NonCharacter


class Achievement(object):

    """成就类，包含成就名、条件与报酬"""

    def __init__(self, id, name, condition, reward, characters):
        self._id = id
        self._name = name
        self._condition = condition
        self._reward = reward
        self._condition_node = characters[
            self.__match_condition(condition, characters.get_regular())
        ]
        self._condition_count = self.__match_count_condition(condition)

        self._reward_node = characters[
            self.__match_reward(reward, characters.get_regular())
        ]
        self._reward_count = self.__match_count_reward(reward)

    @property
    def id(self):
        """返回成就id"""
        return self._id

    @property
    def name(self):
        """返回成就名"""
        return self._name

    @property
    def condition(self):
        """返回条件文本"""
        return self._condition

    @property
    def condition_node(self):
        """返回条件节点（武将/非武将）名称列表"""
        return self._condition_node

    @property
    def condition_count(self):
        """返回条件计数"""
        return self._condition_count

    @property
    def reward(self):
        """返回报酬文本"""
        return self._reward

    @property
    def reward_node(self):
        """返回报酬节点(武将/非武将)"""
        return self._reward_node

    @property
    def reward_count(self):
        """返回报酬计数"""
        return self._reward_count

    def __match_condition(self, str, reg_characters):
        """
        正则匹配原因节点(单武将或双武将或其它),结果返回一个String
        如：
        '吕布'
        '张飞'
        '三英神吕布/三英神董卓'
        """
        m1 = reg_characters.findall(str)
        # 手工匹配
        if not m1:
            return str
        # 三英武将匹配
        elif str.find('三英模式') > -1:
            result = '三英神董卓'
            if str.find('神吕布') > -1:
                result = '三英神董卓/三英神吕布'
            return result
        # 正常武将匹配
        else:
            return m1[0]

    def __match_reward(self, str, reg_characters):
        """
        正则匹配结果节点(单武将或金或使用权)，结果返回一个string
        如：
        '陈宫'
        '200金'
        'SR武将的双将使用权'
        """

        # 武将匹配
        m1 = reg_characters.search(str)
        # 金匹配
        m2 = re.search(r'(?<=赠送)\d+金', str)
        # 解锁匹配
        m3 = re.search(r'(?<=解锁).+$', str)

        if m1:
            content = m1.group()
        elif m2:
            content = m2.group() + '币'
        elif m3:
            content = m3.group()
        else:
            content = ''
        return content

    def __match_count_condition(self, str):
        # 条件计数匹配
        m0 = re.search(r'\d+(?!金)(?!\d)', str)
        if m0:
            count = m0.group()
        else:
            count = '1'
        return count

    def __match_count_reward(self, str):
        # 报酬计数匹配
        m0 = re.search(r'1/\d+', str)
        if m0:
            count = m0.group()
        else:
            count = '1/1'
        return count

    def __str__(self):
        """以字符串形式返回一条成就"""
        return '{}:{}->{}({},{})'.format(
            self.name, self.condition,
            self.reward_node.name,
            self.reward_node.cost, self.reward_count
        )

    def cmp_default(self, other):
        """按照id排序的比较函数"""
        return cmp(self._id, other._id)

    def cmp_cost(self, other):
        """按照cost排序的比较函数"""
        return self._reward_node.cmp_cost(other._reward_node)
    pass


class Achievements:

    """成就类，包含成就名、条件与结果"""

    def __init__(self, characters,
                 achievements_filename=unicode("data/Achievement", 'utf8')
                 ):
        self._characters = characters
        # 读取修正完格式的成就列表
        achievements_text = open(achievements_filename, 'r').read()
        self._achievements = self.__read_achievements(achievements_text)
        pass

    def write_achievements(self, filename):
        """写回成就列表，一般仅在版本更新时使用"""
        filedir = filename[:filename.rfind('/')]
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        with open(filename, 'wb') as file:
            for x in self._achievements:
                csv.writer(file, delimiter='#', lineterminator='\n').writerow(
                    [x.name, x.condition, x.reward])

    def write_achievements_detail(self, filename):
        """全面的成就列表导出"""
        with open(filename, 'wb') as file:
            for x in self._achievements:
                csv.writer(file, delimiter='#', lineterminator='\n').writerow(
                    [x.name, x.condition_node.name, x.condition_count,
                     x.reward_node.name, x.reward_node.cost, x.reward_count])

    def __read_achievements(self, text):
        """读取成就，整理成成就列表。"""
        # 按照武将名进行文本正则解析处理
        achievements = []
        achievements_list = [line.split('#')
                             for line in text.split('\n') if line != '']
        for i, x in enumerate(achievements_list):
            achievements.append(
                Achievement(i, x[0], x[1], x[2], self._characters))

        return achievements

    def filter(self, func):
        """按给定条件筛选"""
        tmp = self._achievements
        self._achievements = filter(func, self._achievements)
        new_obj = copy.copy(self)
        self._achievements = tmp
        return new_obj

    def sort(self, sortby='default', reverse=False):
        """按照指定方式排序"""
        if sortby == 'default':
            cmp = Achievement.cmp_default
        elif sortby == 'cost':
            cmp = Achievement.cmp_cost
        if cmp:
            self._achievements.sort(cmp, reverse=reverse)
        pass

    def __iter__(self):
        """迭代器, 返回目前成就类中可见的所有成就信息"""
        return self._achievements.__iter__()

    def reward_characters(self):
        """返回目前成就类中可获得的所有武将"""
        return [x.reward_node for x in self._achievements]

    def characters_should_buy(self):
        """获取推荐购买武将的函数"""
        character_set = set(self._characters.filter(
            lambda x: re.match(r'\d+金币', x.cost)
        ))
        character_set.difference_update(set(self.reward_characters()))
        character_list = sorted(list(character_set), cmp=Character.cmp_cost)
        return ['{}:{}'.format(x.name, x.cost) for x in character_list]

    def characters_should_use(self):

        # 滤选报酬为武将的成就
        achievements = self.filter(
            lambda x: isinstance(x.reward_node, Character))
        # 去掉报酬武将已获得或未发售的成就
        achievements = achievements.filter(
            lambda x: x.reward_node.cost != '已获得'
            and x.reward_node.pack != '未发售')
        # 滤选待刷武将已获得的成就
        achievements = achievements.filter(
            lambda x: x.condition_node.cost == '已获得')

        achievements.sort('cost', True)
        return achievements

# 测试程序
if __name__ == "__main__":
    t1 = time.time()
    c = Characters()

    c.buy_characters(
        c.filter(lambda x: re.match(r'\d+铜钱', x.cost)).get_character_names())
    c.buy_characters(['SK许攸', '曹丕', '张角', '黄忠', '张春华', '廖化', '刘表',
                      '孟获', '荀彧', '张郃',
                      '刘禅', '徐庶', '蔡文姬', '庞德', '典韦', '鲁肃',
                      'SK神张角', 'SK神黄月英'
                      ])
    c.buy_characters(
        c.filter(
            lambda x: re.match(r'破军包|阴阳包|特别包', x.pack)).get_character_names()
    )
    c.buy_characters(
        c.filter(lambda x: re.match(r'SR.+', x.name)).get_character_names()
    )
    a = Achievements(characters=c)
    a.filter(lambda x: isinstance(x.condition_node, NonCharacter)
             ).write_achievements_detail(
        unicode("test/非武将因素成就.txt", 'utf-8')
    )
    a.sort('cost')
    a.write_achievements_detail(unicode("test/全成就列表细节.txt", 'utf8'))
    a.characters_should_buy()
    a.characters_should_use()

    t2 = time.time()
    print "time:", t2 - t1

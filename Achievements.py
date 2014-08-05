# -*- coding: utf8 -*-
# Achievements.py
# Author: Jiangmf
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
        self._reward_node = characters[
            self.__match_reward(reward, characters.get_regular())
        ]
        self._reward_count = self.__match_count(reward)

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

    def __match_count(self, str):
        # 完成度匹配
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
                 achievements_filename=unicode("data/成就.txt", 'utf8'),
                 rebuild=False
                 ):
        self._characters = characters
        rebuild = rebuild or not os.path.exists(achievements_filename)
        if rebuild:
            # 强制rebuild或数据文件不存在时由程序生成成就列表并新建
            self._achievements_text = self.__preprocess()
        else:
            # 读取修正完格式的成就列表
            self._achievements_text = open(achievements_filename, 'r').read()

        self._achievements = self.__read_achievements(self._achievements_text)
        if rebuild:
            self.write_achievements(achievements_filename)
        pass

    def __preprocess(self):
        """预生成成就文本以供解析"""

        # 预生成成就
        text = ''
        text += '\n神驹飞将#标准模式下使用吕布在1局游戏中发动方天画戟特效杀死至少3名角色。#赠送陈宫的前提（1/3）'
        text += '\n武之化身#使用吕布获得80场标准模式游戏胜利。#赠送陈宫的前提（1/3）'
        text += '\n闭月羞花#标准模式下使用貂蝉在1局游戏中发动离间造成至少3名角色死亡。#赠送☆貂蝉的前提（1/2）'
        text += '\n绝世舞姬#使用貂蝉获得80场标准模式游戏胜利。#赠送☆貂蝉的前提（1/2）'
        text += '\n圣术名医#标准模式下使用华佗在1局游戏中发动回春使至少4个不同的角色脱离濒死状态。#赠送☆关羽的前提（1/2）'
        text += '\n妙手回春#使用华佗获得80场标准模式游戏胜利。#赠送☆关羽的前提（1/2）'
        text += '\n乱世奸雄#标准模式下使用曹操在1局游戏中发动霸图得到至少4张南蛮入侵和1张万箭齐发。#赠送蔡文姬的前提（1/2）'
        text += '\n魏武帝#使用曹操获得80场标准模式游戏胜利。#赠送蔡文姬的前提（1/2）'
        text += '\n掩其无备#标准模式下使用张辽在1局游戏中发动至少12次突袭。#赠送徐晃的前提（1/2）'
        text += '\n前将军#使用张辽获得80场标准模式游戏胜利。#赠送徐晃的前提（1/2）'
        text += '\n你死我活#标准模式下使用夏侯惇在1局游戏中发动誓仇杀死至少3名角色。#赠送SK曹仁的前提（1/2）'
        text += '\n独眼罗刹#使用夏侯惇获得80场标准模式游戏胜利。#赠送SK曹仁的前提（1/2）'
        text += '\n暴虎冯河#标准模式下使用许褚在1局游戏中发动怒发至少3次并在怒发的回合中杀死过至少3名角色。#赠送SK许攸的前提（1/2）'
        text += '\n虎痴#使用许褚获得80场标准模式游戏胜利。#赠送SK许攸的前提（1/2）'
        text += '\n不遗余力#标准模式下使用郭嘉在1局游戏中发动遗计发牌给其他角色至少8次。#赠送法正的前提（1/3）'
        text += '\n早逝先知#使用郭嘉获得80场标准模式游戏胜利。#赠送法正的前提（1/3）'
        text += '\n手眼通天#标准模式下使用司马懿在1局游戏中有至少3次发动神算都抽到对方1张桃。#赠送荀彧的前提（1/2）'
        text += '\n狼顾之鬼#使用司马懿获得80场标准模式游戏胜利。#赠送荀彧的前提（1/2）'
        text += '\n洛神赋#标准模式下使用甄姬一回合内发动洛神在不被改变判定牌的情况下连续判定黑色花色至少8次。#赠送曹丕的前提（1/2）'
        text += '\n薄幸美人#使用甄姬获得80场标准模式游戏胜利。#赠送曹丕的前提（1/2）'
        text += '\n不忍之心#标准模式下使用刘备在1局游戏中发动雌雄双股剑特效杀死至少3名女性角色。#赠送刘禅的前提（1/3）'
        text += '\n乱世枭雄#使用刘备获得80场标准模式游戏胜利。#赠送刘禅的前提（1/3）'
        text += '\n轰雷咆哮#标准模式下使用张飞在1局游戏中发动丈八蛇矛特效杀死至少3名角色 。#赠送黄忠的前提(1/2）'
        text += '\n万夫不当#使用张飞获得80场标准模式游戏胜利。#赠送黄忠的前提(1/2）'
        text += '\n全军突击#标准模式下使用马超在1局游戏中不被改变判定牌的情况下发动铁骑连续判定红色花色至少5次。#赠送SP马超的前提（1/2）'
        text += '\n一骑当千#使用马超获得80场标准模式游戏胜利。#赠送SP马超的前提（1/2）'
        text += '\n武圣显灵#标准模式下使用关羽在1局游戏中发动青龙偃月刀特效杀死至少3名角色。#赠送SK神关羽的前提（1/4）'
        text += '\n美髯公#使用关羽获得80场标准模式游戏胜利。#赠送SK神关羽的前提（1/4）'
        text += '\n浑身是胆#标准模式下使用赵云在1局游戏中发动青?剑特效杀死至少3名角色。#赠送☆赵云的前提（1/2）'
        text += '\n龙枪天升#使用赵云获得80场标准模式游戏胜利。#赠送☆赵云的前提（1/2）'
        text += '\n灵心锦囊#标准模式下使用黄月英在1个回合内发动至少10次灵心。#赠送祝融的前提（1/2）'
        text += '\n归隐杰女#使用黄月英获得80场标准模式游戏胜利。#赠送祝融的前提（1/2）'
        text += '\n空城绝唱#标准模式下使用诸葛亮在1局游戏中有至少8个回合结束时是空城状态。#赠送☆诸葛亮的前提（1/2）'
        text += '\n迟暮丞相#使用诸葛亮获得80场标准模式游戏胜利。#赠送☆诸葛亮的前提（1/2）'
        text += '\n援兵天降#标准模式下使用孙权在1局游戏中被吴国武将用桃救至少3次。#赠送太史慈的前提（1/2）'
        text += '\n年轻贤君#使用孙权获得80场标准模式游戏胜利。#赠送太史慈的前提（1/2）'
        text += '\n神出鬼没#标准模式下使用甘宁在1个回合内发动至少6次奇袭。#赠送张昭的前提（1/3）'
        text += '\n锦帆游侠#使用甘宁获得80场标准模式游戏胜利。#赠送张昭的前提（1/3）'
        text += '\n赴汤蹈火#标准模式下使用黄盖1个回合内发动至少9次苦肉。#赠送神周瑜的前提（1/7）'
        text += '\n轻身为国#使用黄盖获得80场标准模式游戏胜利。#赠送神周瑜的前提（1/7）'
        text += '\n伺机待发#标准模式下使用吕蒙将手牌囤积到32张。#赠送鲁肃的前提（1/2）'
        text += '\n白衣渡江#使用吕蒙获得80场标准模式游戏胜利。#赠送鲁肃的前提（1/2）'
        text += '\n移花接木#标准模式下使用大乔在一局游戏中发动流离至少6次。#赠送小乔的前提（1/2）'
        text += '\n矜持之花#使用大乔获得80场标准模式游戏胜利。#赠送小乔的前提（1/2）'
        text += '\n因祸得福#标准模式下使用孙尚香在1局游戏中累计失去至少8张已装备的装备牌。#赠送SP孙尚香的前提（1/2）'
        text += '\n弓腰姬#使用孙尚香获得80场标准模式游戏胜利。#赠送SP孙尚香的前提（1/2）'
        text += '\n言议英发#标准模式下使用周瑜在1局游戏中使用反间杀死至少3名角色。#赠送庞统的前提（1/2）'
        text += '\n大都督#使用周瑜获得80场标准模式游戏胜利。#赠送庞统的前提（1/2）'
        text += '\n连绵不绝#标准模式下使用陆逊在1个回合内发动至少10次连营。#赠送徐盛的前提（1/3）'
        text += '\n儒生雄才#使用陆逊获得80场标准模式游戏胜利。#赠送徐盛的前提（1/3）'
        text += '\n苍天无影#标准模式下使用张角在1局游戏发动落雷杀死至少4名角色。#赠送SK神张角的前提（1/5）'
        text += '\n天公将军#使用张角获得80场标准模式游戏胜利。#赠送SK神张角的前提（1/5）'
        text += '\n智乱天下#标准模式下使用贾诩发动乱武，并在乱武结算中有至少4名角色死亡。#赠送SK神司马懿的前提（1/7）'
        text += '\n冷酷毒士#使用贾诩获得80场标准模式游戏胜利。#赠送SK神司马懿的前提（1/7）'
        text += '\n恃才傲物#标准模式下使用SK许攸在1局游戏中连续8个回合未损失任何体力。#赠送袁绍的前提（1/2）'
        text += '\n诡计智将#使用SK许攸获得80场标准模式游戏胜利。#赠送袁绍的前提（1/2）'
        text += '\n图南鹏翼#标准模式下使用曹丕在1局游戏中对同一名角色累计发动放逐翻面至少7次。#赠送曹植的前提（1/3）'
        text += '\n霸业承继#使用曹丕获得80场标准模式游戏胜利。#赠送曹植的前提（1/3）'
        text += '\n百步穿杨#标准模式下使用黄忠在1局游戏中，剩余1点体力时累计发动极弓杀死至少3名角色。#赠送姜维的前提（1/3）'
        text += '\n老当益壮#使用黄忠获得80场标准模式游戏胜利。#赠送姜维的前提（1/3）'
        text += '\n铁索连舟#标准模式下使用庞统在1回合内发动连环横置至少7名角色。#赠送神周瑜的前提（1/7）'
        text += '\n凤雏#使用庞统获得80场标准模式游戏胜利。#赠送神周瑜的前提（1/7）'
        text += '\n江东之虎#标准模式下使用孙坚在1局游戏中连续至少5回合在1体力时发动英魂。#赠送SK华雄的前提（1/3）'
        text += '\n武烈帝#使用孙坚获得80场标准模式游戏胜利。#赠送SK华雄的前提（1/3）'
        text += '\n忠义豪壮#标准模式下使用太史慈在1回合内发动扫讨拼点胜利后，使用【杀】杀死至少4名角色。#赠送SK孙策的前提（1/2）'
        text += '\n笃烈之士#使用太史慈获得80场标准模式游戏胜利。#赠送SK孙策的前提（1/2）'
        text += '\n辅吴将军#标准模式下使用张昭在一局游戏中发动直谏将至少5张装备牌置于吴势力武将的装备区。#赠送SK神陆逊的前提（1/5）'
        text += '\n经天纬地#使用张昭获得80场标准模式游戏胜利。#赠送SK神陆逊的前提（1/5）'
        text += '\n坚贞简亮#标准模式使用SK邓芝作为忠臣获得两局胜利。#赠送神赵云的前提（1/5）'
        text += '\n乱箭肃敌#标准模式下使用袁绍在1回合内发动齐射至少7次。#赠送SK神张角的前提（1/5）'
        text += '\n高贵名门#使用袁绍获得80场标准模式游戏胜利。#赠送SK神张角的前提（1/5）'
        text += '\n义从号令#标准模式下使用SK公孙瓒在体力大于2的情况下杀死至少3名角色，并且在体力1的情况下存活并获胜。#赠送张角的前提（1/2）'
        text += '\n白马将军#使用SK公孙瓒获得80场标准模式游戏胜利。#赠送张角的前提（1/2）'
        text += '\n驱虎吞狼#标准模式下使用荀彧在1局游戏中使用驱虎造成至少4名角色死亡。#赠送荀攸的前提（1/3）'
        text += '\n王佐之才#使用荀彧获得80场标准模式游戏胜利。#赠送荀攸的前提（1/3）'
        text += '\n固若金汤#标准模式下使用SK曹仁在1局游戏中发动至少5次据守，并且全局损失体力不多于2点的情况下获胜。#赠送☆曹仁的前提（1/2）'
        text += '\n大将军#使用SK曹仁获得80场标准模式游戏胜利。#赠送☆曹仁的前提（1/2）'
        text += '\n刺美人#标准模式下使用祝融在一局游戏中对男性发动烈刃并拼点赢至少4次。#赠送孟获的前提（1/2）'
        text += '\n野性女王#使用祝融获得80场标准模式游戏胜利。#赠送孟获的前提（1/2）'
        text += '\n不死金刚#标准模式下使用孟获在一局游戏中发动再起回复体力至少9点。#赠送SK神黄月英的前提（1/4）'
        text += '\n南蛮王#使用孟获得80场标准模式游戏胜利。#赠送SK神黄月英的前提（1/4）'
        text += '\n怜香惜玉#标准模式下使用小乔在1局游戏中发动天香让一名男性武将累计摸牌至少15张。#赠送神周瑜的前提(1/7）'
        text += '\n矫情之花#使用小乔获得80场标准模式游戏胜利。#赠送神周瑜的前提(1/7）'
        text += '\n猛锐冠世#标准模式下使用SK孙策在1回合内发动昂扬摸牌至少8张。#赠送神吕蒙的前提(1/5）'
        text += '\n小霸王#使用SK孙策获得80场标准模式游戏胜利。#赠送神吕蒙的前提(1/5）'
        text += '\n勇冠三军#标准模式下使用SK华雄在体力上限为1的情况下获得胜利。#赠送神吕布的前提(1/6）'
        text += '\n魔将#使用SK华雄获得80场标准模式游戏胜利。#赠送神吕布的前提(1/6）'
        text += '\n血路先驱#标准模式使用SK祖茂作为忠臣获得两局胜利。#赠送SK神陆逊的前提（1/5）'
        text += '\n乱世歌姬#标准模式下使用蔡文姬在1局游戏里发动4次悲歌并发动断肠，然后赢得胜利。#赠送SP蔡文姬的前提(1/2）'
        text += '\n异乡孤女#使用蔡文姬获得80场标准模式游戏胜利。#赠送SP蔡文姬的前提(1/2）'
        text += '\n弹尽粮绝#标准模式下使用徐晃在1局游戏中用装备区的牌发动断粮至少5次#赠送SK神张辽的前提（1/4）'
        text += '\n亚夫遗风#使用徐晃获得80场标准模式游戏胜利。#赠送SK神张辽的前提（1/4）'
        text += '\n周苛之节#标准模式下使用庞德在1局游戏中发动猛进至少6次。#赠送SP庞德的前提(1/2）'
        text += '\n人马一体#使用庞德获得80场标准模式游戏胜利。#赠送SP庞德的前提(1/2）'
        text += '\n力荐英才#标准模式下使用徐庶在1局游戏中发动举荐至少6次，并且赢得胜利。#赠送神诸葛亮的前提（1/5）'
        text += '\n忠孝侠士#使用徐庶获得80场标准模式游戏胜利。#赠送神诸葛亮的前提（1/5））'
        text += '\n大智若愚#标准模式下使用刘禅每回合都发动放权并获得胜利累计6次。#赠送神赵云的前提（1/5）'
        text += '\n无为之主#使用刘禅获得80场标准模式游戏胜利。#赠送神赵云的前提（1/5）'
        text += '\n刚直壮烈#标准模式下使用陈宫在1局游戏中对吕布发动明策5次。#赠送神吕布的前提（1/6）'
        text += '\n决意赴死#使用陈宫获得80场标准模式游戏胜利。#赠送神吕布的前提（1/6）'
        text += '\n指囷相赠#标准模式下使用鲁肃在1局游戏中发动好施分给其他角色累计15张牌。#赠送神吕蒙的前提（1/5）'
        text += '\n独断之明#使用鲁肃获得80场标准模式游戏胜利。#赠送神吕蒙的前提（1/5）'
        text += '\n一夫当关#标准模式下使用典韦在1局游戏中发动至少5次强袭,并用强袭至少杀死3名角色。#赠送神曹操的前提（1/6）'
        text += '\n古之恶来#使用典韦获得80场标准模式游戏胜利。#赠送神曹操的前提（1/6）'
        text += '\n才兼文武#标准模式下使用姜维一局中挑衅至少弃4张牌，并发动星占至少3次。#赠送神诸葛亮的前提（1/5）'
        text += '\n龙之传承#使用姜维获得80场标准模式游戏胜利。#赠送神诸葛亮的前提（1/5）'
        text += '\n奋身出命#标准模式下使用徐盛在一局游戏中对同一名角色发动至少4次踏破并获胜。。#赠送SK神陆逊的前提（1/5）'
        text += '\n江东铁壁#使用徐盛获得80场标准模式游戏胜利。#赠送SK神陆逊的前提（1/5）'
        text += '\n无当飞将#标准模式使用SK王平作为忠臣获得三局胜利。#赠送SK神张辽的前提（1/4）'
        text += '\n八斗之才#标准模式使用曹植在一局游戏中发动落英获得至少10张牌并发动酒诗翻面至少4次。#赠送神曹操的前提（1/6）'
        text += '\n琳琅妙笔#使用曹植获得80场标准模式游戏胜利。#赠送神曹操的前提（1/6）'
        text += '\n西凉猛狮#标准模式下在主公是曹操而其他场上角色全部存活的情况下，使用SP马超作为反贼获得胜利10次。#赠送神赵云的前提（1/5）'
        text += '\n梦醉良缘#标准模式下在主公是刘备的情况下，使用SP孙尚香作为内奸获得胜利10次。#赠送SK神黄月英的前提（1/4）'
        text += '\n算无遗策#标准模式下在主公是曹操的情况下，使用SP贾诩作为忠臣杀死至少4名角色并获得胜利6次。#赠送贾诩的前提（1/1）'
        text += '\n少年英雄#标准模式下在主公是刘备的情况下，使用☆赵云作为忠臣杀死至少4名反贼获得胜利6次。#赠送神赵云的前提(1/5）'
        text += '\n活心醒龙#标准模式下在主公是曹操的情况下，使用☆关羽作为内奸一局中杀死至少3名魏势力角色并获得胜利。#赠送庞德的前提(1/1）'
        text += '\n星火燎原#标准模式下使用☆诸葛亮在1回合内发动火计造成至少7点伤害。#赠送徐庶的前提(1/2）'
        text += '\n幻妖言惑#标准模式下使用☆貂蝉在1回合杀死4名男性其他角色。#赠送神吕布的前提(1/6）'
        text += '\n险不辞难#标准模式下使用☆曹仁在一局游戏内发起溃围技能摸牌至少11张，并发动严整技能至少4次。#赠送SK神张辽的前提(1/4）'
        text += '\n金璧之才#标准模式下在主公是曹操的情况下使用SP蔡文姬以内奸身份获得胜利6次。#赠送神曹操的前提(1/6）'
        text += '\n抬榇之悟#标准模式下使用SP庞德发动猛进弃掉同一名角色装备区累计4张牌。#赠送SK神关羽的前提(1/4）'
        text += '\n治世之道#标准模式下使用SR曹操作为主公在一局游戏中发动治世累计令其他角色回复9点体力。#赠送曹植的前提(1/3）'
        text += '\n将门虎女#标准模式使用关银屏在一局游戏中发动龙咆2次，血祭2次。#赠送SK左慈的前提(1/4）'
        text += '\n破竹之咒#标准模式使用陈琳在一局游戏中对曹操使用笔伐2次，并使用颂词令其摸两张牌。#赠送SK左慈的前提(1/4）'
        text += '\n兴家赤族#标准模式使用诸葛恪在一局游戏中发动黩武令三名不同名角色进入濒死状态。#赠送SK左慈的前提(1/4）'
        text += '\n真命天子#标准模式使用刘协在一局游戏中发动密诏四次，天命四次并获得胜利。#赠送SK左慈的前提(1/4）'
        text += '\n君临天下#作为主公，获得100次游戏胜利。#赠送孙坚的前提(1/4）'
        text += '\n草头天子#作为反贼，获得100次游戏胜利。#赠送SK公孙瓒的前提(1/4）'
        text += '\n忠心耿耿#作为忠臣，获得100次游戏胜利。#赠送典韦的前提(1/4）'
        text += '\n唯我独尊#作为内奸，取得一次胜利。#赠送SP贾诩的前提(1/4）'
        text += '\n运筹帷幄#作为内奸，取得100次胜利。#赠送SP贾诩的前提(1/4）'
        text += '\n秉公无私#作为主公，在一局游戏内从未对忠臣造成伤害并取得胜利。#赠送孙坚的前提(1/4）'
        text += '\n天道威仪#作为主公，在忠臣全死光后，手刃至少3名角色并取得胜利。#赠送孙坚的前提(1/4）'
        text += '\n至圣至明#作为主公，亲手杀死所有反贼和内奸，忠臣全未死。#赠送孙坚的前提(1/4）'
        text += '\n乱臣贼子#作为反贼，在一局游戏内杀2名忠臣（内奸亦可）。#赠送SK公孙瓒的前提(1/4）'
        text += '\n乘虚而入#作为反贼，在自己的第一个回合手刃主公。#赠送SK公孙瓒的前提(1/4）'
        text += '\n绝处逢生#作为反贼，其他反贼全死亡且忠臣全存活的状况下获得胜利。#赠送SK公孙瓒的前提(1/4）'
        text += '\n赤胆忠心#作为忠臣，在一局游戏内杀2名反贼（内奸亦可）。#赠送典韦的前提(1/4）'
        text += '\n忠肝义胆#作为忠臣，在自身存活且主公满血状态下获取胜利。#赠送典韦的前提(1/4）'
        text += '\n竭智尽忠#作为忠臣，自己的第一个回合杀掉至少一名反贼或者内奸，并且取胜。#赠送典韦的前提(1/4）'
        text += '\n老奸巨猾#作为内奸，在主公误杀忠臣的情况下获胜。#赠送SP贾诩的前提(1/4）'
        text += '\n老谋深算#作为内奸，手刃4个反贼或者忠臣并获得胜利。#赠送SP贾诩的前提(1/4）'
        text += '\n心不畏死#在自己死亡的情况下获得胜利累计100次。#赠送100金'
        text += '\n踏尸前行#杀死至少4名其他角色并获得胜利累计100次。#赠送150金'
        text += '\n天下无双#完成标准包全部武将成就。#赠送250金'
        text += '\n功成名就#完成全部身份类成就。#赠送200金'
        text += '\n武之皇#获得评价【武皇的证明】累计10次。#赠送三英神董卓(1/1）,'
        text += '\n面面俱到#在标准、三英、武皇模式中获得良、绝、神评价各5次。#赠送陈宫的前提（1/3）'
        text += '\n助顺讨逆#三英模式战胜双将状态的神董卓与神吕布累计8次。#赠送刘禅的前提（1/3）'
        text += '\n失道寡助#三英模式战胜非双将状态的神董卓累计10次。#赠送徐庶的前提（1/2）'
        text += '\n狱魔祸世#三英模式使用非双将状态的神董卓获胜累计10次。#赠送SK华雄的前提（1/3）'
        text += '\n天降之财#标准模式下使用“免费金币”功能获得累计150金币。#赠送姜维的前提（1/3）'
        text += '\n君子之交#标准模式下使用“分享”功能分享游戏体会累计1次。#赠送张昭的前提（1/3）'
        text += '\n时来运转#幸运签抽取“中吉”18次。#赠送SK神黄月英的前提（1/4）'
        text += '\n岁在甲子#幸运签抽取“大吉”6次。#赠送SK神张角的前提（1/5）'
        text += '\n天遂人愿#幸运签抽取“万吉”3次。#赠送神吕蒙的前提（1/5）'
        text += '\n谦虚好学#完成新手教学的全程。#赠送荀攸的前提（1/3）'
        text += '\n慧眼如炬#在评价的抽取奖励中,抽得一枚拼图碎片。#赠送法正的前提（1/3）'
        text += '\n以逸待劳#在图鉴中，花费金币购买一枚拼图碎片。#赠送徐盛的前提（1/3）'
        text += '\n灵魂解放#在挑战模式中获得全胜（连续通过6小关），累计10次。#解锁SR武将的双将使用权'
        text += '\n三天打鱼#在“任务册”内累计领取五次每日任务的奖励(当前等级20或以上)#赠送SK神关羽的前提（1/4）'
        text += '\n两天晒网#在“任务册”内使用挑战令“直接完成”两个每日任务(当前等级20或以上)#赠送神吕布的前提（1/6）'
        text += '\n恩怨分明#标准模式使用法正在一局游戏中分别在获得卡牌和受到伤害时发动恩怨各3次。#赠送SK神司马懿的前提（1/7）'
        text += '\n蜀汉谋主#使用法正获得80场标准模式游戏胜利。#赠送SK神司马懿的前提（1/7）'
        text += '\n再世留侯#标准模式使用荀攸在一局游戏中发动画策12次。#赠送SK神司马懿的前提（1/7）'
        text += '\n曹魏谋主#使用荀攸获得80场标准模式游戏胜利。#赠送SK神司马懿的前提（1/7）'
        text += '\n刀剑封魔#在“任务册”中完成三英任务一次(当前等级18或以上)#赠送SK神司马懿的前提（1/7）'

        # 强制排错
        text = re.sub(r'(?<!SK)王平', "SK王平", text)
        text = re.sub(r'(?<!SK)邓芝', "SK邓芝", text)
        text = re.sub(r'(?<!SK)祖茂', "SK祖茂", text)
        text = re.sub(r'(?<!SK)神陆逊', "SK神陆逊", text)
        text = re.sub(r'(?<!SK)神黄月英', "SK神黄月英", text)
        text = re.sub(r'(?<!SK)神张角', "SK神张角", text)
        text = re.sub(r'(?<!SK)神张辽', "SK神张辽", text)
        text = re.sub(r'(?<!SK)神关羽', "SK神关羽", text)
        text = re.sub(r'(?<!SK)神司马懿', "SK神司马懿", text)

        return text

    def write_achievements(self, filename):
        """写回成就列表，一般仅在版本更新时使用"""
        with open(filename, 'wb') as file:
            for x in self._achievements:
                csv.writer(file, delimiter='#', lineterminator='\n').writerow(
                    [x.name, x.condition, x.reward])

    def write_achievements_detail(self, filename):
        """全面的成就列表导出"""
        with open(filename, 'wb') as file:
            for x in self._achievements:
                csv.writer(file, delimiter='#', lineterminator='\n').writerow(
                    [x.name, x.condition_node.name, x.reward_node.name,
                     x.reward_node.cost, x.reward_count])

    def __read_achievements(self, text):
        """读取成就，整理成成就列表。"""
        # 按照武将名进行文本正则解析处理
        achievements = []
        achievements_list = [line.split('#')
                             for line in text.split('\n') if line != '']
        for i in range(len(achievements_list)):
            x = achievements_list[i]
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
        return ['{}:{}->{}({},{})'.format(
            x.name, x.condition_node.name,
            x.reward_node.name,
            x.reward_node.cost, x.reward_count
            ) for x in achievements._achievements]

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
    a = Achievements(characters=c, rebuild=False)
    a = Achievements(characters=c, rebuild=True)
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

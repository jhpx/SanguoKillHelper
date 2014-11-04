# -*- coding: utf8 -*-
# AchievementsPlot.py
# Author: Jiangmf
# Date: 2014-07-08
import pygraphviz as pgv
from Characters import Characters
from Achievements import Achievements


class AchievementsPlot(object):

    """成就画图类，仅用于画图"""

    def __init__(self, characters):
        self._characters = characters
        self._achievements = Achievements(characters)
        pass

    def get_ahievements_data_after_reassign_group(self):
        """整理武将依赖，按照相同节点先分后合"""
        group = {}
        # 两重循环，但其实第二重最大循环次数也只有2次
        for x in self._achievements:
            for y in x.condition_node.name.split('/'):
                key = y + "#" + x.reward_node.name
                group[key] = group.get(key, '') + ',' + x.name
        return [k + "#" + group[k][1:] for k in group.keys()]

    def draw_png(self, png_filename=unicode('成就.png', 'utf8')):
        """生成一幅武将成就图"""
        # 设定一个有向图
        G = pgv.AGraph(rankdir='LR')

        G.node_attr['fontname'] = 'Simsun'
        G.edge_attr['fontname'] = 'Simsun'
        G.node_attr['shape'] = 'box'

        for y in self.get_ahievements_data_after_reassign_group():
            # 添加边前添加节点，AGraph会自动处理重复
            info = y.split('#')
            c0 = self._characters[info[0]]
            c1 = self._characters[info[1]]

            G.add_node(c0.name.decode('utf8'), color=c0.color, style=c0.style)
            G.add_node(c1.name.decode('utf8'), color=c1.color, style=c1.style)

            G.add_edge(
                info[0].decode('utf8'),
                info[1].decode('utf8'),
                label=info[2].decode('utf8')
            )
#       print G
        G.layout('dot')
        G.draw(png_filename)
        pass
# 测试程序
if __name__ == "__main__":
    c = Characters()
    g = AchievementsPlot(c)
#    print "\n".join(g.get_ahievements_data_after_reassign_group())
    g.draw_png('test/test.png')

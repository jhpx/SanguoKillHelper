# -*- coding: utf8 -*-
# Characters.py
# Author: Jiangmf
import abc, re, csv, copy
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
		return self._cost>1000 and '不可购买' or str(int(self._cost))+'金币'

	def cmp_cost(self, other):
		"""按价值的比较函数"""
		return -other.__cmp_cost_NonCharacter__(self)

	def __cmp_cost_NonCharacter__(self, other):
		"""按价值比较非武将与非武将"""
		return cmp(self._cost, other._cost) or cmp(self._name, other._name)

	def __cmp_cost_Character__(self, other):
		"""按价值比较非武将与武将"""
		return cmp(self._cost, other._cost.imag) or cmp(len(self._name), len(other._name))

pass
class Character(Node):
	"""武将类：包含武将名、国别、卡包、价值、颜色、风格"""
	ORDER_COUNTRY = {'蜀':0, '魏':1, '吴':2, '神':3, '群':4}
	ORDER_PACK    = {'标准包':0, 'SR标准包':1, '天罡包':2, '地煞包':3, '人杰包':4, \
	'破军包':5, '阴阳包':6, '特别包':7, '魂烈包':8, '三英包':9,'未发售':10}
	COLOR_COUNTRY = {'魏':'blue', '蜀':'green', '吴':'red', '群':'yellow', '神':'purple'}

	def __init__(self, name, country, pack, cost):
		self._name = name
		self._pack = pack
		self._country = country
		#调用setter
		self.cost = cost

	@property
	def color(self):
		"""按照国别返回武将颜色"""
		if self._country in Character.COLOR_COUNTRY.keys():
			return Character.COLOR_COUNTRY[self._country]
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
		elif self._cost.imag>1000:
			return '不可购买'
		else:
			return self._cost.real and str(int(self._cost.real))+'铜钱' \
			or str(int(self._cost.imag))+'金币'

	@cost.setter
	def cost(self, value):
		"""以铜钱/金币设定该武将的价值"""
		if value=='已获得':
			self._cost = 0j
		else:
			list = re.split(r'(\d+)', value)
			if '铜钱'==list[-1]:
				self._cost = complex(list[1])
			elif '金币'==list[-1]:
				self._cost = complex(list[1]+'j')
			else:
				self._cost = 10000j

	def __str__(self):
		"""以字符串形式返回一个武将的所有属性"""
		return '%s,%s,%s,%s'%(self._name, self._country, self._pack, self.cost)

	def cmp_default(self, other):
		"""按照卡包、国别、名称排序的比较函数"""
		return cmp(Character.ORDER_PACK[self._pack], Character.ORDER_PACK[other._pack]) \
		or cmp(Character.ORDER_COUNTRY[self._country], Character.ORDER_COUNTRY[other._country]) \
		or cmp(self._name, other._name)

	def cmp_cost(self, other):
		"""按价值的比较函数"""
		return -other.__cmp_cost_Character__(self)

	def __cmp_cost_NonCharacter__(self, other):
		"""按价值比较武将与非武将"""
		return cmp(self._cost.imag, other._cost) or cmp(len(self._name), len(other._name))

	def __cmp_cost_Character__(self, other):
		"""按价值比较武将与武将"""
		return cmp(self._cost.imag, other._cost.imag) \
		or cmp(self._cost.real, other._cost.real) \
		or self.cmp_default(other)
pass

class Characters(object):
	"""武将集，包含一些武将加载、处理的方法"""
	def __init__(self, characters_filename = unicode("各包武将.txt", 'utf8'), \
	gallery_filename = unicode("武将列表.txt", 'utf8'), \
	cost_filename = unicode("武将价格.txt", 'utf8'), rebuild=False):
		"""rebuild为True时，重建'武将列表'"""
		self._char_dic = {}
		if rebuild:
			self._char_dic = self.__read_characters(characters_filename, cost_filename)
		else:
			self._char_dic = self.__read_gallery(gallery_filename)

		self._sort_list = self._char_dic.keys()
		self.sort('cost')
		if rebuild:
			self.write_characters(gallery_filename)


	def __read_characters(self, characters_filename, cost_filename):
		"""从'各包武将'与'武将价格'读取信息，并初始化"""
		characters = {}
		cost ={}
		pack = ''

		#优先构建价格字典
		with open(cost_filename, 'rb') as csvfile:
			for row in csv.reader(csvfile):
				cost[row[0]] = row[1]

		for line in open(characters_filename, 'r'):
			m1 = re.search(r'.+包|未发售', line)
			if m1:
				pack = m1.group()
			elif re.search(r'^蜀|魏|吴|群|神', line):
				character_name_list_temp = line[6:].rstrip('\n').split("、")
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
				#使用变长参数调用的形式
				characters[row[0]] = Character(*tuple(row))
		return characters

	def write_characters(self, filename):
		"""写回武将列表，一般仅在版本更新时使用"""
		with open(filename, 'wb') as file:
			for name in self._sort_list:
				x = self.get_character(name)
				csv.writer(file).writerow([x.name, x.country, x.pack, x.cost])
		pass

	def buy_characters(self, name_list):
		"""购买一个武将，即修改其价值为'已获得'"""
		for x in name_list:
			self._char_dic[x].cost = '已获得'
		pass

	def get_character_names(self):
		"""返回目前武将集中可见的所有武将名"""
		return self._sort_list

	def get_character_list(self):
		"""返回目前武将集中可见的所有武将信息"""
		return [self.get_character(x) for x in self._sort_list]

	def get_character(self, name):
		"""返回目前武将集中所有武将及所有信息"""
		if name in self._char_dic.keys():
			return self._char_dic[name]
		else:
			return NonCharacter(name)

	def filter(self, func):
		"""按给定条件筛选"""
		self._sort_list = [x.name for x in filter(func, self.get_character_list())]
		new_obj = copy.copy(self)
		self._sort_list = self._char_dic.keys()
		self.sort()
		return new_obj

	def sort(self, sortby='default'):
		"""按照指定列排序"""
		if sortby=='default':
			self._sort_list = [x.name for x in sorted(self.get_character_list(), cmp=Character.cmp_default)]
		elif sortby=='cost':
			self._sort_list = [x.name for x in sorted(self.get_character_list(), cmp=Character.cmp_cost)]
		elif sortby=='cost_reverse':
			self._sort_list = [x.name for x in sorted(self.get_character_list(), cmp=Character.cmp_cost, reverse=True)]
		pass

	def get_regular(self):
		"""返回武将列表的正则表达式"""
		return re.compile("(?<!主公是)(?<!对)("+"|".join(self._sort_list)+"|三英模式.+$)")
pass

# 测试程序
if __name__ == "__main__":
	c = Characters(rebuild=True)
	c = Characters()
	c.get_character_list()
	c.get_character_names()
	c.get_character('孙权')
	c.get_character('姜孟冯')
	c.buy_characters(['SR孙权','SR黄盖', 'SR周瑜','SR马超', 'SR大乔','SR貂蝉', 'SR张飞'])
	c.filter(lambda x:x.cost=='已获得').write_characters(unicode("test/已获得武将列表.txt", 'utf8'))
	c.write_characters(unicode("test/全部武将列表.txt", 'utf8'))
	print "all_complete!!"

from random import randint as rd
from GameMap import GameMap  # 垃圾python


def player_func(map_info, player_id):  # 辅助函数
    ACTIONS = []
    tmp_left = [i.power[player_id] for i in map_info.nodes]

    def isValid(action):
        a, b, c = action
        if map_info.nodes[a].belong != player_id:
            return False
        if b not in map_info.nodes[a].get_next():
            return False
        if tmp_left[a] <= c + 0.01:
            return False
        tmp_left[a] -= c
        return True

    for i in range(1000):
        tmp_action = (rd(1, len(map_info.nodes) - 1),
                      rd(1, len(map_info.nodes) - 1), rd(1, 1000) / 10)
        if isValid(tmp_action):
            ACTIONS.append(tmp_action)

    # 随机出兵
    return ACTIONS


class player_class:  # 格式要求
    def __init__(self, player_id: int):
        self.player_id = player_id

    def view(self, node, map_info):
        nextlst = node.get_next()
        nextempty = []
        nextfri = []
        nextenemy = []
        for id in nextlst:
            if map_info[id].belong == -1:
                nextempty.append(map_info[id])
            elif map_info[id].belong == self.player_id:
                nextfri.append(map_info[id])
            elif map_info[id].belong == 1 - self.player_id:
                nextenemy.append(map_info[id])
        # print(nextempty,nextfri,nextenemy)
        return (nextempty, nextfri, nextenemy)  # 以node为元素的列表

    def frontier(self, node, map_info):
        return len(self.view(node, map_info)[2]) > 0

    def expandable(self, node, map_info):
        return len(self.view(node, map_info)[0]) > 0

    def expand(self, node, map_info):  # 返回这个节点为起点的一切指令
        # 读取一个节点的值
        action = []
        if node.belong == self.player_id:
            print('@')
            info = self.view(node, map_info)
            nextempty = info[0]
            nextfri = info[1]
            nextenemy = info[2]
            if len(nextenemy) == 0:
                if len(nextempty) > 0:
                    free = node.power[self.player_id]-20  # 可调节的,需保证派出兵力大于1
                    if free-len(nextempty) > 0:
                        for nod in nextempty:
                            action.append(
                                (node.number, nod.number, free/len(nextempty)))
                else:
                    free = node.power[self.player_id]-30
                    less = []
                    for nod in nextfri:
                        if nod.power[self.player_id] < 0.8*node.power[self.player_id]:  # 可调参
                            less.append(nod)
                    for nod in less:
                        action.append(
                            (node.number, nod.number, max(free/len(less), 1)))
            else:
                free = node.power[self.player_id]-10  # 可调
                action.append((node.number, nextenemy[0].number, free))
            return action
        else:
            return []

    # 前面的map_info都是列表的意思

    def player_func(self, map_info: GameMap):
        N = map_info.N
        action = []
        # print(map_info.nodes)
        for node in map_info.nodes:
            action = action+self.expand(node, map_info.nodes)[:]
            print(node, self.expandable(node, map_info.nodes))
            print(node, self.frontier(node, map_info.nodes))
        return action

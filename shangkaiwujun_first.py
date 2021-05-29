# import json
from GameMap import GameMap
import config


# 问题：不会集兵，不会集体进攻。。。被打爆了
# 运行一段时间就会死于所有点都是100，然后被打爆

def countScores(nodes: list, N: int, player_id:int) -> list:
    '''
    计算各点重要度权重：1/distance1+1/distance2
    返回列表，各点对应
    '''
    scores = [0]*(N+1)
    scores[1] = 10
    scores[N] = 10
    scores[(N-1)*player_id+1] -= 9
    counting = {1, }
    counted = {1, }
    distance = 1
    while counting:
        newcounting = set()
        for x in counting:
            newcounting.update(
                [y for y in nodes[x].get_next() if y not in counted])
        for x in newcounting:
            scores[x] += 1/(distance)
        distance += 1
        counting = newcounting
        counted.update(newcounting)
    counting = {N, }
    counted = {N, }
    distance = 1
    while counting:
        newcounting = set()
        for x in counting:
            newcounting.update(
                [y for y in nodes[x].get_next() if y not in counted])
        for x in newcounting:
            scores[x] += 1/(distance)
        distance += 1
        counting = newcounting
        counted.update(newcounting)
    for j in range(N) :
        t=nodes[j].get_next()
        for item in t :
            if nodes[item].belong != player_id :
                scores[j] += 1
    return scores


def produce(power: float) -> float:
    '''
    返回新生成兵力，只是重新计算已给函数
    '''
    if power <= config.POWER_LIMIT:
        new = power+power*config.SPAWN_RATE*(1-(power/config.POWER_LIMIT))
    else:
        new = config.POWER_LIMIT+config.SPAWN_RATE*(power-config.POWER_LIMIT)
    return new


def march(power: float) -> float:
    '''
    对于行军返回兵力，只是计算已给函数
    '''
    gain = max(power-power**0.5, 0)
    return gain


def fight(power1: float, power2: float) -> tuple:
    '''
    计算战斗结果，返回tuple(战斗是否胜利，节点剩余人数)
    '''
    if power1 > power2:
        return (True, (power1**2-power2**2)**0.5)
    else:
        return (False, (power2**2-power1**2)**0.5)


def assessFunc(manpowerscore: float, conquerpoint: float, producingscore: float) -> float:
    '''
    加权计算占领的得分与人力得分
    manpower既包括己方加人数，也包括敌方减人数
    '''
    a = 0.025
    b = 1
    c = 0.025
    # 参数待调
    return manpowerscore*a+conquerpoint*b+producingscore*c
# tqy# a和c应该一样大


# def assessMarches(nodes: list, node: int, edges: list, scores: list, player_id: int) -> float:  # player_id:0玩家一 1玩家二
#     '''
#     对每一个点的方式进行评估，输入贪心后可选择的边路径和行军兵力，进行评估分析，返回评估分
#     edges:[(aimnode:int,marchpower:float)]
#     '''
#     manpower = nodes[node].power[player_id]
#     manpowerscore = 0
#     conquerpoint = 0
#     producingscore = -produce(manpower)
#     for edge in edges:
#         aimnode, marchpower = nodes[edge[0]], edge[1]
#         if aimnode.belong == -1:
#             gain = march(marchpower)
#             manpowerscore += gain-marchpower
#             producingscore += produce(gain)
#             conquerpoint += scores[edge[0]]
#         elif aimnode.belong == player_id:
#             gain = march(marchpower)
#             manpowerscore += gain-marchpower
#             producingscore += produce(aimnode.power[player_id] +
#                                       marchpower)-produce(aimnode.power[player_id])
#         else:
#             gain = march(marchpower)
#             aimnodepower = aimnode.power[int(not player_id)]
#             remain = fight(gain, aimnodepower)
#             if remain[0]:
#                 manpowerscore += aimnodepower
#                 manpowerscore += remain[1]-marchpower
#                 conquerpoint += scores[edge[0]]
#                 producingscore += produce(remain[1])+produce(aimnodepower)
#             else:
#                 manpowerscore += aimnodepower-remain[1]
#                 manpowerscore += -marchpower
#                 producingscore += produce(aimnodepower) - produce(remain[1])
#         manpower -= marchpower
#     producingscore += produce(manpower)
#     return assessFunc(manpowerscore, conquerpoint, producingscore)


def assessMarch(nodes: list, node: int, edge: tuple, scores: list, player_id: int) -> float:
    '''
    防止暴毙，先写每一步的贪心
    '''
    # 现在的问题：在重点地方屯兵收益应当更大？怎么做
    manpowerscore = 0
    manpower = nodes[node].power[player_id]
    aimnode, marchpower = nodes[edge[0]], edge[1]
    producingscore = produce(manpower-marchpower)-produce(manpower)
    if aimnode.belong == -1:  # 如果无主
        gain = march(marchpower)
        manpowerscore += gain-marchpower
        producingscore += produce(gain)
        conquerpoint = scores[edge[0]]
    elif aimnode.belong == player_id:  # 如果为自己据点
        gain = march(marchpower)
        manpowerscore += gain-marchpower
        producingscore += produce(aimnode.power[player_id] +
                                  marchpower)-produce(aimnode.power[player_id])
        conquerpoint = 0
    else:  # 战斗
        gain = march(marchpower)
        aimnodepower = aimnode.power[int(not player_id)]
        remain = fight(gain, aimnodepower)
        if remain[0]:  # 如果胜利
            manpowerscore += aimnodepower
            manpowerscore += remain[1]-marchpower
            conquerpoint = scores[edge[0]]
            producingscore += produce(remain[1])+produce(aimnodepower)
        else:  # 如果失败
            manpowerscore += aimnodepower-remain[1]
            manpowerscore += -marchpower
            producingscore += produce(aimnodepower) - produce(remain[1])
            conquerpoint = 0
    return assessFunc(manpowerscore, conquerpoint, producingscore)



def decideMarch(nodes: list, node: int, scores: list, actions: list, player_id: int) -> None:
    '''
    每一步决定后修改nodes内兵力，将现有兵力 k*连结节点 等分，化为有限维，寻找评估最大的行为(理想。。。)
    贪心算法
    注：现有算法：对每一步都贪心。。。每一步的输出兵力少于现有的*a，从占领分最高的开始贪心，贪心方法：b等分???貌似其实可以算。。。
    '''
    k = 2
    a = 0.6
    b = 10
    # 待调参数

    def updateActions(edge: tuple) -> None:
        "将决策加进actions中"
        action = [x for x in range(len(actions)) if (
            actions[x][0] == edge[1] and actions[x][1] == edge[0])]
        if action:
            act_num = action[0]
            if actions[act_num][2] >= edge[2]:
                actions[act_num] = (
                    actions[act_num][0], actions[act_num][1], actions[act_num][2]-edge[2])
            else:
                actions[act_num] = (
                    actions[act_num][1], actions[act_num][0], edge[2]-actions[act_num][2])
        else:
            actions.append(edge)

    next_nodes = nodes[node].get_next()
    next_nodes.sort(key=lambda x: scores[x], reverse=True)
    manpower = nodes[node].power[player_id]
    edges = []
    #tqy# 这个地方的梯度下降仿佛可以完善一下，一次算一个节点应该没问题
    for x in next_nodes:
        power_bin = (manpower*a)/b
        max_point = None
        edge=(0,0,0)
        for y in range(b+1):
            assessPoint = assessMarch(
                nodes, node, (x, power_bin*y), scores, player_id)
            if max_point is None or max_point < assessPoint:
                max_point = assessPoint
                edge = (node, x, power_bin*y)
        if edge[2] != 0:
            edges.append(edge)
        manpower -= edge[2]
    for edge in edges:
        updateActions(edge)


def decideMarches(nodes: list, scores: list, player_id: int, N: int) -> list:
    '''
    对于所有控制点，给出基于decideMarch的总决策
    广搜，给出结果
    '''
    root = 1 if player_id == 0 else N
    counting = {root}
    counted = {root}
    actions = []
    decideMarch(nodes, root, scores, actions, player_id)
    while counting:
        # print(counting)
        newcounting = set()
        for node in counting:
            for newnode in nodes[node].get_next():
                if newnode in counted:
                    continue
                if nodes[newnode].belong == player_id:
                    decideMarch(nodes, newnode, scores, actions, player_id)
                newcounting.add(newnode)
                counted.add(newnode)
        counting = newcounting
    return actions


class player_class:
    def __init__(self, player_id: int):
        self.player_id = player_id

    def player_func(self, map_info: GameMap):
        player_id=self.player_id
        nodes = map_info.nodes[:]
        N = map_info.N
        # print('1')
        scores = countScores(nodes, N , player_id)
        #print("================================================")
        #print(scores)
        #print("========================================")
        actions = decideMarches(nodes, scores, self.player_id, N)
        #print(actions)
        return actions


# 主要问题，完全没有防守，所以产生的结果是对敌方没有预警——增加敌方信息
# 函数形式的优化
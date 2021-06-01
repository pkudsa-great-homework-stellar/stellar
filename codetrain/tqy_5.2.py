# import src.GameMap as GameMap#垃圾python
from GameMap import GameMap


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


class player_class:  # 格式要求
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.strategy = 'expand'
        self.d = None
        self.turn = 0
        self.start_fight = 0
        self.fight_judge = False

    def countScores(self, map_info):
        '''
        计算各点 距离地方老家的 distance
        返回列表，各点对应
        '''
        nodes = map_info.nodes
        distance_list = [0] * (map_info.N + 1)
        if self.player_id == 0:
            counting = {map_info.N, }
            counted = {map_info.N, }
        else:
            counting = {1, }
            counted = {1, }
        distance = 1
        while counting:
            newcounting = set()
            for x in counting:
                newcounting.update(
                    [y for y in nodes[x].get_next() if y not in counted])
                distance_list[x] = distance
            distance += 1
            counting = newcounting
            counted.update(newcounting)
        # print(distance_list)
        return distance_list

    def dis_to_front(self, map_info):
        dic = {}
        front = self.get_front(map_info)
        for id in front:
            dic[id] = 0
        key = list(dic.keys())
        value = [0] * len(key)
        for id in key:
            for jd in map_info.nodes[id].get_next():
                if jd not in key and map_info.nodes[jd].belong == self.player_id:
                    key.append(jd)
                    value.append(dic[id] + 1)
                    dic[jd] = value[-1]
        return dic

    def get_front(self, map_info):
        front = []
        for id in range(1, map_info.N + 1):  # 太阴间了
            if map_info.nodes[id].belong == self.player_id:
                for jd in map_info.nodes[id].get_next():
                    if map_info.nodes[jd].belong != self.player_id:  # 这个是包括空点的
                        front.append(id)
                        break
        return front

    def upgrate_expand(self, map_info):
        nodes = map_info.nodes
        base_front_safe = 20  # 前线留守兵力，初期为10，后期对峙为20
        base_front_danger = most_used
        if self.fight_judge == False:
            for id in range(1, map_info.N + 1):
                if nodes[id].belong == self.player_id:
                    for tip in nodes[id].get_next():
                        if nodes[tip].belong == 1 - self.player_id:
                            self.fight_judge = True
                            self.start_fight = self.turn
        if self.fight_judge == False:
            base_inside = 9  # 生产兵力，初期为10，后期对峙时为50
            base_front_safe = 10  # 前线留守兵力，初期为10，后期对峙为30
        else:
            base_inside = min((self.turn-self.start_fight) * 10 + 9, 50)
        front = self.get_front(map_info)
        dis = self.dis_to_front(map_info)

        action = []
        not_front_nodes = []
        for id in range(1, map_info.N + 1):
            if nodes[id].belong == self.player_id and id not in front:
                not_front_nodes.append(id)
        not_front_nodes.sort(key=lambda x: dis[x], reverse=True)
        for id in not_front_nodes:
            will_come_into = 0
            for edge in action:
                if edge[1] == id:
                    will_come_into += march(edge[2])
            jd_lst = []
            output = 0
            for jd in nodes[id].get_next():
                if dis[jd] == dis[id] - 1:
                    jd_lst.append(jd)
            if nodes[id].power[self.player_id] + will_come_into > base_inside + len(jd_lst):
                output = min(nodes[id].power[self.player_id] + will_come_into -
                             base_inside, nodes[id].power[self.player_id]) - 0.001
            if output > len(jd_lst):
                for jd in jd_lst:
                    action.append((id, jd, output / len(jd_lst)))

        for id in front:
            empty = []
            enemy = []
            # 无敌与有敌区别巨大
            for jd in nodes[id].get_next():
                if nodes[jd].belong == 1 - self.player_id:
                    enemy.append(jd)
                elif nodes[jd].belong == -1:
                    empty.append(jd)
            if len(enemy) == 0:
                will_come_into = 0
                output = 0
                for edge in action:
                    if edge[1] == id:
                        will_come_into += march(edge[2])
                if nodes[id].power[self.player_id] + will_come_into > base_inside + len(empty):
                    output = min(nodes[id].power[self.player_id] + will_come_into - base_inside,
                                 nodes[id].power[self.player_id]) - 0.001
                if output > len(empty):
                    for jd in empty:
                        action.append((id, jd, output / len(empty)))
            elif nodes[id].power[self.player_id] > base_front_danger + 1:
                target = enemy[0]
                for jd in enemy:  # 从多点出击改为避实击虚
                    if nodes[jd].power[1-self.player_id] < nodes[target].power[1-self.player_id]:
                        target = jd
                action.append(
                    (id, target, nodes[id].power[self.player_id] - base_front_safe))
        return action

    def player_func(self, map_info: GameMap):
        self.turn += 1
        self.distance_list = self.countScores(map_info)
        return self.upgrate_expand(map_info)

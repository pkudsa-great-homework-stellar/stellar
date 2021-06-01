import os
import sys
import random
import ast
import json
import time
from multiprocessing import Process
os.chdir(os.path.dirname(__file__))


SRC_PATH = '../src/'
BEDUGGER_PATH = '../debugger/'
sys.path.append(os.path.abspath(SRC_PATH))
sys.path.append(os.path.abspath(BEDUGGER_PATH))

if '初始配置':
    from debuggerCmd import GameWithModule
    from paras import k, parameters, filename, contrast_with_self, N, OUTPUT_File


def match(modules, names, results):
    for x in range(k):
        game = GameWithModule(modules, names, {})
        game.run()
        winner = game.map['winner']
        if winner not in (0, 1):
            continue
        results[winner][0] += 1
        history = game.map['history']
        if len(history) != 100:
            results[1-winner][1] -= 200-len(history)
            results[winner][1] += 200-len(history)
        else:
            end = history[-1][-1]['owner']
            N = len(end)
            score = 100 * \
                (len([x for x in end.items() if x[1] == winner])/N)
            results[winner][1] += score
            results[1-winner][1] -= score


class code():
    def __init__(self, filename: str, parameters: dict, path: str) -> None:
        self.filename = filename
        self.path = path
        self.parameters = parameters
        self.parameters_values = None
        self.random_change()

    def random_change(self):
        dict = {}
        for x in self.parameters.items():
            if x[1][2]:
                dict[x[0]] = int(random.uniform(x[1][0], x[1][1]))
            else:
                dict[x[0]] = random.uniform(x[1][0], x[1][1])
        self.parameters_values = dict

    def copy_file(self):
        return code(self.filename, self.parameters, self.path)

    def create_file(self):
        with open(self.path, encoding='utf-8', errors='ignore') as f:
            file = f.read()

        file = '\n'.join([x[0]+'='+str(x[1])
                          for x in self.parameters_values.items()])+'\n'+file
        tree = ast.parse(file, self.filename)

        # 写入模块
        pack = type(ast)('code(%s)' % self.filename)
        exec(compile(tree, '', 'exec'), pack.__dict__)

        # 检查必要函数
        pack.player_class.player_func

        return pack

    def run(self, other):
        assert isinstance(other, code)
        results = [[0, 0], [0, 0]]
        modules = [self.create_file(), other.create_file()]
        names = [self.filename, other.filename]
        match(modules, names, results)
        results = results[::-1]
        match(modules[::-1], names[::-1], results)
        results = results[::-1]
        return results

    def return_values(self) -> dict:
        return self.parameters_values


class fightsquare():
    def __init__(self, n: int) -> None:
        self.fighters = []
        self.n = n
        self.max_index = None

    def appendfighter(self, fighter: code):
        assert isinstance(fighter, code)
        self.fighters.append(fighter)

    def beginfight(self):
        assert len(self.fighters) == self.n
        scores = []
        for x in range(self.n):
            scores.append([0, 0])
        fight_num = 1
        all_fight_num = (self.n**2-self.n)//2
        start_time = time.time()
        for x in range(1, self.n):
            for y in range(x):
                results = self.fighters[x].run(self.fighters[y])
                scores[x] = list(map(lambda x, y: x+y, scores[x], results[0]))
                scores[y] = list(map(lambda x, y: x+y, scores[y], results[1]))
                now_time = time.time()
                time_used = now_time-start_time
                time_still_need = time_used / \
                    (fight_num/(all_fight_num-fight_num))
                msg = f"=======================PART {fight_num}========================\n"
                msg += f'\tfights_finished:{fight_num}/{all_fight_num}\n'
                msg += f"time_used:{time_used:.3f}s\ttime_still_need:{time_still_need:.3f}s"
                print(msg)
                fight_num += 1
        max_value = scores[0]
        max_index = 0
        for x in range(1, self.n):
            if scores[x][0] > max_value[0] or (scores[x][0] == max_value[0] and scores[x][1] > max_value[1]):
                max_value = scores[x]
                max_index = x
        self.max_index = max_index

    def winner(self) -> code:
        assert self.max_index is not None
        return self.fighters[self.max_index]


if __name__ == '__main__':
    l = len(parameters)
    field = fightsquare(N**l)
    basepath = os.path.dirname(__file__)
    path = os.path.join(basepath, filename)
    # print(path)
    code0 = code(filename, parameters, path)
    field.appendfighter(code0)
    for x in range(N**l-1):
        field.appendfighter(code0.copy_file())
    field.beginfight()
    winner_code = field.winner()
    output_path = os.path.join(basepath, OUTPUT_File)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(winner_code.return_values(), f, ensure_ascii=0)

import os
import sys
import random
import ast
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Manager, Array, Pool, Lock
os.chdir(os.path.dirname(__file__))


SRC_PATH = '../src/'
BEDUGGER_PATH = '../debugger/'
sys.path.append(os.path.abspath(SRC_PATH))
sys.path.append(os.path.abspath(BEDUGGER_PATH))

if '初始配置':
    from debuggerCmd import GameWithModule
    from paras import FILENAME, CONTRAST_WITH_SELF, CONTRAST_FILE, OUTPUT_FILE
    from paras import PARAMETERS
    from paras import N, K, WINNER_IS_KING
    from paras import PRINT_SCORES, SCORES_FILE
    from paras import ANALYZE_SCORES, PRE_ANALYZE
    # 预分析参量：
    PRE_ANALYZE_N = 5


def match(modules: list, names: list, results: list) -> None:
    for x in range(K):
        game = GameWithModule(modules, names, {})
        game.run()
        winner = game.map['winner']
        if winner not in (0, 1):
            continue  # 平局跳过
        results[winner][0] += 1
        results[1-winner][0] -= 1
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

    def run(self, other) -> list:
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
        self.all_fight_num = (self.n**2-self.n)//2
        self.max_index = None
        self.__win_nums = None
        self.__winscores = None

    def appendfighter(self, fighter: code):
        assert isinstance(fighter, code)
        self.fighters.append(fighter)

    def beginfight(self):
        assert len(self.fighters) == self.n
        mgr = Manager()
        win_nums = mgr.list([0]*self.n)
        winscores = mgr.list([0]*self.n)
        fight_num = 1
        pool = Pool()
        start_time = time.time()
        lock = Lock()
        for x in range(1, self.n):
            for y in range(x):
                pool.apply_async(self.fight, args=(
                    win_nums, winscores, start_time, x, y, fight_num, lock))
                # self.fight(win_nums, winscores, start_time,
                #            x, y, fight_num, queue)
                fight_num += 1
        pool.close()
        pool.join()
        win_nums = list(win_nums)
        winscores = list(winscores)
        max_win_num = win_nums[0]
        max_winscore = winscores[0]
        max_index = 0
        for x in range(1, self.n):
            if WINNER_IS_KING:
                if win_nums[x] > max_win_num or (win_nums[x] == max_win_num and winscores[x] > max_winscore):
                    max_win_num = win_nums[x]
                    max_winscore = winscores[x]
                    max_index = x
            else:
                if winscores[x] > max_winscore or (winscores[x] == max_winscore and win_nums[x] > max_win_num):
                    max_win_num = win_nums[x]
                    max_winscore = winscores[x]
                    max_index = x
        self.max_index = max_index
        self.__win_nums = win_nums
        self.__winscores = winscores

    def fight(self, win_nums: Array, winscores: Array, start_time: float, x: int, y: int, fight_num: int, lock: Lock) -> None:
        p_start_time = time.time()
        results = self.fighters[x].run(self.fighters[y])
        lock.acquire()
        win_nums[x] += results[0][0]
        win_nums[y] += results[1][0]
        winscores[x] += results[0][1]
        winscores[y] += results[1][1]
        lock.release()
        now_time = time.time()
        time_used = now_time-start_time
        time_still_needed = (time_used / fight_num) * \
            (self.all_fight_num-fight_num)
        p_used_time = now_time-p_start_time
        msg = f"=======================PART {fight_num} ends========================\n"
        msg += f'\t\tfights finished:{fight_num}/{self.all_fight_num}\n'
        msg += f"time used:{time_used:.3f}s\ttime still needed:{time_still_needed:.3f}s"
        msg += f"pid:{os.getpid()}\tprogram used{p_used_time:.3f}"
        print(msg)

    def winner(self) -> code:
        assert self.max_index is not None
        return self.fighters[self.max_index]

    @property
    def winscores(self):
        assert isinstance(self.__winscores, list)
        return self.__winscores

    @property
    def win_nums(self):
        assert isinstance(self.__win_nums, list)
        return self.__win_nums

    @property
    def scores(self):
        assert isinstance(self.__winscores, list)
        assert isinstance(self.__win_nums, list)
        return {'win_nums': self.__win_nums, 'winscores': self.__winscores}


def makeHistogram(name: str, data: list) -> None:
    n, bins, patches = plt.hist(
        x=data, bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel(name)
    plt.ylabel('Frequency')
    plt.title(name+"-Frequency Histogram")
    maxfreq = n.max()
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    plt.show()


if __name__ == '__main__':
    basepath = os.path.dirname(__file__)
    path = os.path.join(basepath, FILENAME)
    code0 = code(FILENAME, PARAMETERS, path)

    # 预分析
    fight = True
    if PRE_ANALYZE:
        print("\nNOW begins the PRE-ANALYZE:\n")
        field_pre = fightsquare(PRE_ANALYZE_N)
        field_pre.appendfighter(code0)
        for x in range(PRE_ANALYZE_N-1):
            field_pre.appendfighter(code0.copy_file())
        field_pre.beginfight()
        win_nums = field_pre.win_nums
        winscores = field_pre.winscores
        makeHistogram('win_num', win_nums)
        makeHistogram('winscores', winscores)
        winner_code = field_pre.winner()
        values = field_pre.winner().return_values()
        msg = input("\nresult:"+json.dumps(values) +
                    "\ninput 'q' for quit; anything else for continue\n")
        if msg == 'q':
            fight = False

    if fight:
        # 开始对决
        l = len(PARAMETERS)
        field = fightsquare(N**l)
        field.appendfighter(code0)
        for x in range(N**l-1):
            field.appendfighter(code0.copy_file())
        field.beginfight()
        winner_code = field.winner()

        # 开始输出
        os.chdir(os.path.dirname(__file__))
        output_path = os.path.join(basepath, OUTPUT_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(winner_code.return_values(), f, ensure_ascii=0)
            # 输出最佳结果
        if PRINT_SCORES:
            output_path = os.path.join(basepath, SCORES_FILE)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(field.scores, f, ensure_ascii=0)
                # 输出对决结果
        if ANALYZE_SCORES:
            win_nums = field.win_nums
            winscores = field.winscores
            makeHistogram('win_num', win_nums)
            makeHistogram('winscores', winscores)

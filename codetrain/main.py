import os
import sys
import random
import ast
import json
import time
import matplotlib.pyplot as plt
from multiprocessing import Process, Pool, Manager
os.chdir(os.path.dirname(__file__))


SRC_PATH = '../src/'
BEDUGGER_PATH = '../debugger/'
sys.path.append(os.path.abspath(SRC_PATH))
sys.path.append(os.path.abspath(BEDUGGER_PATH))

if '初始配置':
    from debuggerCmd import GameWithModule
    from paras import FILENAME, CONTRAST_WITH_SELF, CONTRAST_FILE, OUTPUT_FILE
    from paras import PARAMETERS
    from paras import N, K, WINNER_IS_KING, PROCESS_LIMITS
    from paras import SAVE_SCORES, SCORES_FILE, SAVE_EVERY_RESULTS
    from paras import ANALYZE_SCORES, SHOW_EVERY_ANALYZE, SAVE_EVERY_ANALYZE
    from paras import PRE_ANALYZE, PRE_ANALYZE_AUTO_SAVE, PRE_ANALYZE_AUTO_SHOW
    from paras import SERVER_MOD, SEND_MAIL, TO_MAILS
    basepath = os.path.dirname(__file__)
    path = os.path.join(basepath, FILENAME)
    name = os.path.splitext(FILENAME)[0]
    output_basepath = os.path.join(basepath, name)
    try:
        os.mkdir(output_basepath)
    except FileExistsError:
        pass
    # 预分析参量：
    PRE_ANALYZE_N = 15


def match(modules, names, results):
    for x in range(K):
        game = GameWithModule(modules, names, {})
        game.run()
        winner = game.map['winner']
        if winner not in (0, 1):
            continue  # 平局跳过
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
    def __init__(self, filename: str, parameters: dict, path: str, randomchange=True) -> None:
        self.filename = filename
        self.path = path
        self.parameters = parameters
        self.parameters_values = None
        if randomchange:
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
    def __init__(self, n: int, processname: str) -> None:
        self.fighters = []  # list of class(code)
        self.n = n
        self.max_index = None
        self.__scores = None
        self.processname = processname

    def appendfighter(self, fighter: code):
        assert isinstance(fighter, code)
        self.fighters.append(fighter)

    def beginfight(self):
        assert len(self.fighters) == self.n
        scores = []  # scores is a list of score:list=[胜利局数，胜利分]
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
                time_still_needed = (time_used / fight_num) * \
                    (all_fight_num-fight_num)
                print(
                    f"===================PART {fight_num} processname:{self.processname}====================")
                print(
                    f'\tfights finished:{fight_num}/{all_fight_num}\tpid:{os.getpid()}')
                print(
                    f"\t    time used:{time_used:.3f}s\ttime still needed:{time_still_needed:.3f}s")
                fight_num += 1
        max_value = scores[0]
        max_index = 0
        for x in range(1, self.n):
            if WINNER_IS_KING:
                if scores[x][0] > max_value[0] or (scores[x][0] == max_value[0] and scores[x][1] > max_value[1]):
                    max_value = scores[x]
                    max_index = x
            else:
                if scores[x][1] > max_value[1] or (scores[x][1] == max_value[1] and scores[x][0] > max_value[0]):
                    max_value = scores[x]
                    max_index = x
        self.max_index = max_index
        self.__scores = scores

    def winner(self) -> code:
        assert self.max_index is not None
        return self.fighters[self.max_index]

    @property
    def scores(self):
        assert isinstance(self.__scores, list)
        return self.__scores

    @property
    def values(self) -> list:
        assert isinstance(self.__scores, list)
        assert self.max_index is not None
        return [x.return_values() for x in self.fighters]

    @property
    def distances(self) -> list:
        assert isinstance(self.__scores, list)
        assert self.max_index is not None
        values = self.values
        max_index = self.max_index
        dict1 = values[max_index]

        def distance(dict2: dict):
            sum = 0
            for x in dict1:
                sum += (dict1[x]-dict2[x])**2
            return sum**0.5
        return [distance(x) for x in values]


def makeScatterPlot(name: str, data: list, distances: list, processname: str, save: bool, show: bool):
    if save or show:
        plt.grid(alpha=0.75)
        plt.xlabel('Distance')
        plt.ylabel(name)
        plt.title(name+"-Distance Scatter Plot\nfrom processname"+processname)
        maxvalue = max(data)
        minvalue = min(data)
        maxdistance = max(distances)
        plt.xlim(xmin=-0.5, xmax=maxdistance*1.1)
        plt.ylim(ymin=minvalue*1.1, ymax=maxvalue*1.1)
        plt.scatter(distances, data, c='#8A2BE2', alpha=0.7, marker='*')
        if save:
            output_path = os.path.join(
                output_basepath, name+"-Distance_Scatter_Plot_"+processname+'.png')
            plt.savefig(output_path, dpi=300)
        if show:
            plt.show()


def core(results, lock, processname: str):
    # 开始对决
    t = time.time()
    code0 = code(FILENAME, PARAMETERS, path)
    l = len(PARAMETERS)
    field = fightsquare(N**l, processname=processname)
    field.appendfighter(code0)
    for x in range(N**l-1):
        field.appendfighter(code0.copy_file())
    field.beginfight()
    winner_code = field.winner()
    time_used = time.time()-t

    # 开始输出
    os.chdir(os.path.dirname(__file__))
    if SAVE_EVERY_RESULTS:
        output_path = os.path.join(
            output_basepath, OUTPUT_FILE+f'_processname{processname}')
        output = winner_code.return_values().copy()
        output['time_used'] = time_used
        output['processname'] = processname
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=0)
    lock.acquire()
    results.append(winner_code.return_values())
    lock.release()
    # 输出最佳结果
    if SAVE_SCORES:
        output_path = os.path.join(
            output_basepath, SCORES_FILE+f'_processname{processname}')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(field.scores, f, ensure_ascii=0)
            # 输出对决结果
    if ANALYZE_SCORES:
        print(
            f"===================Processname:{processname}====================")
        print("                          Analyzing...\n")
        scores = field.scores
        win_num = [x[0] for x in scores]
        winscores = [x[1] for x in scores]
        distances = field.distances
        makeScatterPlot('win num', win_num, distances, processname,
                        SAVE_EVERY_ANALYZE, SHOW_EVERY_ANALYZE)
        makeScatterPlot('winscores', winscores, distances,
                        processname, SAVE_EVERY_ANALYZE, SHOW_EVERY_ANALYZE)


if __name__ == '__main__':
    # 关于服务器模式
    mgr = Manager()
    if SERVER_MOD:
        from log import print_log
        log_lock = Manager().Lock()
        log_stack = mgr.list()
        log = Process(target=print_log, args=(
            log_stack, basepath, name, log_lock))
        print("Run child process 'log'")
        log.start()

        def info(*arg):
            log_lock.acquire()
            log_stack.append(*arg)
            log_lock.release()

        print = info

    code0 = code(FILENAME, PARAMETERS, path)

    # 预分析
    fight = True
    if PRE_ANALYZE:
        print("\nNOW begins the PRE-ANALYZE:\n")
        field_pre = fightsquare(PRE_ANALYZE_N, 'PRE_ANALYZE')
        field_pre.appendfighter(code0)
        for x in range(PRE_ANALYZE_N-1):
            field_pre.appendfighter(code0.copy_file())
        field_pre.beginfight()
        scores = field_pre.scores
        win_num = [x[0] for x in scores]
        winscores = [x[1] for x in scores]
        distances = field_pre.distances
        makeScatterPlot('win_num', win_num, distances,
                        'PRE_ANALYZE', PRE_ANALYZE_AUTO_SAVE, PRE_ANALYZE_AUTO_SHOW)
        makeScatterPlot('winscores', winscores, distances,
                        'PRE_ANALYZE', PRE_ANALYZE_AUTO_SAVE, PRE_ANALYZE_AUTO_SHOW)
        winner_code = field_pre.winner()
        values = field_pre.winner().return_values()
        msg = input("\nresult:"+json.dumps(values)+"\ninput 'q' for quit\n")
        if msg == 'q':
            fight = False
    if fight:
        if PROCESS_LIMITS is None:
            pool = Pool()
        else:
            pool = Pool(PROCESS_LIMITS)
        n = pool._processes
        results = mgr.list()
        lock = mgr.Lock()
        for i in range(n):
            pool.apply_async(func=core, args=(results, lock, str(i)))
        pool.close()
        pool.join()
        print('\nAll processes done\n')
        print(json.dumps(list(results)))
        if n != 1:
            # 终焉之战
            assert len(results) == n
            print('========================FINAL FIGHT========================')
            final = fightsquare(n, 'final')
            for i in range(n):
                x = code(FILENAME, PARAMETERS, path, randomchange=False)
                x.parameters_values = results[i]
                final.appendfighter(x)
            final.beginfight()
            output = final.winner().return_values()
        else:
            output = results[0]

        # 最终输出
        os.chdir(os.path.dirname(__file__))
        output_path = os.path.join(output_basepath, OUTPUT_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=0)
        print("Output Done.")

        if SEND_MAIL:
            # 发邮件
            from mail import zip_dir, sendmail
            output_file = os.path.join(basepath, name+'.zip')
            print("zipping file...")
            os.chdir(basepath)
            b = zip_dir(name, output_file)
            assert b
            print("zipping done.")
            for tomail in TO_MAILS:
                print('sending mail...')
                b = sendmail(tomail, name, json.dumps(output), output_file)
                assert b
            os.remove(output_file)
            print('Mailsending Done.')

    if SERVER_MOD:
        # 结束log进程
        while True:
            if log_stack:
                break
            time.sleep(0.5)
        print("Killed child process 'log'.")
        log.terminate()
        log.join()

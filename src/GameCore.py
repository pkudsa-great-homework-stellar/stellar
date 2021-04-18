from copy import deepcopy
from typing import Optional, Tuple, Any
from GameMap import GameMap
from TimeLimit import time_limit
import json
# 重要约定！！！
PLAYER_1 = 0
PLAYER_2 = 1


class Game:
    def __init__(self, filename1: str, filename2: str, max_time: float, max_turn: int, map_args: dict):
        """
        player's python file should include a function which looks like

        player_func(map: GameMap) -> [Tuple[int, int, float].....]

        when illegal moves are given, player would be considered to make no moves

        :param filename1: player 1's python file
        :param filename2: player 2's python file
        :param max_time: time limitation in seconds
        :param max_turn: maximum turn numbers
        :param map_args: game map's initialization parameters
        """
        self.__max_time = max_time
        self.__map = GameMap(map_args)
        self.__winner = None
        self.__game_end = False
        self.__max_turn = max_turn
        self.__history_map = [self.__map.export_as_dic([],[])]#开局的地图也要记录
        try:
            self.player_func1 = __import__(filename1).player_func
        except:
            # if function is not found, the opposite wins
            self.__winner = 'player2'
            self.__game_end = True

        try:
            self.player_func2 = __import__(filename2).player_func
        except:
            if self.__game_end:
                # both players fail to write a correct function, no one wins
                self.__winner = None
            else:
                self.__winner = 'player1'
                self.__game_end = True

    def next_step(self):
        map_info1 = deepcopy(self.__map)
        map_info2 = deepcopy(self.__map)
        try:
            with time_limit(self.__max_time, "player1"):
                player1_actions = self.player_func1(map_info1,0)
        except Exception:
            print("Player func 1 error!")
            # 这里是否应该捕捉到异常之后直接判负?
            player1_actions = []
        try:
            with time_limit(self.__max_time, "player2"):
                player2_actions = self.player_func2(map_info2,1)
        except Exception:
            print("Player func 2 error!")
            player2_actions = []
        if self.__game_end:
            return
        self.__map.update(player1_actions, player2_actions)

        # 历史地图字典，存入列表
        self.__history_map.append(self.__map.export_as_dic(player1_actions,player2_actions))

        
    def run(self):
        """

        :return: 'player1', 'player2' or None if there is no winner
        """
        for turn in range(self.__max_turn):
            self.next_step()

            #print(self.__map) # 测试代码，记得删
            #print("___________________________________________________________________________")

            if self.__game_end:
                break
            end_early = self.__map.end_early()
            if end_early is not None:
                self.__winner = end_early
                self.__game_end = True
                if self.__winner=="draw":
                    self.__winner = None
                break
        else:
            self.__winner = self.__map.high_score()
        return self.__winner

    def get_history(self):
        return self.__history_map
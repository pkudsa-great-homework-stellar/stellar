# 填写文件名
# 请将文件放在pkudsa.stellar.codetrain文件夹里
FILENAME = 'tqy_5.2.py'
CONTRAST_WITH_SELF = True  # 如果和自己比较，则为true 现在也没写False的情况。。。
CONTRAST_FILE = ''  # 如果上一行为true 则不用填写
OUTPUT_FILE = 'output.json'


# 填写参量
PARAMETERS = {
    'most_used': [40, 65, False],  # 最小值，最大值, 是否必须为整形
    # ...
}


# 对战设置

N = 10
# 对战规模：N**len(parameters)
K = 3
# 每次对决进行2*k次
PROGRAM_LINES = None
# 并行进程数。。。改一种方式，用多个进程跑同样的main代码，然后再进一步考察,None代表取为电脑核数
WINNER_IS_KING = True
# 战胜场数为对比主要方式,为False的话会只比较胜利分


# 输出设置

PRINT_SCORES = False
# 输出分数
SCORES_FILE = 'scores.json'
# 输出分数文件


# 分析设置

ANALYZE_SCORES = True
# 分析结果，并给出分布图
PRE_ANALYZE = True
# 预分析：在给定区域内取15组值进行计算，给出分析结果(大约6分钟)

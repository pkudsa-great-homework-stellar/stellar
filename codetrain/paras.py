from secrets_local import MAIL
# 前置导入，不用管


# 填写文件名
# 请将文件放在pkudsa.stellar.codetrain文件夹里
FILENAME = 'tqy_5.2.py'  # ！！！改文件名！！！
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
PROCESS_LIMITS = None
# 并行进程数。。。改一种方式，用多个进程跑同样的main代码，然后再进一步考察,None代表取为电脑核数
# 若为1 则返回方式与原来相同
WINNER_IS_KING = True
# 战胜场数为对比主要方式,为False的话会只比较胜利分


# 输出设置

SAVE_EVERY_RESULTS = True
# 保存每一个进程的结果
SAVE_SCORES = False
# 保存每一个进程的分数
SCORES_FILE = 'scores.json'
# 保存每一个进程的分数文件


# 分析设置

ANALYZE_SCORES = True
# 分析结果，并给出分布图（每个线程的）
SHOW_EVERY_ANALYZE = False
# 展示每一个分析的结果
SAVE_EVERY_ANALYZE = True
# 保存每一个分析结果


# 预分析设置

PRE_ANALYZE = True
# 预分析：在给定区域内取15组值进行计算，给出分析结果(大约6分钟)
PRE_ANALYZE_AUTO_SAVE = False
# 预分析结果储存
PRE_ANALYZE_AUTO_SHOW = True
# 预分析结果展示


# 服务器设置

SERVER_MOD = False
# 是否用服务器跑
SEND_MAIL = False
# 运算结束发送邮件
TO_MAILS = ['zqi.wong@gmail.com', 'zqi_wong@163.com']
# 接收者

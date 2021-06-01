# 填写文件名
# 请将文件放在pkudsa.stellar.codetrain文件夹里
filename = 'tqy_5.2.py'
contrast_with_self = True  # 如果和自己比较，则为true 现在也没写False的情况。。。
contrast_file = ''  # 如果上一行为true 则不用填写
OUTPUT_File = 'output.json'
# 填写参量
parameters = {
    'most_used': [40, 65, False],  # 最小值，最大值, 是否必须为整形
    # ...
}
# 对战设置
N = 15
# 对战规模：N**len(parameters)
k = 3
# 每次对决进行2*k次

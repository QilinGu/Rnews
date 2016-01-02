'''
   Created by suemi on 16/1/2.
   summary:随机切割数据库
'''

import sys,os
sys.path.append(".")
from utils.DBUtil import DBUtil


from optparse import OptionParser

option_0 = { 'name' : ('-m', '--method'), 'help' : '选取切割的方法,按时间或随机比例切割', 'nargs' : 1 }
option_1 = { 'name' : ('-r', '--ratio'), 'help' : '选取切割数据的比例', 'nargs' : 1 }
option_2 = { 'name' : ('-d', '--day'), 'help' : '选取前n天的记录作为训练数据', 'nargs' : 1 }
options=[option_0,option_1,option_2]


def main(options, arguments):
    method=options.method if options.method else "day"
    if method=="day":
        day=int(options.day) if options.day else 20
        DBUtil.splitByClickedDate(day)
    elif method=="random":
        ratio=int(options.ratio) if options.ratio else 0.8
        DBUtil.randomSplit(ratio)
    else:
        print("请选择合适的切割方法!")

if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
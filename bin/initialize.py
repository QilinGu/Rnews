'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 初始化工作，将文件的内容写入数据库
@author: suemi
'''
import sys,os
sys.path.append(".")
from optparse import OptionParser
from utils.DBUtil import DBUtil


option_0 = { 'name' : ('-s', '--start'), 'help' : '选择处理的起始位置', 'nargs' : 1 }
option_1 = { 'name' : ('-e','--end'), 'help' : '选择处理的结束位置', 'nargs' : 1 }

options=[option_0,option_1]

def main(options,arguments):
    start=int(options.start) if options.start else 0
    end=int(options.end) if options.end else 1000000
    if len(arguments)==0:
        print("请务必选择原始数据文件的路径!")
        return
    filePath=arguments[0]
    DBUtil.dumpRawData(filePath, start, end)
    
    
if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 执行分词流程
@author: suemi
'''

import sys,os
sys.path.append(".")
from optparse import OptionParser
from utils.WordExtractor import ExMode, WordExtractor

option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择分词的算法', 'nargs' : 1 }
option_1 = { 'name' : ('-n', '--num'), 'help' : '提取的关键词个数', 'nargs' : 1 }

options=[option_0,option_1]

def main(options,arguments):
    method=ExMode(options.method) if options.method else ExMode.TFIDF
    topK=20 if not options.num else int(options.num)
    extractor=WordExtractor()
    extractor.config("mode", method)
    extractor.config("topK",topK)
    extractor.process()
    
if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
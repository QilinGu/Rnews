'''
   Created by suemi on 16/1/2.
'''

import sys,os
sys.path.append(".")
from utils.DBUtil import DBUtil


from optparse import OptionParser

option_0 = { 'name' : ('-r', '--ratio'), 'help' : '选取切割数据的比例', 'nargs' : 1 }
options=[option_0]


def main(options, arguments):
    ratio=int(options.ratio) if options.ratio else 0.8
    DBUtil.randomSplit(ratio)


if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
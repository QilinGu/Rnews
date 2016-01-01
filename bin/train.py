'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 训练用户模型，对于当前来说就是寻找用户的friends
@author: suemi
'''

import sys,os
sys.path.append(".")
from optparse import OptionParser
from core.Trainer import TrainerCategory, TrainerFactory

option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择训练器类型', 'nargs' : 1 }
option_1 = { 'name' : ('-n', '--num'), 'help' : '设定参数数量', 'nargs' : 1 }

options=[option_0,option_1]

def main(options,arguments):
    method=TrainerCategory(options.method) if options.method else TrainerCategory.FRIEND
    num=int(options.num) if options.num else 10
    trainer=TrainerFactory.getTrainer(method)
    trainer.config(num)
    trainer.onUpdate()
    trainer.trainAll()
    
if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)

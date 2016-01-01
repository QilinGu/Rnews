'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 1. 对语料进一步分析，抽取新闻特征 2.抽取文章特征后，可以抽取用户特征
@author: suemi
'''
import sys,os
sys.path.append(".")
from optparse import OptionParser
from utils.CorpusHandler import TopicMethod, CorpusHandler
from core.Provider import Category, UFCategory, ProviderFactory

option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择语料分析的算法', 'nargs' : 1 }
option_1 = { 'name' : ('-n', '--num'), 'help' : '提取的主题个数', 'nargs' : 1 }
option_2 = { 'name' : ('-o', '--operation'), 'help' : '指定进行的操作提取用户特征还是文章特征', 'nargs' : 1 }

options=[option_0,option_1,option_2]

def main(options,arguments):
    operation=Category(options.operation) if options.operation else Category.ARTICLE
    if operation==Category.ARTICLE:
        method=TopicMethod.LDA if not options.method else TopicMethod(options.method)
        num=20 if not options.num else int(options.num)
        hanler=CorpusHandler()
        hanler.process(method,num)
    elif operation==Category.USER:
        method=UFCategory.INTEREST if not options.method else UFCategory(options.method)
        provider=ProviderFactory.getProvider(method,operation)
        provider.onUpdate()
        provider.provideAllFromCompute()

        
if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)


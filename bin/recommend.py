'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 执行推荐过程
@author: suemi
'''
import sys,os
sys.path.append(".")
from optparse import OptionParser
from core.Recommender import BaseRecommender
from core.Predictor import PredictorCategory
from utils.DBUtil import DBUtil


option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择推荐使用的算法', 'nargs' : 1 }
option_1 = { 'name' : ('-n', '--num'), 'help' : '给用户推荐的新闻数目', 'nargs' : 1 }
options=[option_0,option_1]

def main(options,arguments):
    method=PredictorCategory(options.method) if options.method else PredictorCategory.SIM
    topK=int(options.num) if options.num else 3
    recommender=BaseRecommender(topK=topK)
    recommender.select(method)
    recommendation=recommender.recommendAll()
    DBUtil.dumpRecommendation(recommendation)
        
    
if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
'''
Created on 2015年12月10日
@warning: 请务必在命令行添加选项参数，以支持不同方法的处理流程
@summary: 执行推荐过程
@author: suemi
'''
import sys,os

sys.path.append(".")
from core.Recommender import RecommenderCategory, RecommenderFactory


from utils.CacheUtil import CacheUtil


from optparse import OptionParser
from core.Predictor import PredictorCategory
from utils.DBUtil import DBUtil


option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择推荐使用的算法', 'nargs' : 1 }
option_1 = { 'name' : ('-n', '--num'), 'help' : '给用户推荐的新闻数目', 'nargs' : 1 }
options=[option_0,option_1]

def main(options,arguments):
    method=RecommenderCategory(options.method) if options.method else RecommenderCategory.CONTENT
    topK=int(options.num) if options.num else 5
    recommender=RecommenderFactory.getRecommender(method)
    recommender.topK=topK
    recommendation=recommender.recommendAll()
    CacheUtil.dumpRecommendation(recommendation)
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
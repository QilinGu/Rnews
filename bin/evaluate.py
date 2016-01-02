'''
   Created by suemi on 16/1/2.
   @summary:基于数据库中的推荐结果评分
'''
import sys,os
sys.path.append(".")
from optparse import OptionParser

from core.Evaluator import Metric, BaseEvaluator
from core.Recommender import RecommenderFactory
from model.Entity import Record


option_0 = { 'name' : ('-m', '--method'), 'help' : '请选择评价的指标', 'nargs' : 1 }
options=[option_0]

def main(options,arguments):
    method=Metric(options.method) if options.method else Metric.ALL
    evaluator=BaseEvaluator()
    print("Train Data Size: "+str(Record.objects(isTrain=True).count()))
    print("Test Data Size: "+str(Record.objects(isTrain=False).count()))
    if method==Metric.PRECISION:
        precision=evaluator.precision()
        print("precision: "+str(precision))
    elif method==Metric.RECALL:
        recall=evaluator.recall()
        print("recall: "+str(recall))
    elif method==Metric.COVERAGE:
        coverage=evaluator.coverage()
        print("coverage: "+str(coverage))
    elif method==Metric.ALL:
        precision=evaluator.precision()
        print("precision: "+str(precision))
        recall=evaluator.recall()
        print("recall: "+str(recall))
        coverage=evaluator.coverage()
        print("coverage: "+str(coverage))
    else:
        print("请选择合法的检验指标")


if __name__=='__main__':
    parser=OptionParser()
    for option in options:
        param = option['name']
        del option['name']
        parser.add_option(*param, **option)

    options,arguments=parser.parse_args()
    sys.argv[:]=arguments
    main(options, arguments)
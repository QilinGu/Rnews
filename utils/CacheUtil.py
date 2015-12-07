'''
Created on 2015年12月5日

@author: suemi
'''
from utils.CorpusHandler import CorpusMode, TopicMethod
from gensim import corpora
class CacheUtil:
    dataPath="/Volumes/MAC/Rnews/data/"
    dictionaryPath=CacheUtil.dataPath+"rnews.dict"
    corpusPath=CacheUtil.dataPath+"corpus.mm"
    topicPath=CacheUtil.dataPath+"topic.mm"
        
    @staticmethod
    def loadDictionary():
        return corpora.dictionary.Dictionary.load(CacheUtil.dictionaryPath)
    
    @staticmethod
    def loadCorpus(mode=CorpusMode.Mm):
        corpus=None
        CacheUtil.corpusPath=CacheUtil.dataPath+"corpus."+mode
        if mode==CorpusMode.Mm:
            corpus=corpora.MmCorpus(CacheUtil.corpusPath)
        elif mode==CorpusMode.Blei:
            corpus=corpora.BleiCorpus(CacheUtil.corpusPath)
        elif mode==CorpusMode.Low:
            corpus=corpora.LowCorpus(CacheUtil.corpusPath)
        elif mode==CorpusMode.SVMLight:
            corpus=corpora.SvmLightCorpus(CacheUtil.corpusPath)
        return corpus
    
    @staticmethod
    def dumpDictionary(dictionary):
        dictionary.save(CacheUtil.dictionaryPath)
    
    @staticmethod
    def dumpCorpus(corpus,mode=CorpusMode.Mm):
        CacheUtil.corpusPath=CacheUtil.dataPath+"corpus."+mode
        if mode==CorpusMode.Mm:
            corpora.MmCorpus.serialize(CacheUtil.corpusPath,corpus)
        elif mode==CorpusMode.Blei:
           corpora.BleiCorpus.serialize(CacheUtil.corpusPath,corpus)
        elif mode==CorpusMode.Low:
           corpora.LowCorpus.serialize(CacheUtil.corpusPath,corpus)
        elif mode==CorpusMode.SVMLight:
            corpora.SvmLightCorpus.serialize(CacheUtil.corpusPath,corpus)
        
    
    @staticmethod
    def dumpTopic(corpus,method=TopicMethod.LDA):
        CacheUtil.topicPath=CacheUtil.dataPath+method+".mm"
        corpora.MmCorpus.serialize(CacheUtil.topicPath,corpus)
        
    @staticmethod
    def loadTopic(method=TopicMethod.LDA):
        CacheUtil.topicPath=CacheUtil.dataPath+method+".mm"
        return corpora.MmCorpus(CacheUtil.topicPath)
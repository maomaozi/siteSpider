#coding=utf-8
from numpy import *
import time
import jieba
import config as cfg

global instance
instance = None

#将文字矩阵转换为不重复的向量
def creatVacabList(dataSet):
    vacabSet = set([])
    for document in dataSet:
        vacabSet = vacabSet | set(document)
    return list(vacabSet)

#文档向量化，这里是词袋模型，不只关心某个词条出现与否，还考虑该词条在本文档中的出现频率
def vacabWord2list(vacabList, inputSet):
    returnVac = [0] * len(vacabList) #初始化长度为n的list

    for word in inputSet:
        if word in vacabList:
            returnVac[vacabList.index(word)] += 1
    return returnVac

# vacabList改为map形式加速查询, inputSet改为可迭代对象
def vacabWord2list2(vacabMap, inputList):
    returnVac = [0] * len(vacabMap) #初始化长度为n的list
    for word in inputList:
        if word in vacabMap:
            returnVac[vacabMap[word]] += 1
    return returnVac

# 加载数据
def loadFile(start,end):
    docList = []
    classList = []
    #0负类，1正类，2中性类
    for i in range(start, end+1):
        wordList = textParse(open('neutral/%d.txt' % i, mode='r').read().decode('gbk').encode('utf-8'))
        docList.append(wordList)
        classList.append(2)

        wordList = textParse(open('positive/%d.txt' % i, mode='r').read().decode('gbk').encode('utf-8'))
        docList.append(wordList)
        classList.append(1)

        wordList = textParse(open('negative/%d.txt' % i, mode='r').read().decode('gbk').encode('utf-8'))
        docList.append(wordList)
        classList.append(0)
    return docList,classList

#中文分词
stopWords = set(open(cfg.bayes_model_dir + "stop_words.txt", 'r').read().decode('gbk').encode('utf-8').split("\n"))

def textParse(bigString):
    import re
    global stopWords
    inputData = "".join(re.findall(ur'[\u4e00-\u9fa5]+', bigString))#过滤掉输入数据中的所有非中文字符
    wordList = "/".join(jieba.cut(inputData))#完成对中文的分词, 默认模式
    listOfTokens = wordList.split("/")
    stopList = [tok for tok in listOfTokens if (tok not in stopWords and len(tok) >= 2)]
    # 往往会存在大量长度为1的词（不在停用词表里），这些词对特征表示同样贡献不大，利用len(tok) >= 2将其过滤掉
    return stopList

#训练朴素贝叶斯
def trainNB1(trainMatrix,trainCategory,lableNum,vocabLen):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pNum =  1.0*ones((numWords,lableNum))
    pDenom = ones(lableNum)
    classNum = zeros(lableNum)
    for i in range(numTrainDocs):
        for j in range(lableNum):
            if trainCategory[i] == j:
               pNum[:,j] += trainMatrix[i]
               pDenom[j] += sum(trainMatrix[i])

    pVect = log(pNum/(pDenom+vocabLen))#加一平滑的分母为 总单词数
    pAbusive = 1.0 * zeros(lableNum)
    for j in range(lableNum):
        classNum[j] = sum(trainCategory == j)
    pAbusive = classNum/float(numTrainDocs)
    savez(cfg.bayes_model_dir + "parameter.npz", pVect, pAbusive, pNum,pDenom,classNum)
    return pVect,pAbusive

#分类
def classfyNB(currentVer, pVect, pAbusive):
    lableNum = len(pAbusive)
    pro = zeros(lableNum)
    pro = dot(currentVer.T, pVect) + log(pAbusive)
    maxIndex = argmax(pro)
    return maxIndex

#分词训练
def spamTrain(start,end):
    docList, classList = loadFile(start,end)
    #将文字转换为不重复的向量
    vocabList = creatVacabList(docList)
    #训练集
    trainingSet = list(range(len(classList)))
    trainMat = []
    trainClass = []
    for docIndex in trainingSet:
        trainMat.append(vacabWord2list(vocabList,docList[docIndex]))
        trainClass.append(classList[docIndex])

    pVect, pAbusive = trainNB1(array(trainMat),array(trainClass),3,len(vocabList))
    # pVectDict = {}
    # for i in range(len(vocabList)):
    #     pVectDict[vocabList[i]] = {'0': pVect[i,0],'1': pVect[i,1],'2':pVect[i,2]}
    savez(cfg.bayes_model_dir + "vocabList.npz",vocabList)
    return  pVect, pAbusive,vocabList

#测试正确率
def spamTest():
    data = load(cfg.bayes_model_dir + 'parameter.npz')
    pVect = data["arr_0"]
    pAbusive = data["arr_1"]
    vocabList = list(load(cfg.bayes_model_dir + 'vocabList.npz')["arr_0"])
    docList, classList = loadFile(1, 40)
    testSet = list(range(len(classList)))
    #测试
    errorCount = 0
    for docIndex in testSet:
        currentMat = vacabWord2list(vocabList, docList[docIndex])
        curretnClass = classfyNB(array(currentMat),pVect,pAbusive)
        if curretnClass != classList[docIndex]:
            print("当前%d,test:%d:fact%d"%(docIndex, curretnClass, classList[docIndex]))
            errorCount+=1
    print("error is %f" % (errorCount / float(len(testSet))))

class test():
    def __init__(self):
        self.data = load(cfg.bayes_model_dir + 'parameter.npz')
        self.pVect = self.data["arr_0"] #每个类别的条件概率
        self.pAbusive = self.data["arr_1"]#每个类别所占比例
        self.pNum = self.data["arr_2"]
        self.pDemo = self.data["arr_3"]
        self.vocabMap = dict()#词汇表
        self.classNum = self.data["arr_4"]#每个类别的个数
        self.documentNum = sum(self.classNum)#所有文档个数
        self.vocabList = list(load(cfg.bayes_model_dir + 'vocabList.npz')["arr_0"])
        for i in range(len(self.data["arr_2"])):
            # K : V ==  word : index == self.data["arr_2"][i] : i
            self.vocabMap[self.vocabList[i]] = i

    def contextTest(self, str):
        wordList = textParse(str)
        currentMat = vacabWord2list2(self.vocabMap, wordList)
        curretnClass = classfyNB(array(currentMat), self.pVect, self.pAbusive)
        return curretnClass

    def learning(self,text,lable):
        lableNum = len(self.pAbusive)#当前有多少类
        wordList = textParse(text)#分割字符串
        currentMat = vacabWord2list2(self.vocabMap, wordList)#将字符串转换为01矩阵
        #更新参数进行分类
        #新词出现的个数，用于平滑
        newWordList = set([tok for tok in wordList if (tok not in self.vocabMap and len(tok) >= 2)])
        newWordLen = len(newWordList)
        wordListLen= len(wordList)
        dictlength = len(self.vocabMap)
        #     #更新每个类别所占比例
        self.pAbusive = self.documentNum*self.pAbusive/(1.0+self.documentNum)
        pVect = 1.0 * ones((dictlength+newWordLen, lableNum))
        pNum = 1.0 * ones((dictlength+newWordLen, lableNum))
        for j in range(lableNum):
            if j == lable:
                # 更新类别比例
                self.pAbusive[j] += 1/(1.0+self.documentNum)
                #更新旧词频率
                self.pNum[:, lable] += currentMat
                self.pDemo[lable] += sum(currentMat)
                pVect[:len(self.pNum),lable] = log(self.pNum[:,lable]/(self.pDemo[lable]+dictlength+newWordLen))
                #更新新词频率
                pVect[len(self.pNum):,lable] = log(pVect[len(self.pNum):,lable]/(self.pDemo[lable]+dictlength+newWordLen))
                self.classNum[j]+=1
            else:
                #更新对立类的频率
                pVect[:len(self.pNum), j] = log(self.pNum[:, j] / (self.pDemo[j] + dictlength + newWordLen+wordListLen))
                pVect[len(self.pNum):, j] = log(pVect[len(self.pNum):,j] / (self.pDemo[j] + dictlength + newWordLen+wordListLen))
        pNum[:len(self.pNum),:] = self.pNum
        self.vocabList += newWordList
        for i in range(newWordLen):
            self.vocabMap[self.vocabList[i+dictlength]] = i+dictlength
        del self.pVect
        self.pVect = pVect
        del self.pNum
        self.pNum = pNum
        savez(cfg.bayes_model_dir + "vocabList.npz", self.vocabList)
        savez(cfg.bayes_model_dir + "parameter.npz", self.pVect, self.pAbusive, self.pNum, self.pDemo, self.classNum)

    def testLearning(self):
        docList, classList = loadFile(21, 40)
        testSet = list(range(len(classList)))
        # 测试
        errorCount = 0
        for docIndex in testSet:
            self.learning(docList[docIndex], classList[docIndex])

def get_instance():
    global instance
    if instance is None:
        instance = test()
    return instance
if __name__ == '__main__':
    # str = open('test.txt', mode='r').read().decode('gbk').encode('utf-8')
    spamTrain(1,40)
    # r = get_instance()
    # strnum = '1'
    #
    # r.learning(str,int(strnum))
    # r.testLearning()
    # spamTest()

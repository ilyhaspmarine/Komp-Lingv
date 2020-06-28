from DBContext import *
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.ml.feature import Word2Vec

class W2VTrainer:

    def __init__(self):
        os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3"

    def __prepare(self):
        db = DBContext()
        news = db.get_news()
        text = ''
        for item in news:
            text += item + '\n'
        with open('./w2v.txt', 'w', encoding='utf-8') as f:
            f.write(text)

    def train(self):

        self.__prepare()

        spark = SparkSession\
            .builder\
            .appName("Kursach")\
            .getOrCreate()

        input_file = spark.sparkContext.textFile('./w2v.txt')

        # print(input_file.collect())
        prepared = input_file.map(lambda x: ([x]))
        df = prepared.toDF()
        prepared_df = df.selectExpr('_1 as text')

        tokenizer = Tokenizer(inputCol='text', outputCol='words')
        words = tokenizer.transform(prepared_df)

        stop_words = StopWordsRemover.loadDefaultStopWords('russian')
        remover = StopWordsRemover(inputCol='words', outputCol='filtered', stopWords=stop_words)
        filtered = remover.transform(words)

        # print(stop_words)

        # filtered.show()

        # words.select('words').show(truncate=False, vertical=True)

        # filtered.select('filtered').show(truncate=False, vertical=True)

        vectorizer = CountVectorizer(inputCol='filtered', outputCol='raw_features').fit(filtered)
        featurized_data = vectorizer.transform(filtered)
        featurized_data.cache()
        vocabulary = vectorizer.vocabulary

        # featurized_data.show()

        # featurized_data.select('raw_features').show(truncate=False, vertical=True)

        # print(vocabulary)

        idf = IDF(inputCol='raw_features', outputCol='features')
        idf_model = idf.fit(featurized_data)
        rescaled_data = idf_model.transform(featurized_data)

        self.__word2Vec = Word2Vec(vectorSize=3, minCount=0, inputCol='words', outputCol='result')
        self.__model = self.__word2Vec.fit(filtered)
        w2v_df = self.__model.transform(words)
        w2v_df.show()
        spark.stop()

    def get_syn(self, src):
        self.__model.findSynonyms(src, 10).show()


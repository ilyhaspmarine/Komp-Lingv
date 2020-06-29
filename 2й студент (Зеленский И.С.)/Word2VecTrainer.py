from DBContext import *
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import Word2Vec
from pyspark.ml.feature import CountVectorizer
import string
import re

class W2VTrainer:

    def __init__(self):
        self.__model = None
        self.__word2Vec = None
        os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3"

    # Удаление пунктуации из текста
    def __remove_punctuation(sel, text):
        return text.translate(str.maketrans('', '', string.punctuation))

    # Удаление разрыва строк из текста
    def __remove_linebreaks(self, text):
        return text.strip()

    def __prepare(self):
        db = DBContext()
        news = db.get_news()
        text = ''
        for item in news:
            text += item + '\n'
        with open('./w2v.txt', 'w', encoding='utf-8') as f:
            f.write(text)

    def __get_only_words(self, tokens):
        return list(filter(lambda x: re.match(r'[а-яА-Я]+', x), tokens))

    def train(self):

        self.__prepare()

        spark = SparkSession\
            .builder\
            .appName("Kursach")\
            .getOrCreate()

        input_data = spark.sparkContext.textFile('./w2v.txt')

        prepared = input_data.map(lambda x: [x])\
            .map(lambda x: (self.__remove_linebreaks(x[0]), '1'))\
            .map(lambda x: (self.__remove_punctuation(x[0]), '1'))
        prepared_df = prepared.toDF().selectExpr('_1 as text')

        tokenizer = Tokenizer(inputCol='text', outputCol='words')
        words = tokenizer.transform(prepared_df)

        filtered_words_data = words.rdd.map(lambda x: (x[0], self.__get_only_words(x[1])))
        filtered_df = filtered_words_data.toDF().selectExpr('_1 as text', '_2 as words')

        stop_words = StopWordsRemover.loadDefaultStopWords('russian')
        remover = StopWordsRemover(inputCol='words', outputCol='filtered', stopWords=stop_words)
        filtered = remover.transform(filtered_df)

        self.__word2Vec = Word2Vec(vectorSize=3, minCount=0, inputCol='filtered', outputCol='result')
        self.__model = self.__word2Vec.fit(filtered)
        w2v_df = self.__model.transform(filtered)
        w2v_df.show()
        spark.stop()

    def get_syn(self, src):
        print(src + '\n')
        self.__model.findSynonyms(src, 10).show()


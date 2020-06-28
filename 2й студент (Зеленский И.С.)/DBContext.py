from pymongo import MongoClient


class DBContext:
    def __init__(self):
        client = MongoClient('192.168.1.103', 27314)
        self.__db = client['NewsDataBase']
        # print(self.__db['News_parse'].find().count())

    def get_news(self):
        raw = self.__db['News_parse'].find()
        news = [i['Текст статьи'] for i in raw]
        raw.close()
        return news

    def insert_refs(self, refs):
        self.__db['News_analyse'].remove({})
        self.__db['News_analyse'].insert_many(refs)


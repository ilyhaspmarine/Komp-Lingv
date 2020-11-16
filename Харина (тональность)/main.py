import pymorphy2
import re
from gensim.models import Word2Vec
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier


def normalize_new(new_text):
    """
    обработка исходного текста input_data с помощью pymorphy2
    """
    morph = pymorphy2.MorphAnalyzer()
    if new_text is not None:
        allowed = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'NPRO', 'INFN']
        input_words = re.split(r'[^А-Яа-я]+', new_text)
        output_data = []
        for word in input_words:
            p = morph.parse(word)[0]
            if p.tag.POS in allowed:
                output_data.append(p.normal_form)
        return output_data

def normalize_news():
    """
    нормализация новостей
    """
    print('Получение новостей...')
    news = read_file('news.csv')
    result = {'ttext':[]}
    print('Нормализация новостей...')
    for new in news:
        normalized = normalize_new(new['ttext'])
        if (len(normalized) != 0):
            result['ttext'].append(' '.join(normalized))
    return (result['ttext'])


def read_file(filename):
    """
    чтение исходного текста из файла с именем filename
    """
    if filename is None or len(filename) == 0:
        print('\nERROR! Не задано имя файла\n')
    else:
        try:
            with open(filename, 'r') as f:
                return pd.read_csv(filename,';').to_dict('records')
        except OSError:
            print('\nERROR! Файл не найден\n')

def load_model(name):
    """
    загрузка модели с именем name
    """
    model = None
    if (name is None or len(name) == 0):
        print('\nERROR! Не задано имя модели\n')
    else:
        try:
            model = Word2Vec.load(name)
            print('Модель загружена')
        except OSError:
            print('\nERROR! Модель не найдена\n')
        if model is not None:
            return model

def word_vector(model, word):
    """
    векторная форма слова word
    """
    try:
        return model.wv[word]
    except KeyError:
        return None

def words_vectors(model, text):
    '''
    список векторов слов для нормализованного текста
    '''
    words = re.split(r'\s+',text)
    words_vectors = []
    for word in words:
        vector = word_vector(model, word)
        if vector is not None:
            words_vectors.append(vector)
    return words_vectors

def mean_vector(words_vectors):
    '''
    вектор (средний)
    '''
    mean_vector = []
    if (len(words_vectors) != 0):
        length = len(words_vectors[0])
        for j in range(length):
            summ = 0
            for vector in words_vectors:
                summ += vector[j]
            mean_vector.append(summ/length)
    return mean_vector

def main():
    print('Start')
    W2V_model = load_model('VM_Model')
    twits = read_file('normalized.csv')
    x = []#текст обучающего твитта
    y = []#тип обучающего твитта
    a = []#текст новости
    for twit in twits:#обучающие твитты
        vector = mean_vector(words_vectors(W2V_model, twit['ttext'])) #
        if (len(vector) != 0):
            x.append(vector)
            y.append(twit['ttype'])

    news = normalize_news() #нормальзиванные новости
    for new in news:
        vector_news = mean_vector(words_vectors(W2V_model, new))  # вектор нормализованных новостей
        if (len(vector_news) != 0):
            a.append(vector_news)


    training_length = round(len(x) * 0.2)
    predict_length = len(a)
    training_x = x[:training_length]
    training_y = y[:training_length]
    model = KNeighborsClassifier(n_neighbors=3)
    print('Установка модели...')
    model.fit(training_x,training_y)
    print('Предсказание...')
    predicted_news = model.predict(a)
    for i in range(predict_length):
        print('Для', i, 'новости предсказанное значение тональности', predicted_news[i])
        if (predicted_news[i] == 1):
            print('Это означает, что новость позитивная')
            print('---------------------------------')
        else:
            print('Это означает, что новость негативная')
            print('---------------------------------')


main()


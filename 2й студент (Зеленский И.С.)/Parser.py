from DBContext import *
import os
import shutil
import xml.etree.ElementTree as ET

# import subprocess


class Parser:

    def __init__(self):
        self.__db = DBContext()

    def go_parse(self):
        news = self.__db.get_news()
        print('data received...')
        shutil.rmtree('./input')
        os.mkdir('./input')
        i = 1
        for item in news:
            with open('./input/' + str(i) + '.txt', 'w', encoding='utf-8') as f:
                f.write(str(item))
                f.close()
                i += 1
        print('running tomita...')
        self.__run_tomita()
        print('processing xml...')
        result = self.__process_xml()
        # print(len(result))
        self.__db.insert_refs(result)
        shutil.rmtree('./input')
        os.mkdir('./input')

    def __run_tomita(self):
        # if 1 == 2:
        os.system('./tomita-parser ./tomita/config.proto')
        # else:
            # subprocess.run(['tomitaparser.exe', './tomita/config.proto'])

    def __process_xml(self):
        tree = ET.parse('./output/output.xml').getroot()
        res = {}
        for fact in tree.findall('document/facts'):
            if fact.find('Place/Place') is not None:
                place = fact.find('Place/Place').attrib.get('val').lower()
                text = fact.find('Place/Text').attrib.get('val').lower()
                if place in res.keys():
                    res[place].append(text)
                else:
                    res[place] = []
                    res[place].append(text)
            if fact.find('Person/Person') is not None:
                person = fact.find('Person/Person').attrib.get('val').lower()
                text = fact.find('Person/Text').attrib.get('val').lower()
                if person in res.keys():
                    res[person].append(text)
                else:
                    res[person] = []
                    res[person].append(text)
        result = []
        for key in res.keys():
            item = {}
            item['Упоминается'] = key
            item['Упоминания'] = res[key]
            result.append(item)
        return result

#!/usr/bin/env python
import nltk
import re
import string
import json


def read_file(name):
    """ функция для чтения из файла """
    with open(name) as fl:
        return fl.readlines()


class LineHandler:
    """ класс для выполнения задания по обработке"""

    def __init__(self, line):
        self.inf_dict = {}
        self.line = line                                                    # входная строка
        self.inf_dict['body'] = ''                                          # словарь содержащий требуемые поля
        self.inf_dict["metadata"] = []
        self.inf_dict['body_tags'] = []
        self.inf_dict['orphan_tokens'] = []

    def explore(self):

        dog_index = self.line.rfind('@') + 1
        self.inf_dict["metadata"].append(self.line[dog_index:-3])            # нахожу [@...]

        self.line = self.line[:dog_index-4]
        self.inf_dict['body'] = self.line                                    # заполняю body
        clean_line = self.remove_words(r'[\$]\w+', self.line)                # удаляю долларовые слова

        self.inf_dict['body_tags'] = re.findall(r'[\#\@](\w+)', clean_line)  # зплняю body_tags очищаю строку
        clean_line = self.remove_words(r'[\#\@](\w+)', clean_line)

        clean_line = self.find_urls(clean_line)

        self.find_trash(clean_line)

        return self.inf_dict

    def find_trash(self, clean_line):
        """ поиск безсмысленых слов """
        tokens = clean_line.split(' ')

        clean_tokens = []
        for i in range(len(tokens)):                                           # очстка от "" и пунктуации (односимвлн слова нам тоже не нужны)
            if len(tokens[i]) < 2:
                continue
            while True:
                if tokens[i][-1] in string.punctuation:
                    tokens[i] = tokens[i][:-1]
                else:
                    clean_tokens.append(tokens[i])
                    break

        clean_tokens = set(clean_tokens)
        for i in clean_tokens:                                                 # проверка на смсл
            if nltk.wsd.lesk(tokens, i) is None:
                self.inf_dict['orphan_tokens'].append(i)

    def find_urls(self, clean_line):
        """ отлавливание ЮРЛОВ """
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.line)
        clean_line = self.remove_words('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                       clean_line)

        if len(urls):
            self.inf_dict["metadata"].extend(urls)
        return clean_line

    def remove_words(self, expr, line):
        """ функция для очисти регулярочками """
        return re.sub(expr, '', line)


if __name__ == "__main__":

    data = read_file('input.txt')                   # чтение из файла

    result = {'records': []}                        # словарь для сериализации

    for i in data:                                  # обработка строк
        hndlr = LineHandler(i)
        result['records'].append(hndlr.explore())

    with open('output.json', 'w') as file:          # сереализация
        json.dump(result, file)

#!/usr/bin/env python
import nltk
import re
import string
import json


class FileReader:
    @staticmethod
    def read_file(name):
        """ func to read from file """
        with open(name) as fl:
            return fl.readlines()


class JsonWriter:
    @staticmethod
    def write_json(name, jsn):
        with open(name, 'w') as file:                   # serialization
            json.dump(jsn, file)


class RemoverUnwantedWords:
    @staticmethod
    def remove_words(expr, line):
        """ func for cleaning by regex """
        return re.sub(expr, '', line)


class CheckerForMeaning:
    @staticmethod
    def find_trash(clean_line, inf_dict):
        """ find contextless word """
        tokens = clean_line.split(' ')

        clean_tokens = []
        for i in range(len(tokens)):                    # removing punctuation and " "
            if len(tokens[i]) < 2:
                continue
            while True:
                if tokens[i][-1] in string.punctuation:
                    tokens[i] = tokens[i][:-1]
                else:
                    clean_tokens.append(tokens[i])
                    break

        clean_tokens = set(clean_tokens)
        for i in clean_tokens:                          # check for meaning
            if nltk.wsd.lesk(tokens, i) is None:
                inf_dict['orphan_tokens'].append(i)
        return inf_dict


class UrlFinder:
    @staticmethod
    def find_urls(clean_line, raw_line, inf_dict):
        """ find URL """
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_line)
        funk_for_clean = RemoverUnwantedWords.remove_words
        clean_line = funk_for_clean('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                    clean_line)

        if len(urls):
            inf_dict["metadata"].extend(urls)
        return clean_line, inf_dict


class TweetLineHandler:
    """ class for performance extraction useful inf from tweet"""

    def __init__(self, line):
        self.line = line

    def explore(self):
        inf_dict = {'body': '', "metadata": [], 'body_tags': [], 'orphan_tokens': []}

        dog_index = self.line.rfind('@') + 1
        inf_dict["metadata"].append(self.line[dog_index:-3])                        # find [@...]

        line = self.line[:dog_index - 4]
        inf_dict['body'] = line
        clean_line = RemoverUnwantedWords.remove_words(r'[\$]\w+', line)            # remove $-words

        inf_dict['body_tags'] = re.findall(r'[\#\@](\w+)', clean_line)
        clean_line = RemoverUnwantedWords.remove_words(r'[\#\@](\w+)', clean_line)  # clean line

        clean_line, inf_dict = UrlFinder.find_urls(clean_line, self.line, inf_dict)

        inf_dict = CheckerForMeaning.find_trash(clean_line, inf_dict)

        return inf_dict


if __name__ == "__main__":

    data = FileReader.read_file('input.txt')  # reading from file

    result = {'records': []}

    for i in data:                            # tweet handling
        hndlr = TweetLineHandler(i)
        result['records'].append(hndlr.explore)

    JsonWriter.write_json('output.json', result)

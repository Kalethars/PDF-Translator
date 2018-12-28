# coding:utf-8

import os
import codecs
import argparse
import urllib.request
import codecs
import time
from Py4Js import Py4Js
import win_unicode_console

win_unicode_console.enable()


def pdf2txt(fileName):
    if not os.path.exists(fileName + '.pdf'):
        return

    print('Converting .pdf to .txt format...')
    os.system('py -2 pdf2txt.pyw -o "%s.txt" "%s.pdf"' % (fileName, fileName))


def txt2sentences(fileName):
    print('Converting text to sentences...')

    special = ['ff', 'fi', 'fl', 'ffi', 'ffl', 'ft']
    cid = dict()
    cid['(cid:128)'] = 'fi'
    cid['(cid:129)'] = 'ffi'
    cid['(cid:130)'] = 'ff'
    cid['(cid:131)'] = 'fl'
    cid['(cid:138)'] = 'tt'
    cid['(cid:140)'] = 'Th'

    f = codecs.open(fileName + '.txt', 'r', encoding='utf-8')
    s = f.read()
    f.close()

    lines = s.split('\r\n')
    start = 0
    end = len(lines)
    for j in range(len(lines)):
        line = ''
        for k in range(len(lines[j])):
            if lines[j][k].lower() in 'abcdefghijklmnopqrstuvwxyz':
                line = line + lines[j][k].lower()
        if line in ['abstract', 'abstracts', 'introduction'] and j < len(lines) / 2 and start == 0:
            start = j + 1
        elif line in ['acknowledgement', 'acknowledgements', 'acknowledgment', 'acknowledgments', 'reference',
                      'references'] and j >= len(lines) / 2 and end == len(lines):
            end = j
        line = lines[j]
        for k in range(len(lines[j]) - 1, -1, -1):
            if lines[j][k] == ' ':
                line = line[:-1]
            else:
                break
        lines[j] = line
    s = lines[start]
    for j in range(start + 1, end):
        if len(lines[j]) > 0:
            for k in cid.keys():
                lines[j] = lines[j].replace(k, cid[k])
            while '(cid:' in lines[j]:
                pos = lines[j].find('(cid:')
                pos2 = pos + lines[j][pos:].find(')') + 1
                lines[j] = lines[j].replace(lines[j][pos:pos2], '')
            s = s + '\r\n' + lines[j]
    sentence = ''
    sentenceCount = 0
    sentences = []
    letter = False
    space = False
    enter = False
    wordCount = 0
    word = ''
    for i in range(len(s)):
        if s[i].lower() in 'abcdefghijklmnopqrstuvwxyz-+/0123456789':
            enter = False
            if letter:
                letter = True
                word = word + s[i]
                sentence = sentence + s[i]
            else:
                letter = True
                space = False
                word = s[i]
                sentence = sentence + s[i]
        elif ord(s[i]) >= 64256 and ord(s[i]) <= 64261:
            enter = False
            if letter:
                letter = True
                word = word + special[ord(s[i]) - 64256]
                sentence = sentence + special[ord(s[i]) - 64256]
            else:
                letter = True
                space = False
                word = special[ord(s[i]) - 64256]
                sentence = sentence + special[ord(s[i]) - 64256]
        elif ord(s[i]) == 13 and word != '':
            if word[-1] == '-':
                word = word[:-1]
                sentence = sentence[:-1]
            else:
                letter = False
                space = True
                wordCount = wordCount + 1
                word = ''
                sentence = sentence + ' '
        elif ord(s[i]) == 10:
            if enter:
                letter = False
                space = False
                enter = False
                if wordCount >= 5:
                    sentences.append(sentence)
                    sentenceCount = sentenceCount + 1
                wordCount = 0
                sentence = ''
            else:
                enter = True
        elif s[i] in '@#$%^&*()_=[]{}:"|,<>~`' or ord(s[i]) == 39 or ord(s[i]) == 92 or ord(s[i]) == 8217:
            enter = False
            if letter:
                letter = False
                space = False
                wordCount = wordCount + 1
                word = ''
                if ord(s[i]) == 8217:
                    sentence = sentence + "'"
                else:
                    sentence = sentence + s[i]
            else:
                space = False
                if ord(s[i]) == 8217:
                    sentence = sentence + "'"
                else:
                    sentence = sentence + s[i]
        elif s[i] in '.!?;':
            enter = False
            if s[i] in '!?;' or (s[i] == '.' and (
                    word != 'al' and word != 'etc' and word != 'e' and word != 'g' and word != 'i' and
                    word.lower() != 'mr' and word.lower() != 'mrs' and word.lower() != 'ms' and word.lower() != 'dr')):
                if i < len(s) - 1:
                    if s[i] == '.' and not s[i + 1].isdigit():
                        letter = False
                        space = False
                        sentence = sentence + s[i]
                        if wordCount >= 5:
                            sentences.append(sentence)
                            sentenceCount = sentenceCount + 1
                        wordCount = 0
                        sentence = ''
                        word = ''
                    else:
                        letter = True
                        space = False
                        sentence = sentence + s[i]
                        word = word + s[i]
                else:
                    letter = False
                    space = False
                    sentence = sentence + s[i]
                    if wordCount >= 5:
                        sentences.append(sentence)
                        sentenceCount = sentenceCount + 1
                    wordCount = 0
                    sentence = ''
                    word = ''
            elif s[i] == '.' and (
                    word == 'al' or word == 'etc' or word == 'e' or word == 'g' or word == 'i' or
                    word.lower() == 'mr' and word.lower() == 'mrs' and word.lower() == 'ms' and word.lower() == 'dr'):
                sentence = sentence + s[i]
                letter = False
                wordCount = wordCount + 1
                word = ''
        else:
            if ord(s[i]) != 13:
                enter = False
            if letter:
                letter = False
                space = True
                wordCount = wordCount + 1
                word = ''
                sentence = sentence + ' '
            else:
                if not space and sentence != '':
                    sentence = sentence + ' '
                    space = True

    f = open(fileName + '_sentences.txt', 'w')
    f.write('\n'.join(sentences))
    f.close()


def translate(fileName):
    def output(f, s):
        f.write(s)
        print(s, end='')

    def open_url(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return data

    def translatePart(content):
        RETRY_PUNISHMENT = 2

        if len(content) > 4891:
            print('Length exceeded!')
            return

        url = 'http://translate.google.cn/translate_a/single?client=t' \
              '&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca' \
              '&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1' \
              '&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s' % (js.getTk(content), urllib.parse.quote(content))

        retryCount = 0
        while True:
            try:
                response = open_url(url)
                break
            except Exception as e:
                retryCount += 1
                print('Internet connection seems to have some problems, retry after %i seconds...' %
                      (retryCount * RETRY_PUNISHMENT))
                print('(%s)' % str(e))
                time.sleep(retryCount * RETRY_PUNISHMENT)

        response = response.replace('[null,', '[None,')
        response = response.replace(',null', ',None')
        response = response.replace(',true', ',True')
        response = response.replace(',false', ',False')

        result = eval(response)

        f = codecs.open(fileName + '_translated.txt', 'a', 'utf-8')
        output(f, content)
        for i in range(len(result[0])):
            if result[0][i][0] != None:
                output(f, result[0][i][0])
        output(f, '\r\n\r\n')
        f.close()
        return
        # end=result.find("\",")
        # if end>4:
        # return result[4:end]

    f = codecs.open(fileName + '_sentences.txt', 'r', 'utf-8')
    s = f.read().split('\r\n')
    f.close()
    f = codecs.open(fileName + '_translated.txt', 'w', 'utf-8')
    f.close()

    print('Translating...')

    js = Py4Js()
    for i in range(len(s)):
        print('%i/%i' % (i + 1, len(s)))
        translatePart(s[i] + '\n')

    print('Translation finished!')


parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parsedArgs = parser.parse_args()

fileName = parsedArgs.file
if fileName[-4:] in {'.pdf', '.txt'}:
    fileName = fileName[:-4]

pdf2txt(fileName)
txt2sentences(fileName)
translate(fileName)

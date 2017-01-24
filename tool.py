# coding=utf-8
import numpy as np
import sys
import MySQLdb
import random
import copy
import time

def get_file_lines(path):
    """读取文件中所有的函数

    :param
        path：文件路径
    :return
        lines：包含文本内容的数组
    """
    with open(path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    f.close()
    return lines


def get_speech_dic():
    """ 获取词性权重表

    :return
        speechDic：词性权重表 speechDic[词性]=权重
    """
    lines = get_file_lines('./dict/speech.txt')
    speech_dic = {}
    for i in lines:
        i = i.split('\t', 2)
        speech_dic[i[0]] = float(i[1])
    return speech_dic


def lcs(strA, strB):
    '''利用LCS求两个字符串的最大公共子串

    :param
        strA：字符串A
        strB：字符串B
    :return:
        strC：最大公共子串
    '''
    if strA == strB:
        return strA
    try:
        strA = strA.decode("utf-8")
        strB = strB.decode("utf-8")
    except:
        print '不让转码'

    lenA = len(strA)
    lenB = len(strB)
    opt = np.zeros((lenA + 1, lenB + 1))
    for i in np.arange(lenA) + 1:
        for j in np.arange(lenB) + 1:
            if i != 0 and j != 0:
                if strA[i - 1] == strB[j - 1]:
                    opt[i][j] = opt[i - 1][j - 1] + 1
                else:
                    opt[i][j] = max(opt[i - 1][j], opt[i][j - 1])

    i = lenA
    j = lenB
    strC = []
    while i > 0 and j > 0:
        if strA[i - 1] == strB[j - 1]:
            strC.append(strA[i - 1])
            i -= 1
            j -= 1
        elif opt[i - 1][j] >= opt[i][j - 1]:
            i -= 1
        else:
            j -= 1
    strC.reverse()
    return strC


def get_stop_word():
    stop_word=set([])
    for line in get_file_lines('./dict/stopwords.txt'):
        stop_word.add(line.decode("utf-8"))
    return stop_word


def write_file(path, lines, flag):
    """

    :param
        path：写入的文件路径
        lines：写入的文件内容
    :return:
        True：操作成功
    """
    f = open(path, flag)
    for line in lines:
        try:
            f.write(line.encode('utf-8') + "\n")
        except UnicodeError:
            f.write(line + "\n")
    f.flush()
    f.close()
    return True


def get_freq_dic(path):
    freq_dic = {}

    for line in get_file_lines(path):
        line = line.decode("utf-8")
        temp = line.split("\t")
        freq_dic[temp[0]] = int(temp[1])

    return freq_dic


def get_flag_dic(path):
    word_flag_dic = {}
    for line in get_file_lines(path):
        line = line.decode("gbk")
        temp = line.split(",")
        word_flag_dic[temp[0]] = temp[1:]
    return word_flag_dic


def long_to_int(value):
    """ 将long类型转换为int类型，超出最大值部分只能划除

    :param value:
    :return:
    """
    assert isinstance(value, (int, long))
    return int(value & sys.maxint)


def exe_time(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        sys.stdout.write('\033[0;32;0m')
        print "-----------------------------------"
        print "%s,function \033[4;32;0m%s()\033[0m\033[0;32;0m start" \
              % (time.strftime("%X", time.localtime()), func.__name__)
        sys.stdout.write('\033[0m')
        res = func(*args, **kwargs)
        sys.stdout.write('\033[0;32;0m')
        print "%s,function \033[4;32;0m%s()\033[0m\033[0;32;0m end" \
              % (time.strftime("%X", time.localtime()), func.__name__)
        print "%.3fs taken for function \033[4;32;0m%s()\033[0m\033[0;32;0m" \
              % (time.time() - t0, func.__name__)
        print "-----------------------------------"
        sys.stdout.write('\033[0m')
        return res
    return wrapper


stop_word = get_stop_word()
speech_dic = get_speech_dic()
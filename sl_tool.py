# -*- coding: utf-8 -*-
import sys
import os
import shutil

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = "bard"


def get_exist_news_id():
    """ 获取现有新闻的id并返回

    :return:
    exist_news_id: {cmt_id: news_id}

    """
    exist_news_id = {}
    lines = get_file_lines("./data/exist_news_id.txt")
    for line in lines:
        line = line.split("@@@@")
        exist_news_id[line[1]] = int(line[0])
    return exist_news_id


def save_exist_news_id(exist_news_id):
    """ 存储现有新闻的id

    :param exist_news_id: {cmt_id: news_id}
    :return:
    """
    id_list = []
    for it in exist_news_id.items():
        id_list.append(str(it[1]) + "@@@@" + it[0])
    write_file_append("./data/exist_news_id.txt", id_list)


def save_lasted_id(lasted_id):
    """ 获取最新的词/新闻/事件/主题编号

    :param lasted_id:
    :return:
    """
    parameter_list = []
    term_list = sorted(lasted_id.items(), reverse=True, key=lambda x: x[0])
    line = term_list[0][0] + "##" + str(term_list[0][1])
    for term in term_list[1:]:
        line = line + "@@@@" + term[0] + "##" + str(term[1])
    parameter_list.append(line)
    write_file_append("./data/parameter/lasted_id_parameter.txt", parameter_list)


def load_lasted_id():
    """ 保存最新的词/新闻/事件/主题编号

    :return:
    """
    lasted_id = {}
    line = get_file_lines("./data/parameter/lasted_id_parameter.txt")
    if len(line) == 0:
        lasted_id["word_id"] = 0
        lasted_id["news_id"] = 0
        lasted_id["event_id"] = 0
        lasted_id["topic_id"] = 0
    else:
        parameter_rows = line[-1].split('@@@@')
        for parameter_row in parameter_rows:
            parameter = parameter_row.split('##')
            lasted_id[parameter[0]] = int(parameter[1])
    return lasted_id


def save_word_info(word_info):
    write_file_append("./data/word_info_append.txt", word_info)


def load_word_info():
    word_dir = {}
    lines = get_file_lines("./data/word_info_append.txt")
    for line in lines:
        line = line.split("@@@@")
        word_dir[line[1].decode('utf-8')] = int(line[0])
    return word_dir


def get_news_event_relative():
    """ 获得新闻事件关联词典

    :return:
    news_event_relative：{新闻编号:事件编号}
    event_news_relative：{事件编号:新闻编号}
    """
    news_event_relative = {}
    event_news_relative = {}
    lines = get_file_lines("./data/event_news_relative.txt")
    for line in lines:
        line = line.split("@@@@")
        news_event_relative[int(line[1])] = int(line[0])
        if int(line[0]) not in event_news_relative:
            event_news_relative[int(line[0])] = int(line[1])
    return news_event_relative, event_news_relative


def save_event_news_relative(event_news_relative_list):
    write_file("./data/event_news_relative.txt", event_news_relative_list)


def save_topic_event_relative(topic_event_relative_list_append):
    write_file("./data/topic_event_relative_append.txt", topic_event_relative_list_append)


def save_event_keyword_relative(event_keyword_relative):
    write_file("./data/event_keyword_relative.txt", event_keyword_relative)


def save_event_keyword_relative_mongodb(event_keyword_relative_mongodb):
    write_file("./data/event_keyword_relative_mongodb.txt", event_keyword_relative_mongodb)


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


def write_file(path, lines):
    """

    :param
        path：写入的文件路径
        lines：写入的文件内容
    :return:
        True：操作成功
    """
    f = open(path, 'w')
    for line in lines:
        f.write(line.encode('utf-8') + "\n")
    f.flush()
    f.close()
    return True


def write_file_append(path, lines):
    """

    :param
        path：写入的文件路径
        lines：写入的文件内容
    :return:
        True：操作成功
    """
    f = open(path, 'a')
    for line in lines:
        f.write(line.encode('utf-8') + "\n")
    f.flush()
    f.close()
    return True


def get_term_dir():
    term_dir = {}
    flag_dir = {}
    speech_dir = get_speech_dic()
    with open('./data/dictionary/weight.txt') as ifile:
        for line in ifile:
            arr = line.split('\t', 5)
            flag_dir[arr[0]] = arr[1]
            if arr[1] in speech_dir:
                term_dir[arr[0]] = speech_dir[arr[1]] * (1 + float(arr[4]))
            else:
                term_dir[arr[0]] = 1
    return term_dir, flag_dir


def get_speech_dic():
    """ 获取词性权重表

    :return
        speechDic：词性权重表 speechDic[词性]=权重
    """
    lines = get_file_lines('./data/dictionary/speech.txt')
    speech_dic = {}
    for i in lines:
        i = i.split('\t', 2)
        speech_dic[i[0]] = float(i[1])
    return speech_dic


def get_emotion_words():
    """ 获取各个类别情绪词词典

    :return:
    """
    path = './data/emotion_dictionary/'
    dictionary = {}
    for f in os.listdir(path):
        lines = get_file_lines(path + f)
        f = f.split('.txt')[0].decode('gbk').encode('utf-8')
        if f in dictionary:
            dictionary[f].extend(lines)
        else:
            dictionary[f] = lines
    return dictionary


def get_special_words():
    """ 获取副词词典

    :return:
    """
    path = './data/dictionary/special.txt'
    lines = get_file_lines(path)
    special_dic = {}
    for line in lines:
        line = line.split(' ')
        special_dic[line[0].decode('utf-8')] = float(line[1])
    return special_dic


def get_convert_labels():
    """ 获取反对词词典

    :return:
    """
    lines = get_file_lines('./data/dictionary/convert.txt')
    convert_dic = {}
    for line in lines:
        line = line.split(' ')
        convert_dic[line[0]] = line[1]
    return convert_dic


def get_emotion_dic():
    """ 获取情绪对应编号

    :return:
    """
    lines = get_file_lines('./data/dictionary/emotion.txt')
    emotion_dic = {}
    for line in lines:
        line = line.split('\t')
        emotion_dic[line[0]] = int(line[1])
    return emotion_dic


def translate_news(news_rows):
    """ 用户将数据库返回的信息表示为news类

    :param news_rows:
    :return:
    """
    pass


def save_mysql_parameter(mysql_parameter):
    items = mysql_parameter.items()
    line = items[0] + "##" + str(items[1])
    for i in items[1:]:
        line = line + "@@@@" + i[0] + "##" + str(i[1])
    write_file_append("./data/parameter/mysql_parameter.txt", [line])


def get_save_parameter():
    """ 多线程存储需要参数同步，其他情况下不需要

    :return:
    """
    save_parameter = {}
    lines = get_file_lines('./data/parameter/db_parameter.txt')
    if len(lines) == 0:
        save_parameter["mysql_word_save_rows"] = 63737
        save_parameter["mongodb_word_save_rows"] = 0
    else:
        line = lines[-1]
        arr = line.split("@@@@")
        for i in arr:
            parameter = i.split("##")
            save_parameter[parameter[0]] = int(parameter[1])
    return save_parameter


def reload_data():
    """ 还原数据

    :return:
    """
    source_path = "./backup/"
    target_path = "./data/"
    copy_dir(source_path, target_path)
    source_path = "./backup/parameter/"
    target_path = "./data/parameter/"
    copy_dir(source_path, target_path)


def backup_data():
    """ 备份数据

    :return:
    """
    source_path = "./data/"
    target_path = "./backup/"
    copy_dir(source_path, target_path)
    source_path = "./data/parameter/"
    target_path = "./backup/parameter/"
    copy_dir(source_path, target_path)


def copy_dir(source_path, target_path):
    for file_name in os.listdir(source_path):
        s_path = os.path.join(source_path, file_name)
        t_path = os.path.join(target_path, file_name)
        if os.path.isfile(s_path):
            shutil.copy2(s_path, t_path)


def get_stop_word():
    stop_word=set([])
    for line in get_file_lines('./data/dictionary/emotion.txt'):
        stop_word.add(line.decode("utf-8"))
    return stop_word

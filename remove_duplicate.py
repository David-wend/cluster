# coding=utf-8

import info_init
import tool
import numpy as np
from jieba import posseg as pseg
import create_news_doc
import count
from datetime import datetime

time_format = "%Y-%m-%d %H:%M:%S"


def count_similar(title_arr_list, title_arr_j, limit_info, similar_word_limit=2):
    """ 利用相同关键词与最大公共子串长度计算事件与新闻的相似度

    对事件新闻列表中的每个新闻news_i:
        计算新闻news_i与新闻news_j的新闻标题分词交集intersection_ij
        对于交集intersection中的每个分词word：
            新闻i与新闻j的相似度similarity_ij+=词表中word的权重
        计算新闻i与新闻j标题中的最大公共子串LCS_ij
        alpha=1+最大公共子串的长度/新闻ij中标题长度的最大值
        相似度阈值limit=基础相似度阈值base_limit+新闻ij中标题长度的最大值/5
        如果similarity_ij*(1+alpha)>limit:
            相似新闻数similar_news_num+=1
    如果(相似新闻数/事件新闻数)>0.6:
        则认为事件与新闻相似，将新闻加入到事件的新闻列表中

    :param title_arr_list:包含多个新闻标题分词数组的二维数组
    :param title_arr_j:新闻标题分词数组
    :return:
    相似则返回True，否则返回False
    """
    similar_news_num = 0
    for title_arr_i in title_arr_list:
        similarity = float(0)
        similar_word_num = 0
        stop_words = ["搜狐", "新闻", "腾讯", "腾讯网", "网易", "新浪"]
        for word in set(title_arr_i) & set(title_arr_j) - set(stop_words):
            similar_word_num += 1
            similarity += 1  # info_init.termdir.get(word, 1)
            if word in info_init.flagdir:
                similarity += info_init.speechdir.get(info_init.flagdir[word], 1)
        if similar_word_num > similar_word_limit:
            # news_lcs = tool.lcs("".join(title_arr_i), "".join(title_arr_j))  # 最大相同子串
            similarity *= (1 + len(set(title_arr_i) & set(title_arr_j)) / max(len(title_arr_i), len(title_arr_j)))
        limit = limit_info + float(min(len(title_arr_i), len(title_arr_j))) / 5
        # if "乐天" in ".".join(title_arr_i) and "乐天" in ".".join(title_arr_j):
        #     print similarity, limit
        #     print "两个新闻标题为" + ".".join(title_arr_i) + "@@@@" + ".".join(title_arr_j) + " " + str(similarity)

        if similarity > limit:
            # print similarity, limit
            print "两个新闻标题为" + ".".join(title_arr_i) + "@@@@" + ".".join(title_arr_j) + " " + str(similarity)
            # print title_arr_i, title_arr_j
            similar_news_num += 1

    if float(similar_news_num) / len(title_arr_list) > 0.6:  # 投票表决
        return True
    else:
        return False


def remove_duplicate():
    # time_1 = datetime.now()

    lines = tool.get_file_lines("./dict/doc.txt")
    words = []
    filter_set = set([])
    times = []
    ids = []

    # for i in range(100, 200):
    new_lines = []
    for i in range(len(lines)):
        try:
            arr = lines[i].split("@@@@", 1)
            # print arr
            brr = arr[1].split("##", 3)
            times.append(datetime.strptime(brr[2], time_format))
            ids.append(int(arr[0]))
            words.append([term.word for term in pseg.cut(brr[0])])
            new_lines.append(lines[i])
        except IndexError:
            continue
            # words.append([])

    times_index = np.argsort(times, axis=0)
    times = np.sort(times, axis=0)
    words = np.array(words)[times_index]
    ids = np.array(ids)[times_index]
    new_lines = np.array(new_lines)[times_index]

    # for i in range(len(times)):
    #     print "".join(words[i]), times[i]

    temp_relative = []
    flags = np.ones(len(words))
    for i in range(len(words) - 1):
        # print i, times[i]
        if flags[i]:
            flags[i] = 0
            for j in range(i + 1, len(words)):
                if flags[j]:
                    delta = times[j] - times[i]
                    if abs(delta.days) < 2:
                        if count_similar([words[i]], words[j], 4.5, 3):
                            flags[j] = 0
                            filter_set.add(j)
                            temp_relative.append(
                                str(ids[i]) + "@@@@" + str(ids[j]) + "@@@@" + "".join(words[i]) + "@@@@" + "".join(
                                    words[j]))
                    else:
                        # print abs(delta.days)
                        break
    temp = []
    result = []
    result_set = set(range(len(words))) - filter_set
    for i in result_set:
        try:
            temp.append(new_lines[i].split("@@@@")[1].split("##")[0])
            result.append(new_lines[i])
        except IndexError:
            print new_lines[i]

    tool.write_file("./dict/similar_relative.txt", temp_relative, "w")
    tool.write_file("./dict/filter_doc.txt", result, "w")
    tool.write_file("./dict/filter_doc_title.txt", temp, "w")

    # time_2 = datetime.now()
    # print time_1, time_2


if __name__ == '__main__':
    print datetime.now()
    # 对新闻标题进行去重
    # remove_duplicate()
    # 根据去重后的标题，重新生成词典
    # create_news_doc.transform_doc()
    # 挖掘频繁项集
    count.get_co_name()
    # 根据频繁模式进行聚类
    count.lan_de_qi_ming()

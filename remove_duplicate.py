# coding=utf-8

import info_init
import tool
import numpy as np
from jieba import posseg as pseg
import create_news_doc
import count
from datetime import datetime


def count_similar(title_arr_list, title_arr_j, limit_info):
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
        for word in set(title_arr_i) & set(title_arr_j):

            similar_word_num += 1
            similarity += info_init.termdir.get(word, 1)
            if word in info_init.flagdir:
                similarity += info_init.speechdir.get(info_init.flagdir[word], 1)
        if similar_word_num > 2:
            news_lcs = tool.lcs("".join(title_arr_i), "".join(title_arr_j))  # 最大相同子串
            similarity *= (1 + len(news_lcs) / max(len(title_arr_i), len(title_arr_j)))
        limit = limit_info + float(min(len(title_arr_i), len(title_arr_j))) / 5
        # print similarity, limit
        if similarity > limit:
            # print similarity, limit
            # print ".".join(title_arr_i) + "@@@@" + ".".join(title_arr_j)
            # print title_arr_i, title_arr_j
            similar_news_num += 1

    if float(similar_news_num) / len(title_arr_list) > 0.6:  # 投票表决
        return True
    else:
        return False


def remove_duplicate():
    lines = tool.get_file_lines("./dict/doc.txt")
    words = []
    filter_set = set([])

    for i in range(len(lines)):
        try:
            arr = lines[i].split("@@@@", 1)
            print arr
            brr = arr[1].split("##", 3)
            words.append([term.word for term in pseg.cut(brr[0])])
        except IndexError:
            words.append([])

    flags = np.ones(len(words))
    for i in range(len(words)):
        if flags[i]:
            flags[i] = 0
            for j in range(len(words)):
                if i==j:
                    continue
                if flags[j]:
                    if count_similar([words[i]], words[j], 3):
                        flags[j] = 0
                        filter_set.add(j)

    temp = []
    result = []
    result_set = set(range(len(words))) - filter_set
    for i in result_set:
        temp.append(lines[i].split("@@@@")[1].split("##")[0])
        result.append(lines[i])

    tool.write_file("./dict/filter_doc.txt", result, "w")
    tool.write_file("./dict/filter_doc_title.txt",temp,"w")


if __name__ == '__main__':
    print datetime.now()
    # remove_duplicate()
    create_news_doc.transform_doc()
    count.get_co_name()



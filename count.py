# coding=utf-8

import Inverted_index
import tool
import numpy as np
import pandas as pd
from sklearn import tree
import jieba
import remove_duplicate
import math
from collections import Counter
from datetime import datetime

__author__ = 'david'


class FeatureCluster:
    def __init__(self, feature_cut):
        self.feature_cut_array = []
        self.append_new_feature_cut(feature_cut)

    def append_new_feature_cut(self, feature_cut):
        self.feature_cut_array.append(feature_cut)

    def __str__(self):
        return "@@".join(["".join(y) for y in self.feature_cut_array])


def update_doc_id(doc_id_dic, new_word, old_word):
    """ 将old_word下所有文档归类到new_word

    :param doc_id_dic:
    :param new_word:
    :param old_word:
    :return:
    """
    doc_id_dic[new_word] = list(set(doc_id_dic[new_word]).union(set(doc_id_dic[old_word])))
    del doc_id_dic[old_word]
    return doc_id_dic


def calculate_dtw(dictionary, word_a, word_b):
    """ 利用动态时间规划计算两个序列的相似度

    :param dictionary:
    :param word_a:
    :param word_b:
    :return:
    """
    time_dict_a = Counter(calculate_fm_day_info(dictionary, word_a))
    time_dict_b = Counter(calculate_fm_day_info(dictionary, word_b))
    time_array_a = []
    time_array_b = []
    for i in np.sort(dict.fromkeys([x for x in time_dict_a if x in time_dict_b]).keys()):
        time_array_a.append(time_dict_a[i])
        time_array_b.append(time_dict_b[i])
    if len(time_array_a) == 0 or len(time_array_a) == 0:
        return 20

    dtw_value = tool.get_dtw(time_array_a, time_array_a)
    return dtw_value


def calculate_time_overlapping_rate(dictionary, word_a, word_b):
    """ 计算两个词的时间分布重合率

    :param dictionary:
    :param word_a:
    :param word_b:
    :return:
    """
    time_array_a = calculate_fm_day_info(dictionary, word_a)
    time_array_b = calculate_fm_day_info(dictionary, word_b)
    print len(time_array_a), len(time_array_b),
    return float(len(set(time_array_a) & set(time_array_b))) / len(set(time_array_a) | set(time_array_b))


def calculate_hot(doc_id_dic, freq_mode):
    """ 计算特征热度，计算公式为它所包含的新闻数目平方和的二次方,即sqrt(a**2+b**2)

    :param doc_id_dic:
    :param freq_mode:
    :return:
    """
    hot_value = 0
    for feature_cut_array_k in freq_mode.feature_cut_array:
        word = "".join(feature_cut_array_k)
        hot_value += len(doc_id_dic[word]) ** 2
    return np.sqrt(hot_value)


def calculate_fm_day_info(dictionary, word):
    """ 返回频繁模式在时间分布信息

    :param dictionary:
    :param word:
    :return:
    """
    set_i, dict_i = dictionary.transform_term_info(word)
    time_array = []
    for t in set_i:
        new_datetime = datetime(dictionary.doc_dic[t].time.year, dictionary.doc_dic[t].time.month,
                                dictionary.doc_dic[t].time.day, 0, 0)
        time_array.append(new_datetime)
    time_array = np.array(time_array)
    # return [Counter(time).most_common(1)[0][0], time.min(), time.max()]
    return np.sort(time_array)


def calculate_novelty(dictionary, word, short_period=7, middle_period=14, long_period=30):
    """ 根据频繁模式出现的时间规律，计算新颖度，公式为出现次数的变异系数

    :param dictionary:
    :param word:
    :param short_period:
    :param middle_period:
    :param long_period:
    :return:
    """
    time_array = calculate_fm_day_info(dictionary, word)
    time_dict_array = sorted(Counter(time_array).items(), key=lambda x: x[0], reverse=True)
    max_time = time_dict_array[0][0]
    max_time_num = time_dict_array[0][1]
    short_arr = np.zeros(short_period)
    middle_arr = np.zeros(middle_period)
    long_arr = np.zeros(long_period)
    short_arr[0] = max_time_num
    middle_arr[0] = max_time_num
    long_arr[0] = max_time_num
    for t in time_dict_array[1:]:
        delta = max_time - t[0]
        if delta.days < short_period:
            short_arr[delta.days] += 1
        if delta.days < middle_period:
            middle_arr[delta.days] += 1
        if delta.days < long_period:
            long_arr[delta.days] += 1
    print short_arr, middle_arr, long_arr
    # return [short_arr.std() / short_arr.mean(), middle_arr.std() / middle_arr.mean(), long_arr.std() / long_arr.mean(),
    #         long_arr.sum()]

    return [short_arr.mean() / middle_arr.mean(), middle_arr.mean() / long_arr.mean(),
            short_arr.mean() / long_arr.mean(), short_arr.std() / short_arr.mean(),
            middle_arr.std() / middle_arr.mean(), long_arr.std() / long_arr.mean(),
            long_arr.sum()]


def calculate_integrity(dictionary, word):
    """ 计算完整性

    :param dictionary:
    :param word:
    :return:
    """
    word_freq = dictionary.word_freq_dic[dictionary.word_index_dic[word]]
    f_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[:-1], ""), 1)
    return float(word_freq) / f_word_freq


def calculate_stability(dictionary, word):
    """ 计算稳定性

    :param dictionary:
    :param word:
    :return:
    """
    word_freq = dictionary.word_freq_dic[dictionary.word_index_dic[word]]
    f_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[:-1], ""), 1)
    l_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[1:], ""), 1)
    return float(word_freq) / (f_word_freq + l_word_freq - word_freq + 1)


def calculate_independence_by_freq(dictionary, word):
    """ 计算灵活性方法1

    :param dictionary:
    :param word:
    :return:
    """
    set_i, dict_i = dictionary.transform_term_info(word)
    f_word_set = set([])
    l_word_set = set([])
    for doc_id in set_i:
        for location_id in dict_i[doc_id].location_ids:
            if location_id > 0:
                f_word_set.add(dictionary.doc_dic[doc_id].words[location_id - 1])
            if location_id < len(dictionary.doc_dic[doc_id].words) - 1:
                l_word_set.add(dictionary.doc_dic[doc_id].words[location_id + 1])
    return [float(len(f_word_set)) / (dictionary.word_freq_dic[dictionary.word_index_dic[word]] + 1),
            float(len(l_word_set)) / (dictionary.word_freq_dic[dictionary.word_index_dic[word]] + 1)]


def calculate_independence(dictionary, word):
    """ 计算灵活性方法2

    :param dictionary:
    :param word:
    :return:
    """
    set_i, dict_i = dictionary.transform_term_info(word)
    f_word_set = set([])
    l_word_set = set([])
    for doc_id in set_i:
        for location_id in dict_i[doc_id].location_ids:
            if location_id > 0:
                # print dictionary.doc_dic[doc_id].words
                f_word_set.add(dictionary.doc_dic[doc_id].words[location_id - 1])
            if location_id < len(dictionary.doc_dic[doc_id].words) - 1:
                l_word_set.add(dictionary.doc_dic[doc_id].words[location_id + 1])
    return [1 - float(1) / (len(f_word_set) + 1), 1 - float(1) / (1 + len(l_word_set))]


def get_co_name():
    """ 频繁模式挖掘算法

    :return:
    """
    i_dic = Inverted_index.InvertDic()
    i_dic.init_all_dic()
    candidate_list = i_dic.word_index_dic.keys()
    # 这里设定n阶频繁模式及其对应的支持度阈值
    limit_dic = {1: 4, 2: 3, 3: 3, 4: 2, 5: 2}
    ids_dic = {}
    tool.write_file("./dict/word_co.txt", [], "w")
    # 设置最多计算到第K阶的频繁模式
    for k in range(10):
        result_dic = {}
        for i in range(len(candidate_list)):
            for j in range(len(candidate_list)):
                if i == j:
                    continue
                # 计算两个频繁模式是否满足条件可以合并
                if i_dic.add_term_bound(candidate_list[i], candidate_list[j]):
                    # 获取满足条件的频繁模式文档分布信息
                    ids, locations = i_dic.get_co_occurrence_info(candidate_list[i], candidate_list[j])
                    if len(ids) > limit_dic.get(len(candidate_list[i]), 2):
                        # 记录新频繁模式的信息
                        i_dic.add_new_term(candidate_list[i], candidate_list[j])
                        new_word = candidate_list[i] + i_dic.index_word_dic[i_dic.word_comb_word_dic[
                            i_dic.word_index_dic[candidate_list[j]]][-1]]
                        result_dic[new_word] = len(ids)
                        ids_dic[new_word] = ids

        result_list = sorted(result_dic.items(), key=lambda x: x[1])
        # 保存所有频繁模式的信息
        lines = []
        for temp in result_list:
            # try:
            lines.append(temp[0] + "@@" + str(temp[1]) + "@@" + str(
                round(calculate_integrity(i_dic, temp[0]), 4)) + "@@" + str(
                round(calculate_stability(i_dic, temp[0]), 4)) + "@@" + "##".join(
                [str(round(x, 4)) for x in calculate_novelty(i_dic, temp[0])]) + "@@" + "##".join(
                [str(round(x, 4)) for x in calculate_independence(i_dic, temp[0])]) + "@@" + "##".join(
                [str(round(x, 4)) for x in calculate_independence_by_freq(i_dic, temp[0])]) + "@@" + "##".join(
                [str(x) for x in ids_dic[temp[0]]]))
            # except KeyError:
            #     print temp[0]
            #     continue
        tool.write_file("./dict/word_co.txt", lines, "a")
        try:
            del result_dic[u"新闻"]
            del result_dic[u"搜狐"]
            del result_dic[u"腾讯"]
        except:
            pass
        candidate_list = result_dic.keys()


def var_dump_word_tree(word, words, freq, values, doc_ids, word_index_dic):
    """ 打印某个频繁模式及其子模式

    :param word:
    :param words:
    :param freq:
    :param values:
    :param doc_ids:
    :param word_index_dic:
    :return:
    """
    word_index = word_index_dic[word]
    print words[word_index], freq[word_index], values[word_index][0], values[word_index][1], \
        values[word_index][2], values[word_index][3]
    if len(word) > 2:
        return var_dump_word_tree(word[:-1], words, freq, values, doc_ids, word_index_dic), \
               var_dump_word_tree(word[1:], words, freq, values, doc_ids, word_index_dic)


def load_data():
    """ 读取频繁模式信息

    :return:
    """
    path = "./dict/word_co.txt"
    lines = tool.get_file_lines(path)
    words = []
    word_index_dic = {}
    values = {}
    doc_ids = {}
    freq = {}
    num = 0
    for line in lines:
        arr = line.split("@@")
        word = arr[0].decode("utf8")
        words.append(word)
        word_index_dic[word] = num
        num += 1
        freq[word] = int(arr[1])
        crr = arr[4].split("##")
        brr = arr[5].split("##")
        values[word] = [float(arr[2]), float(arr[3]), float(brr[0]), float(brr[1]), float(crr[0]), float(crr[1])]
        doc_ids[word] = [int(x) for x in arr[7].split("##")]
    return words, freq, values, doc_ids, word_index_dic


def calculate_total_weight(freq, values):
    return freq * 0.1 + values[0] + values[1] + values[2] + values[3]


def remove_non_sense_word(words, freq, values):
    """ 根据频繁模式得分进行剪枝

    :param words:
    :param freq:
    :param values:
    :return:
    """
    result = {}
    # candidate_remove = {}
    for w_i in words:
        if freq[w_i] > 2:
            if values[w_i][0] > 0.7 and values[w_i][1] > 0.52 and values[w_i][2] > 0.6:
                result[w_i] = calculate_total_weight(freq[w_i], values[w_i])
            elif len(w_i) > 3 and freq[w_i] > 12 and values[w_i][0] > 0.45 and values[w_i][1] > 0.45 and values[w_i][
                2] > 0.7:
                result[w_i] = calculate_total_weight(freq[w_i], values[w_i])

    result_list = sorted(result.keys(), key=lambda x: x[1], reverse=False)  # 排序比较keys
    return result_list


def train_clf():
    word_weights = pd.read_csv("./dict/word_weight.txt", header=None, sep=",")
    col_names = ["word_name", "freq", "integrity", "stability",
                 "independence_l", "independence_r", "label"]
    word_weights.columns = col_names
    label = word_weights["label"]
    words_pd = word_weights["word_name"]
    word_weights.drop("label", axis=1, inplace=True)
    word_weights.drop("word_name", axis=1, inplace=True)

    dt_clf = tree.DecisionTreeClassifier(max_depth=5)
    dt_clf.fit(word_weights, label)
    pre_y = dt_clf.predict(word_weights)
    # print classification_report(label, pre_y)
    return words_pd[pre_y == 1].index


def calculate_sim(word_i_doc_ids, word_j_doc_ids):
    """ 根据文档分布进行相似度

    :param word_i_doc_ids:
    :param word_j_doc_ids:
    :return:
    """
    word_i_set = set(word_i_doc_ids)
    word_j_set = set(word_j_doc_ids)
    return float(len(word_i_set & word_j_set)) / (np.sqrt(len(word_i_set)) * np.sqrt(len(word_j_set)))


def calculate_sim_by_cut(word_index_dic, doc_ids, word_i_cut_array, word_j_cut_array):
    """ 根据文档分布计算相似度

    :param word_index_dic:
    :param doc_ids:
    :param word_i_cut_array:
    :param word_j_cut_array:
    :return:
    """
    word_i_set = set([])
    word_j_set = set([])
    for i in word_i_cut_array:
        if i in word_index_dic:
            if i == u"事件" or i == u"中国":
                continue
            word_i_set = word_i_set | set(doc_ids[i])
    for j in word_j_cut_array:
        if j in word_index_dic:
            if j == u"事件" or i == u"中国":
                continue
            word_j_set = word_j_set | set(doc_ids[j])
    word_i = "".join(word_i_cut_array)
    word_j = "".join(word_j_cut_array)
    lcs_similar = float(len(tool.lcs(word_i, word_j))) / max(len(word_i), len(word_j)) + 1
    # return float(len(word_i_set & word_j_set)) / (min_len * np.sqrt(max_len)), float(
    #     len(word_i_set & word_j_set)) / min(len(word_i_set), len(word_j_set)), float(
    #     len(word_i_set & word_j_set)) / (np.sqrt(min_len) * np.sqrt(max_len))
    return float(len(word_i_set & word_j_set)) / (np.sqrt(len(word_i_set)) * np.sqrt(len(word_j_set))) * lcs_similar


def calculate_entropy(doc_ids, doc_word_dic):
    """ 计算特征的熵重叠度

    :param doc_ids:
    :param doc_word_dic:
    :return:
    """
    entropy_value = 0
    for doc_id in doc_ids:
        entropy_value += -float(1) / len(doc_word_dic[doc_id]) * math.log10(
            float(1) / len(doc_word_dic[doc_id]))
    return entropy_value


def lan_de_qi_ming():
    # 初始化词典，并读取一阶频繁项集
    i_dic = Inverted_index.InvertDic()
    i_dic.init_all_dic()
    words, freq, values, doc_ids, word_index_dic = load_data()

    # 根据词元得分进行预剪枝
    word_name = remove_non_sense_word(words, freq, values)

    # 分词
    word_cut_array = []
    # for word in words:
    for word in word_name:
        if len(word) > 2:
            word_cut_array.append([x for x in jieba.cut(word)])
        else:
            word_cut_array.append([word])

    # 一趟聚类，根据频繁项集文档分布计算相似度
    feature_array = []
    feature_tag = np.zeros(shape=len(word_cut_array))
    distance = np.zeros(shape=(len(word_cut_array), len(word_cut_array)))
    for i in range(len(word_cut_array) - 1):
        if feature_tag[i] == 0:
            feature_tag[i] = 1
            fc = FeatureCluster(word_cut_array[i])
            feature_array.append(fc)
            for j in range(i + 1, len(word_cut_array)):
                if i == j:
                    continue
                if feature_tag[j] == 0:
                    # 考虑时间相似度

                    num = 0
                    for word_cut_array_k in fc.feature_cut_array:
                        similar = calculate_sim_by_cut(word_index_dic, doc_ids,
                                                       word_cut_array_k,
                                                       word_cut_array[j])
                        if similar > 1.7:
                            feature_tag[j] = 1
                            fc.append_new_feature_cut(word_cut_array[j])
                            break
                        if similar > 0.7:
                            num += 1
                            if float(num) / len(fc.feature_cut_array) > 0.8:
                                fc.append_new_feature_cut(word_cut_array[j])
                                feature_tag[j] = 1
                                break

    # 话题去重
    for fc in feature_array:
        print fc, calculate_hot(doc_ids, fc)

        # 根据上下位去重，如有“林丹出轨”去除“林丹出”
        new_feature_cut_array = []
        fca_sorted = sorted(fc.feature_cut_array, key=lambda x: len("".join(x)), reverse=False)
        words_fca_dict = {"".join(fca): fca for fca in fca_sorted}
        result = {}
        for fca in fca_sorted:
            word = "".join(fca)
            similar_w = calculate_total_weight(freq[word], values[word])
            result[word] = similar_w
            new_feature_cut_array.append(words_fca_dict[word])
            if word[:-1] in result:
                if values[word][0] > 0.8:
                    new_feature_cut_array.remove(words_fca_dict[word[:-1]])
                    doc_ids = update_doc_id(doc_ids, word, word[:-1])
                    del result[word[:-1]]
            if word[1:] in result:
                if values[word][0] > 0.8:
                    new_feature_cut_array.remove(words_fca_dict[word[1:]])
                    doc_ids = update_doc_id(doc_ids, word, word[1:])
                    del result[word[1:]]
        fc.feature_cut_array = new_feature_cut_array
        print fc

        # 根据语义去重
        new_feature_cut_array = []
        tag = np.zeros(shape=len(fc.feature_cut_array))
        fc.feature_cut_array = sorted(fc.feature_cut_array,
                                      key=lambda x: len("".join(x)),
                                      reverse=True)
        for i in range(len(fc.feature_cut_array)):
            if tag[i] == 0:
                tag[i] = 1
                new_feature_cut_array.append(fc.feature_cut_array[i])
                for j in range(len(fc.feature_cut_array)):
                    if i == j:
                        continue
                    if tag[j] == 0:
                        if remove_duplicate.count_similar([fc.feature_cut_array[i]], fc.feature_cut_array[j], 0.7,
                                                          similar_word_limit=1):
                            doc_ids = update_doc_id(doc_ids, "".join(fc.feature_cut_array[i]),
                                                    "".join(fc.feature_cut_array[j]))
                            tag[j] = 1

        fc.feature_cut_array = new_feature_cut_array
        print fc

    # 将特征文档空间模型转换为文档特征空间模型
    doc_word_dic = {}
    for fc in feature_array:
        for feature_cut_array_k in fc.feature_cut_array:
            word_name = "".join(feature_cut_array_k)
            for doc_id in doc_ids[word_name]:
                doc_word_dic[doc_id] = doc_word_dic.get(doc_id, []) + [word_name]

    # 计算事件下每一个话题簇熵重叠度，越小越纯粹
    entropy_dic = {}
    for fc in feature_array:
        for feature_cut_array_k in fc.feature_cut_array:
            word_name = "".join(feature_cut_array_k)
            entropy_dic[word_name] = calculate_entropy(doc_ids[word_name], doc_word_dic)
            # print word_name, calculate_entropy(doc_ids[word_index_dic[word_name]], doc_word_dic)

    # 讲文档优先归类到熵重叠度小的频繁模式
    entropy_list = sorted(entropy_dic.items(), key=lambda x: x[1])
    news_relative = {}
    for i in entropy_list:
        news_relative[i[0]] = doc_ids[i[0]]
        for doc_id in doc_ids[i[0]]:
            for word_name in doc_word_dic[doc_id]:
                if word_name != i[0]:
                    doc_ids[word_name].remove(doc_id)
            if doc_id in doc_word_dic:
                del doc_word_dic[doc_id]

    # 读取文档标题
    doc_dic = {}
    for line in tool.get_file_lines("./dict/filter_doc.txt"):
        arr = line.split("@@@@")
        brr = arr[1].split("##")
        doc_dic[int(arr[0])] = brr[0]

    # 输出频繁模式及相关文档
    temp = []
    for item in news_relative.items():
        print item[0], item[1]
        for doc_id in item[1]:
            print "\t" + doc_dic[doc_id]
            temp.append(str(word_index_dic[item[0]]) + "@@" + str(doc_id))
    tool.write_file("./dict/topic_news_relative.txt", temp, "w")

    # temp = []
    # num = 2
    # for fc in feature_array[:3]:
    #     for feature_cut_array_k in fc.feature_cut_array:
    #         word_name = "".join(feature_cut_array_k)
    #         temp.append(str(num) + "@@" + str(word_index_dic[word_name]))
    #     num += 1
    # tool.write_file("./dict/event_topic_relative.txt", temp, "w")

    print "输出结果如下"
    # 根据频繁模式热度重新排序并输出
    result = sorted(feature_array, key=lambda x: calculate_hot(doc_ids, x), reverse=True)
    for fc in result:
        if len(fc.feature_cut_array) > 0:
            print fc, calculate_hot(doc_ids, fc)


if __name__ == '__main__':
    lan_de_qi_ming()

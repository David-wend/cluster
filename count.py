# coding=utf-8

import Inverted_index
import tool
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from sklearn import tree
from sklearn import cross_validation
from IPython.display import Image, display
import matplotlib.pyplot as plt
from pandas import DataFrame
import jieba
import remove_duplicate

__author__ = 'david'


def get_main_class(array, num_set):
    '''获取数组中的主类并计算类个数所占的比重

    主类需要满足，该类未被映射，该类新闻在数组中占的比例最大

    :param
        array：正确聚类结果中某个类在预测聚类结果中的映射
        num_set：已经被映射的聚类标号的集合
    :return
        tag：主类标号
        pre：主类所占比重
        right_num：主类数目
    '''
    calculate_array = np.array([0] * (array.max() + 1))
    series = pd.value_counts(array)  # 获得各个元素的计数表
    for i in series.index:
        if i not in num_set:
            calculate_array[i] = series[i]
    right_num = calculate_array.max()
    pre = float(right_num) / len(array)
    tag = calculate_array.argmax()
    while tag in num_set:
        tag += 1
    return tag, pre, right_num


def get_pre(true_result, forecast_result):
    '''计算聚类结果的准确性

    将正确结果与聚类结果进行映射，将分错点标记为-2
    准确率计算公式：正确聚类的个数/样本总数

    :param
        true_result: 聚类正确结果数组
        forecast_result: 聚类预测结果数组
    :return
        pre：准确率
        forecast_result: 已将错误结果标记为-2的聚类预测结果数组
    '''

    true_result = np.array(true_result, dtype=float)
    forecast_result = np.array(forecast_result, dtype=float)
    temp_true_result = np.array(true_result)
    temp_forecast_result = np.array(forecast_result)
    last_pre = 0
    num_set = set()

    correspond_array = DataFrame([], index=['true_value', 'cluser_value', 'pre', 'right_num', 'len'])
    for i in range(len(np.unique(true_result))):
        temp_correspond_array = DataFrame(get_cluser_tag(temp_true_result, temp_forecast_result, num_set),
                                          columns=['true_value', 'cluser_value', 'pre', 'right_num', 'len'])
        temp_correspond_array = temp_correspond_array.sort_values(by=['right_num'], ascending=False)
        temp_tag_num = temp_correspond_array.index[0]
        num_set.add(temp_correspond_array['cluser_value'][temp_tag_num])
        num = temp_correspond_array['true_value'][temp_tag_num]
        boolean = temp_true_result != num
        temp_true_result = temp_true_result[boolean]
        temp_forecast_result = temp_forecast_result[boolean]
        correspond_array[i] = temp_correspond_array.ix[temp_tag_num]
    correspond_array = correspond_array.T

    for i in range(len(correspond_array.index)):
        pre = correspond_array['pre'][i]
        main_class_num = correspond_array['true_value'][i]
        lenth = correspond_array['len'][i]
        last_pre += pre * lenth
        cluser_value = correspond_array['cluser_value'][i]
        arr = np.array(boolean_calculate(true_result == main_class_num, forecast_result != cluser_value, 'and'))
        forecast_result[arr] += true_result[arr] / 100  # 将分错的点的类标记记为-2
        arr = np.array(boolean_calculate(true_result == main_class_num, forecast_result == cluser_value, 'and'))
        forecast_result[arr] = i  # 将分对的点与原来正确结果的类标号对应
    return last_pre / len(true_result), forecast_result


def get_cluser_tag(cluser_array, forecast_result, num_set):
    '''对正确结果与聚类结果进行映射

    :param
        cluser_array：正确聚类结果数组
        forecast_result：预测聚类结果数组
        num_set：已被映射聚类标号的集合
    :return
        correspond_array：DataFrame对象，column=['原始类号','对应类号','准确率','正确聚类个数','类总数']
    '''
    correspond_array = []
    for i in np.unique(cluser_array):
        temp_forecast_result = forecast_result[cluser_array == i]
        main_class_num, pre, right_num = get_main_class(temp_forecast_result, num_set)
        correspond_array.append([i, main_class_num, pre, right_num, len(temp_forecast_result)])
    return correspond_array


def boolean_calculate(arr1, arr2, calculate):  # 对两个数组进行布尔运算
    '''对两个数组的每一项进行布尔运算

    :param
        arr1：第一个数组
        arr2：第二个数组
        calculate：运算方式，可选['not','and','or']
    :return
        result：布尔运算结果
    '''
    result = [True] * len(arr1)
    if calculate == 'and':
        for i in range(len(arr1)):
            result[i] = arr1[i] and arr2[i]
    if calculate == 'or':
        for i in range(len(arr1)):
            result[i] = arr1[i] or arr2[i]
    if calculate == 'not':
        for i in range(len(arr1)):
            result[i] = not arr1[i]
    return result


def calculate_integrity(dictionary, word):
    word_freq = dictionary.word_freq_dic[dictionary.word_index_dic[word]]
    f_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[:-1], ""), 1)
    return float(word_freq) / f_word_freq


def calculate_stability(dictionary, word):
    word_freq = dictionary.word_freq_dic[dictionary.word_index_dic[word]]
    f_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[:-1], ""), 1)
    l_word_freq = dictionary.word_freq_dic.get(dictionary.word_index_dic.get(word[1:], ""), 1)
    return float(word_freq) / (f_word_freq + l_word_freq - word_freq + 1)


def calculate_independence_by_freq(dictionary, word):
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
    set_i, dict_i = dictionary.transform_term_info(word)
    f_word_set = set([])
    l_word_set = set([])
    for doc_id in set_i:
        for location_id in dict_i[doc_id].location_ids:
            if location_id > 0:
                f_word_set.add(dictionary.doc_dic[doc_id].words[location_id - 1])
            if location_id < len(dictionary.doc_dic[doc_id].words) - 1:
                l_word_set.add(dictionary.doc_dic[doc_id].words[location_id + 1])
    return [1 - float(1) / (len(f_word_set) + 1), 1 - float(1) / (1 + len(l_word_set))]


def get_co_name():
    i_dic = Inverted_index.InvertDic()
    i_dic.init_all_dic()
    candidate_list = i_dic.word_index_dic.keys()
    limit_dic = {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
    ids_dic = {}
    # result_dic = {}
    tool.write_file("./dict/word_co.txt", [], "w")
    for k in range(10):
        result_dic = {}
        for i in range(len(candidate_list)):
            for j in range(len(candidate_list)):
                if i == j:
                    continue
                if i_dic.add_term_bound(candidate_list[i], candidate_list[j]):
                    ids, locations = i_dic.get_co_occurrence_info(candidate_list[i], candidate_list[j])
                    if len(ids) > limit_dic.get(len(candidate_list[i]), 2):
                        i_dic.add_new_term(candidate_list[i], candidate_list[j])
                        new_word = candidate_list[i] + i_dic.index_word_dic[i_dic.word_comb_word_dic[
                            i_dic.word_index_dic[candidate_list[j]]][-1]]
                        result_dic[new_word] = len(ids)
                        ids_dic[new_word] = ids

        result_list = sorted(result_dic.items(), key=lambda x: x[1])
        lines = []
        for temp in result_list:
            try:
                lines.append(temp[0] + "@@" + str(temp[1]) + "@@" + str(
                    round(calculate_integrity(i_dic, temp[0]), 4)) + "@@" + str(
                    round(calculate_stability(i_dic, temp[0]), 4)) + "@@" + "##".join(
                    [str(round(x, 4)) for x in calculate_independence(i_dic, temp[0])]) + "@@" + "##".join(
                    [str(round(x, 4)) for x in calculate_independence_by_freq(i_dic, temp[0])]) + "@@" + "##".join(
                    [str(x) for x in ids_dic[temp[0]]]))
            except KeyError:
                print temp[0]
                continue
        tool.write_file("./dict/word_co.txt", lines, "a")
        try:
            del result_dic[u"新闻"]
            del result_dic[u"搜狐"]
        except:
            pass
        candidate_list = result_dic.keys()


def var_dump_word_tree(word, words, freq, values, doc_ids, word_index_dic):
    word_index = word_index_dic[word]
    print words[word_index], freq[word_index], values[word_index][0], values[word_index][1], \
        values[word_index][2], values[word_index][3]
    if len(word) > 2:
        return var_dump_word_tree(word[:-1], words, freq, values, doc_ids, word_index_dic), \
               var_dump_word_tree(word[1:], words, freq, values, doc_ids, word_index_dic)


def load_data():
    path = "./dict/word_co.txt"
    lines = tool.get_file_lines(path)
    words = []
    word_index_dic = {}
    values = []
    doc_ids = []
    freq = []
    num = 0
    for line in lines:
        arr = line.split("@@")
        words.append(arr[0].decode("utf8"))
        word_index_dic[arr[0].decode("utf8")] = num
        num += 1
        freq.append(int(arr[1]))
        brr = arr[4].split("##")
        values.append([float(arr[2]), float(arr[3]), float(brr[0]), float(brr[1])])
        doc_ids.append([int(x) for x in arr[6].split("##")])
    return words, freq, values, doc_ids, word_index_dic


def calculate_total_weight(freq, values):
    return freq * 0.1 + values[0] + values[1] + values[2] + values[3]


def remove_non_sense_word(words, freq, values):
    result = {}
    candidate_remove = {}
    for i in range(len(words)):
        if freq[i] > 2:
            if values[i][0] > 0.7 and values[i][1] > 0.52 and values[i][2] > 0.6:
                # print words[i], calculate_total_weight(freq[i], values[i])
                result[words[i]] = calculate_total_weight(freq[i], values[i])
                if words[i][:-1] in result:
                    candidate_remove[words[i][:-1]] = result[words[i][:-1]]
                    # if result[words[i][:-1]] < 4:
                    # del result[words[i][:-1]]
                if words[i][1:] in result:
                    candidate_remove[words[i][1:]] = result[words[i][1:]]
                    # if result[words[i][1:]] < 4:
                    # del result[words[i][1:]]
    result_list = sorted(result.items(), key=lambda x: x[1])  # 排序比较keys
    return result_list


def split_data_set(data, label, num, flag0=0, flag1=0):
    data = np.matrix(data)
    train_X = data[:num]
    train_Y = label[:num]
    if flag0 == 1:
        train_X_1 = train_X[np.where(train_Y == 1)]
        train_X_1 = train_X_1.repeat(2, axis=0)
        train_X_0 = train_X[np.where(train_Y == 0)]
        train_X_0 = train_X_0[:train_X_1.shape[0]]
        train_X = np.concatenate((train_X_0, train_X_1))
        train_Y = np.concatenate(
            (np.zeros(train_X_1.shape[0], dtype=np.int), np.ones(train_X_1.shape[0], dtype=np.int)))

    test_X = data[num:]
    test_Y = label[num:]
    if flag1 == 1:
        test_X_1 = test_X[np.where(test_Y == 1)]
        test_X_1 = test_X_1.repeat(2, axis=0)
        test_X_0 = test_X[np.where(test_Y == 0)]
        test_X_0 = test_X_0[:test_X_1.shape[0]]
        test_X = np.concatenate((test_X_0, test_X_1))
        test_Y = np.concatenate(
            (np.zeros(test_X_0.shape[0], dtype=np.int), np.ones(test_X_1.shape[0], dtype=np.int)))
    print len(train_X), len(train_Y), len(test_X), len(test_Y)
    return train_X, train_Y, test_X, test_Y


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
    word_i_set = set(word_i_doc_ids)
    word_j_set = set(word_j_doc_ids)
    return float(len(word_i_set & word_j_set)) / (np.sqrt(len(word_i_set)) * np.sqrt(len(word_j_set)))


def calculate_sim_by_cut():
    word_i_set = set(word_i_doc_ids)
    word_j_set = set(word_j_doc_ids)
    return float(len(word_i_set & word_j_set)) / (np.sqrt(len(word_i_set)) * np.sqrt(len(word_j_set)))

def get_word_distribution(word):
    pass


if __name__ == '__main__':
    i_dic = Inverted_index.InvertDic()
    i_dic.init_all_dic()
    # get_co_name()
    words, freq, values, doc_ids, word_index_dic = load_data()

    word_set = set([])
    word_remove_set = set([])
    word_index = train_clf()
    for w in word_index:
        word_set.add(words[w])
        word_remove_set.add(words[w][:-1])
        word_remove_set.add(words[w][1:])

    word_cut_array = []
    for word in word_set - word_remove_set:
        print word
        word_cut_array.append([x for x in jieba.cut(word)])

    for i in range(len(word_cut_array) - 1):
        for j in range(i + 1, len(word_cut_array)):
            if remove_duplicate.count_similar([word_cut_array[i]], word_cut_array[j]):
                print "".join(word_cut_array[i]), "".join(word_cut_array[j])
            print "".join(word_cut_array[i]), "".join(word_cut_array[j]), calculate_sim(
                doc_ids[word_index_dic["".join(word_cut_array[i])]],
                doc_ids[word_index_dic["".join(word_cut_array[j])]])

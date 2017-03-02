# coding=utf-8

import Inverted_index
import tool
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn import cross_validation
from IPython.display import Image, display
import pydotplus
import matplotlib.pyplot as plt

__author__ = 'david'


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
        doc_ids.append(arr[6].split("##"))
    return words, freq, values, doc_ids, word_index_dic


def calculate_total_weight(freq, values):
    return freq * 0.1 + values[0] + values[1] + values[2] + values[3]


def remove_non_sense_word(words, freq, values):
    result = {}
    candidate_remove = {}
    for i in range(len(words)):
        if freq[i] > 2:
            if values[i][0] > 0.6 and values[i][1] > 0.6 and values[i][2] > 0.49 \
                    and values[i][3] > 0.49 and np.mean([values[i][2:]]) > 0.49:
                # print words[i], calculate_total_weight(freq[i], values[i])
                result[words[i]] = calculate_total_weight(freq[i], values[i])
                if words[i][:-1] in result:
                    candidate_remove[words[i][:-1]] = result[words[i][:-1]]
                    # if result[words[i][:-1]] < 4:
                    del result[words[i][:-1]]
                if words[i][1:] in result:
                    candidate_remove[words[i][1:]] = result[words[i][1:]]
                    # if result[words[i][1:]] < 4:
                    del result[words[i][1:]]
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


if __name__ == '__main__':
    # i_dic = Inverted_index.InvertDic()
    # i_dic.init_all_dic()
    # get_co_name()

    # words, freq, values, doc_ids, word_index_dic = load_data()
    # result_list = remove_non_sense_word(words, freq, values)
    # print "==" * 10
    # for i in result_list:
    #     print i[0], i[1]

    # result = []
    # for i in range(len(words)):
    #     result.append(words[i] + "," + str(freq[i]) + "," + ",".join([str(x) for x in values[i]]) + "," + str(0))
    # tool.write_file("./dict/word_weight.txt", result ,"w")

    word_weights = pd.read_csv("./dict/word_weight.txt", header=None, sep=",")
    col_names = ["word_name", "freq", "integrity", "stability",
                 "independence_l", "independence_r", "label"]
    word_weights.columns = col_names
    label = word_weights["label"]
    words = word_weights["word_name"]
    word_weights.drop("label", axis=1, inplace=True)
    word_weights.drop("word_name", axis=1, inplace=True)

    train_x, train_y, test_x, test_y = split_data_set(word_weights, label, 100, flag0=0, flag1=0)
    lr_model = LogisticRegression(C=1.0, penalty='l2')
    lr_model.fit(word_weights, label)
    pre_y = lr_model.predict(word_weights)
    print classification_report(label, pre_y)
    print lr_model.coef_
    print lr_model.intercept_

    rt_clf = RandomForestClassifier(n_estimators=5)
    rt_clf.fit(word_weights, label)
    pre_y = rt_clf.predict(word_weights)
    print classification_report(label, pre_y)

    dt_clf = tree.DecisionTreeClassifier(max_depth=5)
    dt_clf.fit(word_weights, label)
    pre_y = dt_clf.predict(word_weights)
    print classification_report(label, pre_y)
    print words[pre_y == 1]

    # dot_data = tree.export_graphviz(dt_clf, out_file=None, feature_names=word_weights.columns, class_names="index",
    #                                 filled=True, rounded=True, special_characters=True)
    # graph = pydotplus.graph_from_dot_data(dot_data)
    # img = Image(graph.create_png())
    # display(img)
    # graph.write_pdf("data.pdf")

    scores = cross_validation.cross_val_score(lr_model, word_weights, label, cv=5)
    print scores.mean()
    scores = cross_validation.cross_val_score(rt_clf, word_weights, label, cv=5)
    print scores.mean()
    scores = cross_validation.cross_val_score(dt_clf, word_weights, label, cv=5)
    print scores.mean()

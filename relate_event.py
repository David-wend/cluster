# coding=utf-8

import os
import tool
import remove_duplicate
import jieba
import count
import numpy as np


def calculate_hot(doc_id_dic, freq_mode):
    """ 计算特征热度，计算公式为它所包含的新闻数目平方和的二次方,即sqrt(a**2+b**2)

    :param doc_id_dic:
    :param freq_mode:
    :return:
    """
    hot_value = 0
    for feature_cut_array_k in freq_mode.feature_cut_array:
        word = "".join(feature_cut_array_k)
        # try:
        # hot_value += len(doc_id_dic[word]) ** 2
        hot_value += len(doc_id_dic[word]) ** 2
        # except KeyError:
        #     hot_value += 1
    return np.sqrt(hot_value)


def calculate_event_sim(old_event, new_event):
    similar_num = 0
    old_event_cut = [[x for x in oe_one] for oe_one in old_event[1]]
    for ne_one in new_event[1]:
        if ne_one in old_event[1]:
            # similar_num += 1
            return True
        ne_one_cut = [x for x in ne_one]
        if remove_duplicate.count_similar(old_event_cut, ne_one_cut, 6,
                                          similar_word_limit=4):
            similar_num += 1
    if float(similar_num) / len(new_event) >= 0.8:
        return True
    else:
        return False


def merge_event(old_event, new_event, old_event_feature, new_event_feature, old_doc_ids, new_doc_ids):
    for ne_one in new_event[1]:
        if ne_one not in old_event_feature[old_event[0]]:
            old_event_feature[old_event[0]].append(ne_one)
            old_doc_ids[ne_one] = old_doc_ids.get(ne_one, []) + \
                                  new_doc_ids[ne_one]
        del new_doc_ids[ne_one]
    del new_event_feature[new_event[0]]


def update_doc_id(new_doc_id_dic, old_doc_id_dic, new_word, old_word):
    """

    :param new_doc_id_dic:
    :param old_doc_id_dic:
    :param new_word:
    :param old_word:
    :return:
    """
    new_doc_id_dic[new_word] = list(set(new_doc_id_dic.get(new_word, [])).union(set(old_doc_id_dic[old_word])))
    del old_doc_id_dic[old_word]
    return new_doc_id_dic


all_doc_ids = []
all_features = []

root_dir = "./dict/"
num = 0
for parent, dirnames, filenames in os.walk(root_dir):
    for dirname in dirnames:
        file_dir = root_dir + dirname
        # print dirname
        rows = tool.get_file_lines(file_dir + "/word_co.txt")
        temp_doc_ids = {}
        for row in rows:
            arr = row.split("@@", 7)
            temp_doc_ids[arr[0].decode("utf-8")] = [int(x) for x in arr[7].split("##")]
        all_doc_ids.append(temp_doc_ids)

        rows = tool.get_file_lines(file_dir + "/event_topic_relative.txt")
        temp_features = {}
        for row in rows:
            arr = row.split("@@", 2)
            temp_features[int(arr[0]) + num] = temp_features.get(int(arr[0]) + num, []) + [arr[2].decode("utf-8")]
        num += len(rows)
        all_features.append(temp_features)

# print all_doc_ids
# print all_features

for i in range(len(all_features)):
    # print i
    new_event_feature = all_features[i]
    new_doc_ids = all_doc_ids[i]
    for j in range(i):
        old_event_feature = all_features[j]
        old_doc_ids = all_doc_ids[j]
        for old_event in old_event_feature.items():
            for new_event in new_event_feature.items():
                if calculate_event_sim(old_event, new_event):  # 如果两个事件相似
                    merge_event(old_event, new_event, old_event_feature, new_event_feature, old_doc_ids, new_doc_ids)

# for i in all_doc_ids:
#     print i

feature_array = []
for i in range(len(all_features)):
    temp_all_feature = all_features[i]
    for temp_feature in temp_all_feature.items():
        nfc = count.FeatureCluster(temp_feature[1][0])
        for tfc in temp_feature[1][1:]:
            nfc.append_new_feature_cut(tfc)
        feature_array.append(nfc)

# 将特征文档空间模型转换为文档特征空间模型
doc_word_dic = {}
doc_ids = {}
word_index_dic = {}
word_index = 0
for i in range(len(all_features)):
    temp_all_feature = all_features[i]
    temp_all_doc_ids = all_doc_ids[i]
    for temp_feature in temp_all_feature.items():
        for fc in temp_feature[1]:
            word_index_dic[fc] = word_index
            word_index += 1
            doc_ids[fc] = doc_ids.get(fc, []) + temp_all_doc_ids[fc]
            for doc_id in temp_all_doc_ids[fc]:
                doc_word_dic[doc_id] = doc_word_dic.get(doc_id, []) + [fc]

un_num = 0
for i in doc_ids.items():
    if len(i[1]) != len(set(i[1])):
        un_num += 1
print "un_num", un_num

# 计算事件下每一个话题簇熵重叠度，越小越纯粹
entropy_dic = {}
for i in range(len(all_features)):
    temp_all_feature = all_features[i]
    temp_all_doc_ids = all_doc_ids[i]
    for temp_feature in temp_all_feature.items():
        for fc in temp_feature[1]:
            entropy_dic[fc] = count.calculate_entropy(temp_all_doc_ids[fc], doc_word_dic)
            # print word_name, calculate_entropy(doc_ids[word_index_dic[word_name]], doc_word_dic)

print num
print len(feature_array)

# for fc in feature_array:
#     # print fc, calculate_hot(doc_ids, fc)
#
#     # 根据上下位去重，如有“林丹出轨”去除“林丹出”
#     new_feature_cut_array = []
#     fca_sorted = sorted(fc.feature_cut_array, key=lambda x: len("".join(x)), reverse=False)
#     words_fca_dict = {"".join(fca): fca for fca in fca_sorted}
#     result = {}
#     for fca in fca_sorted:
#         word = "".join(fca)
#         similar_w = count.calculate_total_weight(freq[word], values[word])
#         result[word] = similar_w
#         new_feature_cut_array.append(words_fca_dict[word])
#         if word[:-1] in result:
#             if values[word][0] > 0.8:
#                 pass
#                 new_feature_cut_array.remove(words_fca_dict[word[:-1]])
#                 doc_ids = update_doc_id(doc_ids, word, word[:-1])
#                 del result[word[:-1]]
#         if word[1:] in result:
#             if values[word][0] > 0.8:
#                 pass
#                 new_feature_cut_array.remove(words_fca_dict[word[1:]])
#                 doc_ids = update_doc_id(doc_ids, word, word[1:])
#                 del result[word[1:]]
#     fc.feature_cut_array = new_feature_cut_array
#     # print fc
#
#     # 根据语义去重
#     new_feature_cut_array = []
#     tag = np.zeros(shape=len(fc.feature_cut_array))
#     fc.feature_cut_array = sorted(fc.feature_cut_array,
#                                   key=lambda x: len("".join(x)),
#                                   reverse=True)
#     for i in range(len(fc.feature_cut_array)):
#         if tag[i] == 0:
#             tag[i] = 1
#             new_feature_cut_array.append(fc.feature_cut_array[i])
#             for j in range(len(fc.feature_cut_array)):
#                 if i == j:
#                     continue
#                 if tag[j] == 0:
#                     if remove_duplicate.count_similar([fc.feature_cut_array[i]], fc.feature_cut_array[j], 0.8,
#                                                       similar_word_limit=1):
#                         doc_ids = update_doc_id(doc_ids, "".join(fc.feature_cut_array[i]),
#                                                 "".join(fc.feature_cut_array[j]))
#                         tag[j] = 1
#
#     fc.feature_cut_array = new_feature_cut_array
#     # print fc

# 讲文档优先归类到熵重叠度小的频繁模式
entropy_list = sorted(entropy_dic.items(), key=lambda x: x[1])
news_relative = {}
for i in entropy_list:
    # print "get"
    news_relative[i[0]] = doc_ids[i[0]]
    # 以下部分将划分变为硬划分
    # for doc_id in doc_ids[i[0]]:
    #     try:
    #         for word_name in doc_word_dic[doc_id]:
    #             if word_name != i[0]:
    #                 # 这里每次不是只删一个
    #                 # doc_ids[word_name].remove(doc_id)
    #                 doc_ids[word_name] = list(set(doc_ids[word_name]))
    #                 doc_ids[word_name].remove(doc_id)
    #         if doc_id in doc_word_dic:
    #             # print doc_id,
    #             del doc_word_dic[doc_id]
    #     except:
    #         print "error"

# 读取文档标题
doc_dic = {}
for line in tool.get_file_lines("./dict/filter_doc.txt"):
    arr = line.split("@@@@")
    brr = arr[1].split("##")
    doc_dic[int(arr[0])] = brr[0]

# 输出频繁模式及相关文档
temp = []
for item in news_relative.items():
    # print item[0], item[1]
    for doc_id in set(item[1]):
        # print "\t" + doc_dic[doc_id]
        temp.append(str(word_index_dic[item[0]]) + "@@" + str(doc_id) + "@@" + item[0])
tool.write_file("./dict/topic_news_relative.txt", temp, "w")

# 保存话题与事件的联系
temp = []
num = 0
for fc in feature_array:
    for feature_cut_array_k in fc.feature_cut_array:
        word_name = "".join(feature_cut_array_k)
        temp.append(str(num) + "@@" + str(word_index_dic[word_name]) + "@@" + word_name)
    num += 1
tool.write_file("./dict/event_topic_relative.txt", temp, "w")

print "结果如下所示："
result = sorted(feature_array, key=lambda x: calculate_hot(doc_ids, x), reverse=True)
for fc in result:
    if len(fc.feature_cut_array) > 0:
        print fc, calculate_hot(doc_ids, fc)

# coding=utf-8

import os
import tool
import remove_duplicate
import jieba
import count


def calculate_event_sim(old_event, new_event):
    similar_num = 0
    old_event_cut = [[x for x in oe_one] for oe_one in old_event[1]]
    for ne_one in new_event[1]:
        if ne_one in old_event[1]:
            return True
        ne_one_cut = [x for x in ne_one]
        if remove_duplicate.count_similar(old_event_cut, ne_one_cut, 3,
                                          similar_word_limit=3):
            similar_num += 1
    if float(similar_num) / len(new_event) >= 0.5:
        return True
    else:
        return False


def merge_event(old_event, new_event, old_event_feature, new_event_feature, old_doc_ids, new_doc_ids):
    for ne_one in new_event[1]:
        try:
            if ne_one not in old_event_feature[old_event[0]]:
                old_event_feature[old_event[0]].append(ne_one)
            old_doc_ids[ne_one] = old_doc_ids.get(ne_one, []) + new_doc_ids[ne_one]
            del new_doc_ids[ne_one]
        except KeyError:
            continue
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

        rows = tool.get_file_lines(file_dir + "/topic_news_relative.txt")
        temp_doc_ids = {}
        for row in rows:
            arr = row.split("@@", 2)
            temp_doc_ids[arr[2].decode("utf-8")] = temp_doc_ids.get(arr[2].decode("utf-8"), []) + [int(arr[1])]
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
    new_event_feature = all_features[i]
    new_doc_ids = all_doc_ids[i]
    for j in range(i):
        old_event_feature = all_features[j]
        old_doc_ids = all_doc_ids[j]
        for old_event in old_event_feature.items():
            for new_event in new_event_feature.items():
                if calculate_event_sim(old_event, new_event):  # 如果两个事件相似
                    merge_event(old_event, new_event, old_event_feature, new_event_feature, old_doc_ids, new_doc_ids)

# 将特征文档空间模型转换为文档特征空间模型
doc_word_dic = {}
for i in range(len(all_features)):
    temp_all_feature = all_features[i]
    temp_all_doc_ids = all_doc_ids[i]
    for temp_feature in temp_all_feature.items():
        for fc in temp_feature[1]:
            try:
                for doc_id in temp_all_doc_ids[fc]:
                    doc_word_dic[doc_id] = doc_word_dic.get(doc_id, []) + [fc]
            except KeyError:
                continue

# 计算事件下每一个话题簇熵重叠度，越小越纯粹
entropy_dic = {}
for i in range(len(all_features)):
    temp_all_feature = all_features[i]
    temp_all_doc_ids = all_doc_ids[i]
    for temp_feature in temp_all_feature.items():
        for fc in temp_feature:
            entropy_dic[fc] = count.calculate_entropy(temp_all_doc_ids[fc], doc_word_dic)
        # print word_name, calculate_entropy(doc_ids[word_index_dic[word_name]], doc_word_dic)

print num

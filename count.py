# coding=utf-8

__author__ = 'david'
import Inverted_index
import tool


def transform_term_info(inverted_index, word):
    word_set = set([])
    word_dict = {}
    for i_term in inverted_index.word_term_dic[inverted_index.word_index_dic[word]]:
        word_set.add(i_term.doc_id)
        word_dict[i_term.doc_id] = i_term
    return word_set, word_dict


def calculate_co_occurrence(set_i, dict_i, set_j, dict_j):
    co_num = 0
    for k in set_i & set_j:
        list_i = sorted(dict_i[k].location_ids)
        list_j = sorted(dict_j[k].location_ids)
        if list_i[0] > list_j[-1]:
            break
        for id_i in list_i:
            for id_j in list_j:
                if id_j<id_i or id_i<id_j-2:
                    break
                co_num += 1
    return co_num


if __name__ == '__main__':

    inverted_index_dic = Inverted_index.InvertDic()
    candidate_list = inverted_index_dic.word_index_dic.keys()
    candidate_list = list(set(candidate_list) - tool.get_stop_word())
    result_dic = {}

    for i in range(len(candidate_list) - 1):
        for j in range(i+1, len(candidate_list)):
            i_set, i_dic = transform_term_info(inverted_index_dic, candidate_list[i])
            j_set, j_dic = transform_term_info(inverted_index_dic, candidate_list[j])
            co_num = calculate_co_occurrence(i_set, i_dic, j_set, j_dic)
            if co_num > 15:
                result_dic[candidate_list[i] + "##" + candidate_list[j]] = result_dic.get(
                    candidate_list[i] + "##" + candidate_list[j], 0) + co_num
            co_num = calculate_co_occurrence(j_set, j_dic, i_set, i_dic)
            if co_num > 15:
                result_dic[candidate_list[j] + "##" + candidate_list[i]] = result_dic.get(
                    candidate_list[j] + "##" + candidate_list[i], 0) + co_num

    result_list = sorted(result_dic.items(), key=lambda x: x[1])
    lines = []
    for temp in result_list:
        lines.append(temp[0] + "##" + str(temp[1]))
    tool.write_file("./dict/word_co.txt", lines, "a")



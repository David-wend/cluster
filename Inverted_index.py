# coding=utf-8

__author__ = 'david'
from datetime import datetime
import doc_proccess
import tool
from doc_proccess import Doc

time_format = "%Y-%m-%d %H:%M:%S"


class Term:
    """ 倒排索引条目，每个实体保留一个单词在一篇文档的信息

    如果单词在文档中出现过，创建Term类保留信息

            文章1     文章2     文章3
    单词1   Term
    单词2             Term
    单词3                       Term

    """

    def __init__(self, word_id, doc_id, tf):
        """

        :param word_id: 单词编号
        :param doc_id: 文档标号
        :param tf: 单词在文档中出现的次数
        :attribute location_ids: 数组，表示词在文章中出现的下标，ex.[1,3,7]
        """
        self.word_id = word_id
        self.doc_id = doc_id
        self.tf = tf
        self.location_ids = []

    def append_location(self, ids):
        """ 添加单词在文档中出现的位置信息

        :param ids:
        :return:
        """
        self.location_ids += ids

    def __str__(self):
        return str(self.word_id) + "@@@@" + str(self.doc_id) + "@@@@" + str(self.tf) + "@@@@" \
               + "##".join([str(x) for x in self.location_ids])


class CombTerm(Term):
    def __init__(self, word_id, doc_id, tf, term_len):
        Term.__init__(self, word_id, doc_id, tf)
        self.term_len = term_len
        self.comb_words = []

    def append_comb_words(self, word_ids):
        self.comb_words += word_ids

    def append_location(self, ids):
        Term.append_location(self, ids)

    def __str__(self):
        return str(self.word_id) + "@@@@" + str(self.doc_id) + "@@@@" + str(self.tf) + "@@@@" + str(
            self.term_len) + "@@@@" + "##".join([str(x) for x in self.location_ids]) + "@@@@" + "##".join(
            [str(x) for x in self.comb_words])


class InvertDic:
    """ 倒排索引词典

    """

    def __init__(self):
        """

        :attribute word_index_dic: 词典，记录单词编号，eq.{单词:单词编号}
        :attribute word_freq_dic: 词典，记录单词总词频，eq.{单词编号:单词总词频}
        :attribute word_term_dic: 词典，存储倒排索引条目信息，eq.{单词编号:[Term1，Term2]}
                                  Term类保存了一个单词在一篇文档中的信息
        :attribute word_df_dic: 词典，记录单词的文档频率，eq.{单词编号:单词文档频率}
        :attribute doc_dic: 词典，eq.{文档编号:文档标题##文档正文}
        :attribute doc_len: 整数，表示现有文档数量
        """

        self.word_comb_term_dic = {}
        self.word_index_dic = {}
        self.word_freq_dic = {}
        self.word_term_dic = {}
        self.word_df_dic = {}
        self.doc_dic = {}
        self.doc_len = doc_proccess.Doc.get_lasted_doc_id() + 1
        self.word_num = 0
        self.init_all_dic()

    def init_all_dic(self):
        self.get_doc_dic()
        self.get_word_df_dic()
        self.get_word_freq_dic()
        self.get_word_index_dic()
        self.get_word_term_dic()
        self.get_word_comb_term_dic()

    def save_word_comb_term_dic(self):
        lines = []
        for it in self.word_comb_term_dic.items():
            for t in it[1]:
                lines.append(t.__str__())
        tool.write_file("./dict/word_comb_term_dic.txt", lines, "w")

    def save_word_df_dic(self):
        lines = []
        for it in self.word_df_dic.items():
            lines.append(str(it[0]) + "\t" + str(it[1]))
        tool.write_file("./dict/word_df_dic.txt", lines, "w")

    def save_word_index_dic(self):
        lines = []
        for it in self.word_index_dic.items():
            lines.append(it[0] + "\t" +
                         str(it[1]))
        tool.write_file("./dict/word_index_dic.txt", lines, "w")

    def save_word_freq_dic(self):
        lines = []
        for it in self.word_freq_dic.items():
            lines.append(str(it[0]) + "\t" + str(it[1]))
        tool.write_file("./dict/word_freq_dic.txt", lines, "w")

    def save_word_term_dic(self):
        lines = []
        for it in self.word_term_dic.items():
            for t in it[1]:
                lines.append(t.__str__())
        tool.write_file("./dict/word_term_dic.txt", lines, "w")

    def get_doc_dic(self):
        lines = tool.get_file_lines("./dict/doc.txt")
        for line in lines:
            temp = line.split("@@@@")
            info = temp[1].split("##", 3)
            self.doc_dic[int(temp[0])] = doc_proccess.Doc(info[0], info[3], info[1], datetime.strptime(
                info[2], time_format), int(temp[0]))

    def get_word_df_dic(self):
        lines = tool.get_file_lines("./dict/word_df_dic.txt")
        for line in lines:
            temp = line.split("\t")
            self.word_df_dic[int(temp[0])] = int(temp[1])

    def get_word_index_dic(self):
        lines = tool.get_file_lines("./dict/word_index_dic.txt")
        for line in lines:
            temp = line.split("\t")
            try:
                self.word_index_dic[temp[0].decode("utf-8")] = int(temp[1])
                self.word_num += 1
            except:
                print "error"
                continue

    def get_word_freq_dic(self):
        lines = tool.get_file_lines("./dict/word_freq_dic.txt")
        for line in lines:
            temp = line.split("\t")
            self.word_freq_dic[int(temp[0])] = int(temp[1])

    def get_word_term_dic(self):
        lines = tool.get_file_lines("./dict/word_term_dic.txt")
        for line in lines:
            temp = line.split("@@@@")
            t = Term(int(temp[0]), int(temp[1]), int(temp[2]))
            t.append_location([int(x) for x in temp[3].split("##")])
            self.word_term_dic[int(temp[0])] = self.word_term_dic.get(int(temp[0]), []) + [t]

    def get_word_comb_term_dic(self):
        lines = tool.get_file_lines("./dict/word_comb_term_dic.txt")
        for line in lines:
            temp = line.split("@@@@")
            t = CombTerm(int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]))
            t.append_location([int(x) for x in temp[4].split("##")])
            t.append_comb_words([int(x) for x in temp[5].split("##")])
            self.word_comb_term_dic[int(temp[0])] = self.word_term_dic.get(int(temp[0]), []) + [t]

    def update_df_dic(self, words):
        """ 更新文档频率

        :param words:
        :return:
        """
        for word in set(words):
            self.word_df_dic[self.word_index_dic[word]] = self.word_df_dic.get(self.word_index_dic[word], 0) + 1

    def update_invert_index(self, doc):
        """ 更新倒排索引词典，可以将新的文章添加到倒排索引词典内

        :param doc: Doc类
        :return:
        """
        word_id = len(self.word_index_dic)
        self.doc_len += 1
        n_set = set()
        for word in doc.words:
            if word not in self.word_index_dic:
                self.word_index_dic[word] = word_id
                self.word_freq_dic[self.word_index_dic[word]] = 1
                word_id += 1
            else:
                self.word_freq_dic[self.word_index_dic[word]] += 1
            if word not in n_set:
                n_set.add(word)
                t = Term(self.word_index_dic[word], doc.doc_id, doc.freq_dic[word])
                t.append_location(doc.location_dic[word])
                self.word_term_dic[self.word_index_dic[word]] = self.word_term_dic.get(self.word_index_dic[word],
                                                                                       []) + [t]
        self.update_df_dic(doc.words)
        self.doc_dic[doc.doc_id] = doc
        tool.write_file("./dict/doc.txt", [doc.__str__()], "a")

    def get_co_occurrence_info(self, set_i, dict_i, set_j, dict_j):
        ids = []
        locations = []
        for k in set_i & set_j:
            temp = []
            list_i = sorted(dict_i[k].location_ids)
            list_j = sorted(dict_j[k].location_ids)
            if list_i[0] > list_j[-1]:
                continue
            for id_i in list_i:
                for id_j in list_j:
                    if id_i == id_j - 1:
                        ids.append(k)
                        temp.append(id_i)
            if len(temp) > 0:
                locations.append(temp)
        return ids, locations

    def add_new_term(self, word_i, word_j, is_comb_term=False):
        if word_i + word_j in self.word_index_dic:
            print "组合词已在词典"
            return
        if word_i not in self.word_index_dic or word_j not in self.word_index_dic:
            print "待组合词不在词典"
            return

        word_i_set, word_i_dic = self.transform_term_info(word_i, is_comb_term)
        word_j_set, word_j_dic = self.transform_term_info(word_j, is_comb_term)
        doc_ids, doc_locations = self.get_co_occurrence_info(word_i_set, word_i_dic, word_j_set, word_j_dic)

        if len(doc_ids) != len(doc_locations):
            print "数组越位"
            return

        self.word_index_dic[word_i + word_j] = self.word_num
        self.word_num += 1
        self.word_df_dic[word_i + word_j] = len(doc_ids)
        for i in range(len(doc_ids)):
            self.word_freq_dic[word_i + word_j] = self.word_freq_dic.get(word_i + word_j, 0) + len(doc_locations[i])
            t = CombTerm(self.word_index_dic[word_i + word_j], doc_ids[i], len(doc_locations[i]), 2)
            t.append_location(doc_locations[i])
            t.append_comb_words([self.word_index_dic[word_i], self.word_index_dic[word_j]])
            self.word_comb_term_dic[self.word_index_dic[word_i + word_j]] = self.word_comb_term_dic.get(
                self.word_index_dic[word_i + word_j],
                []) + [t]

    def transform_term_info(self, word, is_comb_term=False):
        word_set = set([])
        word_dict = {}
        if not is_comb_term:
            term_dic = self.word_term_dic
        else:
            term_dic = self.word_comb_term_dic
        for i_term in term_dic[self.word_index_dic[word]]:
            word_set.add(i_term.doc_id)
            word_dict[i_term.doc_id] = i_term
        return word_set, word_dict

    def transform_term_to_comb_term(self):
        for it in self.word_term_dic.items():
            for t in it[1]:
                ct = CombTerm(t.word_id, t.doc_id, t.tf, 1)
                ct.append_location(t.location_ids)
                ct.append_comb_words([t.word_id])
                self.word_comb_term_dic[t.word_id] = self.word_comb_term_dic.get(t.word_id, []) + [ct]


if __name__ == '__main__':
    # 初始化词典
    self = InvertDic()
    # doc_id = Doc.get_lasted_doc_id() + 1
    # 保存更新好的词典
    # self.save_word_df_dic()
    # self.save_word_freq_dic()
    # self.save_word_index_dic()
    # self.save_word_term_dic()
    # print self.word_index_dic[u"林丹"]
    # print self.word_index_dic[u"出轨"]
    # self.add_new_term(u"林丹", u"出轨")
    # print self.word_comb_term_dic[self.word_index_dic[u"林丹" + u"出轨"]]
    self.transform_term_to_comb_term()
    self.save_word_comb_term_dic()

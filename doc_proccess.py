# coding=utf-8


__author__ = 'david'
from datetime import datetime
import re
import tool
import jieba.posseg as pseg
time_format = "%Y-%m-%d %H:%M:%S"


class Doc:
    def __init__(self, title, doc_string, news_type, time, doc_id=0):
        """
        :param title: 文章标题
        :param doc_string: 文章内容
        :param doc_id: 文章编号
        :param news_type: 文章类型
        :param time: 发布时间
        :attribute paragraphs: 一维数组，以"\n|\r\n"将正文切分成多个段落，ex.[段落1，段落2]
        :attribute sentences: 二维数组，以"。|！"将段落切分成多个句子，ex.[[段落1的句子1],[段落2的句子1],[]]
        :attribute words: 一维数组，去除标点符号后剩下单词数组，ex.[词1，词2]
        :attribute words_without_f: 一维数组，未去除标点符号后剩下单词数组，ex.[词1，词2]
        :attribute freq_dic: 词典，表示每个词及对应的词频，ex.{词1:3,词2:3}
        :attribute location_dic: 词典，表示每个词在文章中出现的下标，ex.{词1:[1,2,3],词2:[4,5,6]}
        """
        if not isinstance(doc_string, unicode):
            self.doc_string = doc_string.decode('utf8')
        else:
            self.doc_string = doc_string
        self.title = title
        self.doc_id = doc_id
        if time is None:
            self.time = datetime.now()
        else:
            self.time = time
        self.news_type = news_type
        self.paragraphs = []
        self.sentences = []
        self.words = []
        self.words_without_f = []
        self.freq_dic = {}
        self.location_dic = {}
        self.split_title_word()
        self.calculate_freq_location()

    def split_paragraph(self):
        """ 切分段落

        :return:
        """
        para_p = re.compile(ur"\n|\r\n")
        self.paragraphs = para_p.split(self.doc_string)

    def split_sentence(self):
        """ 切分句子

        :return:
        """
        sent_p = re.compile(u"。|！")
        self.sentences = [sent_p.split(para_string) for para_string in self.paragraphs]

    def split_title_word(self):
        """ 切分标题单词单词

        :return:
        """

        for term in pseg.cut(self.title):
            self.words_without_f.append(term.word)
            if term.flag != u"x":
                self.words.append(term.word)

    def split_word(self):
        """ 切分单词

        :return:
        """
        for para in self.sentences:
            for sent in para:
                for term in pseg.cut(sent):
                    self.words_without_f.append(term.word)
                    if term.flag != u"x":
                        self.words.append(term.word)

    def calculate_freq_location(self):
        """ 统计每个词的频率及位置

        :return:
        """
        for i in range(len(self.words)):
            self.freq_dic[self.words[i]] = self.freq_dic.get(self.words[i], 0) + 1
            self.location_dic[self.words[i]] = self.location_dic.get(self.words[i], []) + [i]

    @staticmethod
    def get_lasted_doc_id():
        """ 获取最新的文档编号

        :return:
        """
        lines = tool.get_file_lines("./dict/doc.txt")
        try:
            lasted_id = int(lines[-1].split("@@@@")[0])
        except IndexError or TypeError:
            lasted_id = 0
        return lasted_id

    @staticmethod
    def split_queries(sentence):
        """
        对查询语句进行分词
        :param sentence:
        :return: 已分词列表
        """

        filter_words = []
        for term in pseg.cut(sentence):
            if term.flag != u"x":
                filter_words.append(term.word)
        return filter_words

    def __str__(self):
        # print type(str(self.doc_id))
        # print type(self.doc_string)
        # print type(self.doc_string.encode("utf8").decode("utf8"))
        return str(self.doc_id) + "@@@@" + self.title + "##" + self.news_type + "##" + datetime.strftime(
            self.time, time_format) + "##" + self.doc_string.encode("utf8")


if __name__ == '__main__':
    content = u"在这一年中，中国的改革开放和现代化建设继续向前迈进。国民经济保持了“高增长、低通胀”" \
              u"的\n良好发展态势。农业生产再次获得好的收成，企业改革继续深化，人民生活进一步改善。对外" \
              u"经济技术合作与交流不断扩大"

    d = Doc("一个新闻标题", content, "社会", datetime.now())
    print d.__str__()

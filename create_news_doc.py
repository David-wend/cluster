# coding=utf-8

import Inverted_index
import doc_proccess
import tool
import sql_tool


def insert_doc(data):
    i = Inverted_index.InvertDic()
    # doc_id = doc_proccess.Doc.get_lasted_doc_id() + 1
    doc_rows = tool.get_file_lines("./dict/filter_doc.txt")
    for row in doc_rows:
        temp = row.split("@@@@", 1)
        news = temp[1].split("##", 3)
        title = news[0].decode("UTF-8")
        content = news[3].decode("UTF-8")
        datetime = news[2]
        news_type = news[1].decode("UTF-8")
        doc_id = int(temp[0])
        d = doc_proccess.Doc(title, content, news_type, datetime, doc_id)
        i.update_invert_index(d)
        print news[0] + 'done'

    i.save_word_df_dic()
    i.save_word_freq_dic()
    i.save_word_index_dic()
    i.save_word_term_dic()

if __name__ == '__main__':
    news_type_list = ['军事', '体育', '科技', '娱乐', '社会', '国际', '国内', '数码']
    news_type = '数码'
    # sql = "SELECT `news_title` , `news_content` , `news_datetime` , `news_website_type` FROM `news` where" \
    #       " news_title like '%出轨%' ORDER BY `news_datetime` DESC LIMIT 0 , 200"
    # news_rows = sql_tool.select(sql)
    news_rows = []
    # print len(news_rows)
    insert_doc(news_rows)

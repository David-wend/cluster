# coding=utf-8

import sql_tool
from datetime import datetime
import count
import tool
import numpy as np
import jieba.posseg as pseg
import Inverted_index
from collections import Counter
import jieba
import create_news_doc


def insert_topic():
    words, freq, values, doc_ids, word_index_dic = count.load_data()
    topic_names = u"谌龙@@林丹@@李永波@@神秘女@@李宗伟@@出轨门@@谢杏芳@@原谅林丹@@林丹承认@@孕期出轨@@出轨事件@@林丹出轨@@" \
                  u"营销@@罗尔@@民政局@@三套房@@白血病@@罗一笑@@卖房救女@@罗尔回应@@罗尔事件@@罗一笑捐款@@罗一笑父亲@@罗一笑事件" \
                  u"@@裸贷@@女生裸贷@@女大学生"
    temp = []
    for topic_name in topic_names.split("@@"):
        temp.append([word_index_dic[topic_name], "", 2, topic_name, 1, datetime.now(), ""])

    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic values(%s, %s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_topic_news_relative():
    temp = []
    for line in tool.get_file_lines("./dict/topic_news_relative.txt"):
        arr = line.split("@@")
        temp.append([int(arr[0]), int(arr[1])])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic_news_relative(topic_id, news_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_event_topic_relative():
    temp = []
    for line in tool.get_file_lines("./dict/event_topic_relative.txt"):
        arr = line.split("@@")
        temp.append([int(arr[0]), int(arr[1])])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_event_topic_relative(event_id, topic_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def update_topic_datetime():
    sql = "select topic_id from yunshan_topic"
    topic_rows = sql_tool.select(sql)
    for row in topic_rows:
        sql = "select news_datetime from yunshan_news where news_id in " \
              "(select news_id from yunshan_topic_news_relative where topic_id = %d) " \
              "and news_datetime != '0000-00-00 00:00:00' order by news_datetime asc limit 1" % row[0]
        datetime_rows = sql_tool.select(sql)
        try:
            sql = "update yunshan_topic set topic_datetime = '%s' where topic_id = %d " % \
                  (datetime_rows[0][0].strftime("%Y-%m-%d %H:%M:%S"), row[0])
            print sql
        except:
            sql = "update yunshan_topic set topic_datetime = '2016-11-17 21:09:39' where topic_id = %d " % \
                  (row[0])
            print sql
            continue


def update_event_datetime():
    sql = "select event_id from yunshan_event"
    event_rows = sql_tool.select(sql)
    for row in event_rows:
        sql = "select topic_datetime from yunshan_topic where topic_id in " \
              "(select topic_id from yunshan_event_topic_relative where event_id = %d) " \
              "and topic_datetime != '0000-00-00 00:00:00' order by topic_datetime asc limit 1" % row[0]
        datetime_rows = sql_tool.select(sql)
        try:
            sql = "update yunshan_event set event_datetime = '%s' where event_id = %d " % \
                  (datetime_rows[0][0].strftime("%Y-%m-%d %H:%M:%S"), row[0])
            print sql
        except:
            sql = "update yunshan_event set event_datetime = '2016-11-17 21:09:39' where topic_id = %d " % \
                  (row[0])
            print sql
            continue


def update_topic_img():
    sql = "select topic_id from yunshan_topic"
    topic_rows = sql_tool.select(sql)
    for row in topic_rows:
        sql = "select news_image_url from yunshan_news where news_id in " \
              "(select news_id from yunshan_topic_news_relative where topic_id = %d) " \
              "and news_image_url != '' order by news_datetime asc limit 1" % row[0]
        # print sql
        img_rows = sql_tool.select(sql)
        # print img_rows
        try:
            sql = "update yunshan_topic set topic_img_url = '%s' where topic_id = %d " % \
                  (img_rows[0][0], row[0])
            print sql
            sql_tool.select(sql)
        except:
            sql = "update yunshan_topic set topic_img_url = '无图片' where topic_id = %d " % \
                  (row[0])
            sql_tool.select(sql)
            continue


def insert_topic_evaluation_object_relative():
    sql = "select topic_id from yunshan_topic where topic_id in (select topic_id " \
          "from yunshan_event_topic_relative where event_id = 4)"
    topic_rows = sql_tool.select(sql)
    print topic_rows
    temp = []
    for row in topic_rows:
        temp.append([row[0], 9])
        # temp.append([row[0], 7])
        # temp.append([row[0], 8])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic_evaluation_object_relative(topic_id, evaluation_object_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_web_num():
    sql = "select topic_id from yunshan_topic where topic_id != 0 and topic_id != 1"
    topic_rows = sql_tool.select(sql)
    temp = []
    for row in topic_rows:
        arr = [int(x) for x in np.random.random(size=5) * 10]
        temp.append([row[0], arr[0], arr[1], arr[2], arr[3], arr[4]])

    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_web_num values(%s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_topic_keyword_relative():
    event_id = 4
    sql = "select topic_id from yunshan_event_topic_relative where event_id = %d " % event_id
    topic_rows = sql_tool.select(sql)
    temp = []
    temp_e = []
    temp_e.append([event_id, 5, 2])
    temp_e.append([event_id, 4, 2])
    for row in topic_rows:
        temp.append([row[0], 5, 2])
        temp.append([row[0], 4, 2])
        # temp.append([row[0], 2, 2])
        # temp.append([row[0], 3, 2])
        # temp_e.append([event_id, 5, 2])
        # temp_e.append([event_id, 4, 2])
        # temp_e.append([event_id, 2, 2])
        # temp_e.append([event_id, 3, 2])

    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_event_keyword_relative values(%s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp_e)

    # sql = "insert into yunshan_topic_keyword_relative values(%s, %s, %s)"
    # sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def add_new_word(dictionary, word):
    for i in range(len(word) - 1):
        for j in range(len(word) - i - 1):
            # print word[j:i + j + 1], word[j + 1:j + i + 2]
            i_dic.add_new_term(word[j:i + j + 1], word[j + 1:j + i + 2])
    return dictionary


def p(arr):
    return [round(x, 1) for x in arr]


if __name__ == '__main__':
    # insert_topic_keyword_relative()
    # i_dic = Inverted_index.InvertDic()
    # i_dic.init_all_dic()
    # print count.calculate_fm_high_freq_day(i_dic, u"台")
    # print count.calculate_novelty(i_dic, u"男")
    # print count.calculate_novelty(i_dic, u"女")

    # create_news_doc.insert_doc_from_mongodb()
    # create_news_doc.connect_mongodb()

    i_dic = Inverted_index.InvertDic()
    i_dic.init_all_dic()
    words, freq, values, doc_ids, word_index_dic = count.load_data()
    add_new_word(i_dic, u"人大代表")
    add_new_word(i_dic, u"两会")
    add_new_word(i_dic, u"政协")
    add_new_word(i_dic, u"新闻")
    add_new_word(i_dic, u"事件")
    print p(count.calculate_novelty(i_dic, u"人大代表"))
    print p(count.calculate_novelty(i_dic, u"两会"))
    print p(count.calculate_novelty(i_dic, u"政协"))
    print p(count.calculate_novelty(i_dic, u"新闻"))
    print p(count.calculate_novelty(i_dic, u"事件"))


    # print i_dic.word_index_dic[u"美联储官员"], i_dic.word_index_dic[u"李克强回应"]
    # print count.calculate_dtw(i_dic, u"美联储官员", u"李克强回应"), count.calculate_time_overlapping_rate(i_dic, u"美联储官员", u"李克强回应")
    # print count.calculate_dtw(i_dic, u"人大", u"政协"), count.calculate_time_overlapping_rate(i_dic, u"人大", u"政协")
    # print count.calculate_dtw(i_dic, u"两会", u"政协"), count.calculate_time_overlapping_rate(i_dic, u"两会", u"政协")

    a = [1, 2, 3]
    print np.sort(a)
    # b = [2, 3, 4]
    # print float(len(set(a) & set(b))) / len(set(a) | set(b))
    # print tool.get_dtw(a, [100+x for x in a])

# select news_datetime from yunshan_news where news_id in (select news_id from yunshan_topic_news_relative where topic_id = 152) and news_datetime != "0000-00-00 00:00:00" order by news_datetime asc limit 1
# select topic_datetime from yunshan_topic where topic_id in (select topic_id from yunshan_event_topic_relative where event_id = 2) and topic_datetime != "0000-00-00 00:00:00" order by topic_datetime asc limit 1
# select news_image_url from yunshan_news where news_id in (select news_id from yunshan_topic_news_relative where topic_id = 152) and news_image_url is not null order by news_datetime asc limit 1

# coding=utf-8

import sql_tool
import sl_tool


def insert_news(conn, cursor):
    sql = "select news_id, news_website_id, news_website_type, news_url, news_title, " \
          "news_content, news_datetime, news_source, news_source_url, news_image, " \
          "news_author, news_comment_url_args from news where news_title like '%林丹%'" \
          "or news_title like '%罗尔%' or news_title like '%裸贷%'"

    data = sql_tool.select(sql)
    sql = "insert into yunshan_news values(%s,%s,%s,%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, data)


def insert_comment(conn, cursor):
    sql = "select news_comment_id, news_id, news_comment_content, " \
          "news_comment_datetime, news_comment_goodnumber from news_comment " \
          "where news_id in (select news_id from yunshan_news where news_title " \
          "like '%裸贷%') limit 15"
    tuples = sql_tool.select(sql)
    sql = "insert into yunshan_top_comment(comment_id, news_id, comment_content," \
          "comment_datetime, comment_good_number) values(%s,%s,%s,%s,%s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, tuples)


def insert_topic_news_relative(conn, cursor):
    sql = "select news_id from yunshan_news where news_title like '%林丹%'"
    data = sql_tool.select(sql)
    results = []
    for i in data:
        results.append([i[0], long(0)])
    sql = "insert into yunshan_topic_news_relative values(%s,%s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, results)



if __name__ == '__main__':
    conn, cursor = sql_tool.connect_mysql()
    insert_topic_news_relative(conn, cursor)

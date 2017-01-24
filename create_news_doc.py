# coding=utf-8
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永无BUG
"""
Author = Eric_Chan
Create_Time = 2016/12/31
从数据库导入数据 并创建倒排索引
"""
import Inverted_index
import doc_proccess
import MySQLdb
from tool import exe_time


def get_data_from_mysql(sql):
    # 打开数据库连接
    db = MySQLdb.connect("192.168.235.36", "fig", "fig", "fig")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        # 执行sql语句
        cursor.execute(sql)
    except Exception, e:
        # 发生错误时回滚
        print e.__str__()
        db.rollback()
    data = cursor.fetchall()
    # 关闭数据库连接
    db.close()
    return data


def insert_doc(data):
    i = Inverted_index.InvertDic()
    doc_id = doc_proccess.Doc.get_lasted_doc_id() + 1
    for news in data:
        print news
        title = news[0].decode("UTF-8")
        content = news[1].decode("UTF-8")
        datetime = news[2].decode("UTF-8")
        news_type = news[3].decode("UTF-8")
        d = doc_proccess.Doc(title, content, datetime, news_type, doc_id)
        doc_id += 1
        i.update_invert_index(d)
        print news[0] + 'done'

    i.save_word_df_dic()
    i.save_word_freq_dic()
    i.save_word_index_dic()
    i.save_word_term_dic()

if __name__ == '__main__':
    news_type_list = ['军事', '体育', '科技', '娱乐', '社会', '国际', '国内', '数码']
    news_type = '数码'
    sql = "SELECT `news_title` , `news_content` , `news_datetime` , `news_website_type` FROM `news` where" \
          " news_title like '%林丹%' ORDER BY `news_datetime` DESC LIMIT 0 , 100"
    news_data = get_data_from_mysql(sql)
    print len(news_data)
    insert_doc(news_data)

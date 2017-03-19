# -*- coding: utf-8 -*-
# import pymongo
import MySQLdb
import sys


def connect_mysql():
    """连接数据库

    :return
        conn：
        cursor：
    """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    conn = MySQLdb.connect(host="192.168.235.36", user="fig", passwd="fig", db="fig", charset='utf8')
    cursor = conn.cursor()
    return conn, cursor


def select(sql, t=None):
    """返回数据表

    :return
        row：返回数数据表
    """
    conn, cursor = connect_mysql()
    if t is not None:
        sql = sql % t
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    return row


def save_many_into_mysql(conn, cursor, sql, temp):
    try:
        cursor.executemany(sql, temp)
        conn.commit()
    except MySQLdb.Error, e:
        try:
            sql_error = "Error y%d:%s" % (e.args[0], e.args[1])
            print sql_error
        except IndexError:
            print "MySQL Error:%s" % str(e)

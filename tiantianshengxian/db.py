from django.db import connection as conn


def update(sql, params=None):
    """
    支持 增 删  改  三个操作
    :param sql:
    :param params:
    :return:
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount


def query(sql, params=None):
    """
    查询单条记录
    :param sql:
    :param params:
    :return:
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        # 获取结果集
        data = cursor.fetchone()

        if data is None:
            return

        # 获取查询的字段
        columns = [columns[0] for columns in cursor.description]

        # 把字段 和 数据 合成一个 字段
        return dict(zip(columns, data))


def query_list(sql, params=None):
    """
    查询单条记录
    :param sql:
    :param params:
    :return:
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        # 获取结果集
        data = cursor.fetchall()

        if data is None:
            return []

        # 获取查询的字段
        columns = [columns[0] for columns in cursor.description]

        # 把字段 和 数据 合成一个 字段
        return [dict(zip(columns, d)) for d in data]

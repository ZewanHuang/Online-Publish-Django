import MySQLdb
import datetime

from utils.hash import hash_code
from utils.Global import *

import os

'''连接mySQL并新建数据库表'''

print("connect to database... OK")

myDB = MySQLdb.connect(
    host=db.host,
    user=db.user,
    passwd=db.passwd,
)

print("create new database... OK")

cursor = myDB.cursor()
try:
    cursor.execute("drop database if exists {}".format("`" + db.db + "`"))
    cursor.execute("create database {} character set utf8 collate utf8_general_ci".format("`" + db.db + "`"))
    myDB.commit()  # 提交到数据库执行，一定要记提交哦
except Exception as e:
    myDB.rollback()  # 发生错误时回滚
    print(e)
cursor.close()

print("database create successfully... OK")


'''初始化django数据库'''
os.system("python manage.py makemigrations")
os.system("python manage.py migrate")

print("django init... OK")

'''连接数据库'''
db = MySQLdb.connect(
    host=db.host,
    user=db.user,
    passwd=db.passwd,
    db=db.db,
    charset='utf8'
)

'''待插入的数据'''
username = editor.username
email = editor.email
password = hash_code(editor.password)
has_confirmed = 1
user_type = '编辑'
editor_id = 1
id = 1
avatar = 'avatar/user_default/2.png'
c_time = datetime.datetime.now()

'''插入数据'''
cursor = db.cursor()
try:
    cursor.execute(
        "insert into tb_users(id, username, email, password, has_confirmed, user_type, c_time, avatar, user_desc, real_name, education_exp, job_unit) " \
        "values('%d','%s','%s','%s','%d','%s','%s','%s','%s','%s','%s','%s')" \
        % (id, username, email, password, has_confirmed, user_type, c_time, avatar, None, None, None, None)
    )
    cursor.execute("insert into tb_editors(id, editor_id) " \
                   "values('%d','%d')" \
                   % (id, editor_id))

    db.commit()  # 提交到数据库执行，一定要记提交哦
except Exception as e:
    db.rollback()  # 发生错误时回滚
    print(e)
cursor.close()

print("editor info init... OK")

'''关闭连接'''
db.close()

print("run django server for you... OK")

os.system("python manage.py runserver")

import MySQLdb
import datetime

from utils.hash import hash_code

'''连接数据库'''
db = MySQLdb.connect(
    host='159.75.136.86',
    user='root',
    passwd='db123456',
    db='ops',
    charset='utf8'
)

'''待插入的数据'''
username = 'editor01'
email = 'zewantop@163.com'
password = hash_code('zewantop1')
has_confirmed = 1
user_type = '编辑'
editor_id = 1
id = 1
avatar = '/media/user_default/2.png'
c_time = datetime.datetime.now()

'''插入数据'''
sql = "insert into tb_users(id, username, email, password, has_confirmed, user_type, c_time, avatar, user_desc, real_name, education_exp, job_unit) " \
      "values('%d','%s','%s','%s','%d','%s','%s','%s','%s','%s','%s','%s')" \
      % (id, username, email, password, has_confirmed, user_type, c_time, avatar, None, None, None, None)
cursor = db.cursor()
try:
    cursor.execute(sql)
    db.commit()  # 提交到数据库执行，一定要记提交哦
except Exception as e:
    db.rollback()  # 发生错误时回滚
    print(e)
cursor.close()

'''插入数据'''
sql = "insert into tb_editors(id, editor_id) " \
      "values('%d','%d')" \
      % (id, editor_id)
cursor = db.cursor()
try:
    cursor.execute(sql)
    db.commit()  # 提交到数据库执行，一定要记提交哦
except Exception as e:
    db.rollback()  # 发生错误时回滚
    print(e)
cursor.close()

'''关闭连接'''
db.close()

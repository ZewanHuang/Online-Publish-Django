class editor:
    # editor information

    username = 'editor01'  # 这里的信息为网站编辑的登录信息，包括用户名、密码、邮箱，您将使用该用户名与密码登录进入编辑管理界面
    email = 'zewantop@163.com'
    password = 'zewantop1'


class email:
    EMAIL_HOST = 'smtp.163.com'
    EMAIL_PORT = 25
    EMAIL_HOST_USER = 'zewantop@163.com'
    EMAIL_HOST_PASSWORD = 'AAAAAAAAAAAA'  # 邮箱 SMTP 授权码，此处为虚拟，须修改


class db:
    # database information

    host = '127.0.0.1'
    user = 'root'
    passwd = 'yourpasswd'  # 修改为您本地或远程的 mysql数据库信息
    db = 'ops'


class host:  # 修改为django允许运行的网址
    allowed_host = ['localhost', '127.0.0.1']


class rootUrl:
    WEB_FRONT = 'http://127.0.0.1:8080'  # 若部署服务器，请将 http://127.0.0.1:8080 改为您的域名或服务器IP
    WEB_ROOT = 'http://127.0.0.1:8080/api'  # 同上

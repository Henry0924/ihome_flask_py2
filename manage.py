# coding:utf-8

from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from ihome import creat_app, db


app = creat_app("develop")


# 创建管理工具对象
manage = Manager(app)
Migrate(app, db)
manage.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manage.run()

#encoding: utf-8
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from zlbbs import create_app
from exts import db
from apps.cms import models as cms_models
from apps.front import models as front_models
from apps.models import BannerModel,BoardModel,PostModel,CommentModel,HeightLightModel
import time

CMSUser = cms_models.CmsUser
FrontUser = front_models.FrontUser
CMSRole = cms_models.CMSRole
CMSPermission = cms_models.CMSPermission
app = create_app()

manager = Manager(app)

Migrate(app,db)
manager.add_command('db',MigrateCommand)

@manager.option('-u','--username',dest='username')
@manager.option('-p','--password',dest='password')
@manager.option('-e','--email',dest='email')
def create_cms_user(username,password,email):
    user = CMSUser(username=username,password=password,email=email)
    db.session.add(user)
    db.session.commit()
    print('cms用户添加成功！')

@manager.command
def create_role():
    #访问者(可以修改个人信息)
    visitor = CMSRole(name='访问者',desc='只能浏览相关数据，不能修改。')
    visitor.permissions = CMSPermission.VISITOR
    #运营者(修改个人信息，管理帖子，管理评论，管理前台用户)
    operater = CMSRole(name='运营',desc='管理帖子，管理评论，管理前台用户。')
    operater.permissions = CMSPermission.VISITOR|CMSPermission.FRONTUSER|CMSPermission.POSTER|CMSPermission.COMMENTER|CMSPermission.CMSUSER
    #管理员(拥有绝大部分权限)
    admin = CMSRole(name='管理员',desc='拥有本系统所有权限。')
    admin.permissions = CMSPermission.VISITOR|CMSPermission.FRONTUSER|CMSPermission.POSTER|CMSPermission.COMMENTER|CMSPermission.CMSUSER|CMSPermission.BORDER
    #开发者(最高权限)
    developer = CMSRole(name='开发者',desc='开发人员专用角色。')
    developer.permissions = CMSPermission.ALL_PERMISSION

    db.session.add_all([visitor,operater,admin,developer])
    db.session.commit()

@manager.option('-e','--email',dest='email')
@manager.option('-n','--name',dest='name')
def add_user_to_role(email,name):
    user = CMSUser.query.filter_by(email=email).first()
    if user:
        role = CMSRole.query.filter_by(name=name).first()
        if role:
            role.user.append(user)
            db.session.commit()
            print('用户添加到角色成功！')
        else:
            print('%s这个角色不存在！' %name)
    else:
        print('%s邮箱没有这个用户！' %email)

@manager.option('-t','--telephone',dest='telephone')
@manager.option('-u','--username',dest='username')
@manager.option('-p','--password',dest='password')
def create_front_user(telephone,username,password):
    user = FrontUser(telephone=telephone,username=username,password=password)
    db.session.add(user)
    db.session.commit()


@manager.command
def test_permission():
    user = CMSUser.query.first()
    if user.has_permission(CMSPermission.VISITOR):
        print('这个用户有访问者权限！')
    else:
        print('这个用户没有访问者权限！')

@manager.command
def add_test_post():
    for x in range(1,201):
        title = '标题：%d' %x
        content = '内容：%d' %x
        board = BoardModel.query.first()
        author = FrontUser.query.first()
        post = PostModel(title=title,content=content)
        post.board = board
        post.author = author
        db.session.add(post)
        db.session.commit()
        print('添加第%d篇测试帖子成功！' %x)
        time.sleep(0.1)


if __name__ == '__main__':
    manager.run()
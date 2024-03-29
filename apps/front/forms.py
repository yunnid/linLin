#encoding: utf-8
from ..forms import BaseForm
from wtforms import StringField,IntegerField
from wtforms.validators import regexp,EqualTo,ValidationError,InputRequired
from utils import zlcache

class SignupForm(BaseForm):
    telephone = StringField(validators=[regexp(r'1[345789]\d{9}',message='请输入正确格式的手机号！')])
    sms_captcha = StringField(validators=[regexp(r'\w{4}',message='请输入正确格式的手机验证码！')])
    username = StringField(validators=[regexp(r'.{2,20}',message='用户名长度应该在2至20位之间！')])
    password1 = StringField(validators=[regexp(r'[0-9a-zA-Z\._]{6,20}',message='密码长度应该在6至20位之间！')])
    password2 = StringField(validators=[EqualTo('password1',message='两次输入密码不一致！')])
    graph_captcha = StringField(validators=[regexp(r'\w{4}',message='请输入正确格式的图形验证码！')])

    def validate_sms_captcha(self,field):
        sms_captcha = field.data
        telephone = self.telephone.data
        if sms_captcha != '1111':
            sms_captcha_mem = zlcache.get(telephone)
            if not sms_captcha_mem or sms_captcha_mem.lower() != sms_captcha.lower():
                raise ValidationError(message='短信验证码输入错误！')

    def validate_graph_captcha(self,field):
        graph_captcha = field.data
        if graph_captcha != '1111':
            graph_captcha_mem = zlcache.get(graph_captcha.lower())
            if not graph_captcha_mem:
                raise ValidationError(message='图形验证码输入错误！')

class SigninForm(BaseForm):
    telephone = StringField(validators=[regexp(r'1[345789]\d{9}', message='请输入正确格式的手机号！')])
    password = StringField(validators=[regexp(r'[0-9a-zA-Z\._]{6,20}', message='密码长度应该在6至20位之间！')])
    remember = StringField()

class AddPostForm(BaseForm):
    title = StringField(validators=[InputRequired(message='请输入标题！')])
    content = StringField(validators=[InputRequired(message='请输入内容！')])
    board_id = IntegerField(validators=[InputRequired(message='请输入板块id！')])

class AddCommentForm(BaseForm):
    content = StringField(validators=[InputRequired(message='请输入评论内容！')])
    post_id = IntegerField(validators=[InputRequired(message='请输入帖子id！')])
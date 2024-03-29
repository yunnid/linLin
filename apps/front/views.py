#encoding: utf-8
from flask import (
    Blueprint,
    render_template,
    views,
    request,
    session,
    url_for,
    g,
    abort
)
from ..models import BannerModel,BoardModel,PostModel,CommentModel,HeightLightModel
from utils import restful,safeutils
from .models import FrontUser
from .forms import SignupForm,SigninForm,AddPostForm,AddCommentForm
from exts import db
import config
from .decorators import Login_required
from flask_paginate import Pagination,get_page_parameter
from sqlalchemy import  func

bp = Blueprint('front',__name__)

@bp.route('/')
def index():
    board_id = request.args.get('bd',type=int,default=None)
    sort = request.args.get('st',type=int,default=1)
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).limit(4)
    boards = BoardModel.query.all()
    page = request.args.get(get_page_parameter(),type=int,default=1)
    start = (page-1)*config.PER_PACE
    end = page*config.PER_PACE
    total = 0
    posts = None
    query_obj = ''
    if sort == 1:
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        query_obj = db.session.query(PostModel).outerjoin(HeightLightModel).order_by(HeightLightModel.create_time.desc(),PostModel.create_time.desc())
    elif sort == 3:
        query_obj = query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 4:
        query_obj = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(func.count(CommentModel.id).desc(),PostModel.create_time.desc())
    if board_id:
        query_obj = query_obj.filter(PostModel.board_id==board_id)
        posts = query_obj.slice(start,end)
        total = query_obj.count()
    else:
        posts = query_obj.slice(start,end)
        total = query_obj.count()
    pagination= Pagination(bs_version=3,page=page,total=total,outer_window=0)
    context = {
        'banners': banners,
        'boards': boards,
        'posts': posts,
        'pagination': pagination,
        'current_board': board_id,
        'sort': sort
    }
    return render_template('front/front_index.html',**context)


@bp.route('/acomment/',methods=['POST'])
@Login_required
def add_comment():
    form = AddCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        post = PostModel.query.get(post_id)
        if post:
            comment = CommentModel(content=content)
            comment.post = post
            comment.author = g.front_user
            db.session.add(comment)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有这篇帖子！')
    else:
        return restful.params_error(message=form.get_error())

@bp.route('/p/<post_id>/')
def post_detail(post_id):
    post = PostModel.query.get(post_id)
    if not post:
        abort(404)
    return render_template('front/front_pdetail.html',post=post)


@bp.route('/apost/',methods=['POST','GET'])
@Login_required
def apost():
    if request.method == 'GET':
        boards = BoardModel.query.all()
        context = {
            'boards': boards
        }
        return render_template('front/front_apost.html',**context)
    else:
        form = AddPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            board = BoardModel.query.get(board_id)
            if board:
                post = PostModel(title=title,content=content)
                post.board = board
                post.author = g.front_user
                db.session.add(post)
                db.session.commit()
                return restful.success()
            else:
                return restful.params_error(message='没有这个板块！')
        else:
            return restful.params_error(message=form.get_error())


class SignupView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signup.html',return_to=return_to)
        else:
            return render_template('front/front_signup.html')
    def post(self):
        form = SignupForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            username = form.username.data
            password = form.password1.data
            user = FrontUser(telephone=telephone,username=username,password=password)
            db.session.add(user)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message=form.get_error())

class SigninView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and return_to != url_for('front.signup') and safeutils.is_safe_url(return_to):
            return render_template('front/front_signin.html',return_to=return_to)
        else:
            return render_template('front/front_signin.html')
    def post(self):
        form = SigninForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            password = form.password.data
            remember = form.remember.data
            user = FrontUser.query.filter_by(telephone=telephone).first()
            if user and user.check_password(password):
                session[config.FRONT_USER_ID] = user.id
                if remember:
                    session.permanent = True
                return restful.success()
            else:
                return restful.params_error(message='手机号或密码错误！')
        else:
            return restful.params_error(message=form.get_error())

bp.add_url_rule('/signin/',view_func=SigninView.as_view('signin'))
bp.add_url_rule('/signup/',view_func=SignupView.as_view('signup'))
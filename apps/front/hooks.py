#encoding: utf-8
#create_time: 2019/7/10 15:29
import config
from .views import bp
from flask import session,g,render_template
from .models import FrontUser

@bp.before_request
def before_request():
    if config.FRONT_USER_ID in session:
        user_id = session.get(config.FRONT_USER_ID)
        user = FrontUser.query.get(user_id)
        if user:
            g.front_user = user

@bp.errorhandler
def page_not_found():
    return render_template('front/front_404.html'),404
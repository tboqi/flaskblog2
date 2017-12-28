import os
import base
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_babelex import Babel
import model.article


# Create Flask application
# app = Flask(__name__)
# app.config.from_pyfile('config.py')
# db = SQLAlchemy(app)
# babel = Babel(app)
# app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'


# Define models
roles_users = base.db.Table(
    'roles_users',
    base.db.Column('user_id', base.db.Integer(),
                   base.db.ForeignKey('user.id')),
    base.db.Column('role_id', base.db.Integer(), base.db.ForeignKey('role.id'))
)


class Role(base.db.Model, RoleMixin):
    id = base.db.Column(base.db.Integer(), primary_key=True)
    name = base.db.Column(base.db.String(80), unique=True)
    description = base.db.Column(base.db.String(255))

    def __str__(self):
        return self.name


class User(base.db.Model, UserMixin):
    id = base.db.Column(base.db.Integer, primary_key=True)
    first_name = base.db.Column(base.db.String(255))
    last_name = base.db.Column(base.db.String(255))
    email = base.db.Column(base.db.String(255), unique=True)
    password = base.db.Column(base.db.String(255))
    active = base.db.Column(base.db.Boolean())
    confirmed_at = base.db.Column(base.db.DateTime())
    roles = base.db.relationship('Role', secondary=roles_users,
                                 backref=base.db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(base.db, User, Role)
security = Security(base.app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# Flask views


@base.app.route('/')
def index():
    return render_template('index.html')

# Create admin
admin = flask_admin.Admin(
    base.app,
    '后台管理',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
admin.add_view(MyModelView(Role, base.db.session))
admin.add_view(MyModelView(User, base.db.session))

# admin.add_view(base.PermissionModelView(base.Permission, base.db.session))
# admin.add_view(base.MyModelView(base.Router, base.db.session))
admin.add_view(model.article.ArticleView(
    model.article.Article, base.db.session))
admin.add_view(model.article.CategoryView(
    model.article.Category, base.db.session))

# define a context processor for merging flask-admin's template context into the
# flask-security views.


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


if __name__ == '__main__':
    base.app.jinja_env.auto_reload = True
    # Build a sample db on the fly, if one does not exist yet.
    # app_dir = os.path.realpath(os.path.dirname(__file__))
    # database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    # if not os.path.exists(database_path):
    #     build_sample_db()

    # Start app
    base.app.run(debug=True)

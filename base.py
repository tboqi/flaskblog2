import os
import datetime
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security,  \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_babelex import Babel
from wtforms import TextAreaField
from wtforms.widgets import TextArea


# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'


# role_permission_ln = db.Table(
#     'auth_role_permission_ln',
#     db.Column('permission_id', db.Integer(),
#               db.ForeignKey('auth_permissions.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('auth_roles.id'))
# )


# class Role(db.Model, RoleMixin):
#     __tablename__ = 'auth_roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#     permissions = db.relationship('Permission', secondary=role_permission_ln,
# backref=db.backref('auth_roles', lazy='dynamic'))

#     def __str__(self):
#         return self.name


# class Permission(db.Model, RoleMixin):
#     __tablename__ = 'auth_permissions'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80))
#     # routers = db.relationship("Router",
#     #                           backref=db.backref('auth_routers'))

#     def __str__(self):
#         return self.name


# class Router(db.Model):
#     __tablename__ = 'auth_routers'
#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(255))
#     router = db.Column(db.String(255))
#     name = db.Column(db.String(255))
#     permission = db.relationship('Permission',
#                                  backref=db.backref('auth_permissions'))
#     permission_id = db.Column(db.Integer, db.ForeignKey('auth_permissions.id'))
#     parent_id = db.Column(db.Integer, db.ForeignKey('auth_routers.id'))
#     parent = db.relationship('Router',
# backref=db.backref('auth_routers'), remote_side=[id])

#     def __str__(self):
#         return self.name


# class User(db.Model, UserMixin):
#     __tablename__ = 'auth_users'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     email = db.Column(db.String(255), unique=True)
#     password = db.Column(db.String(255))
#     active = db.Column(db.Boolean())
#     created_at = db.Column(db.DateTime())
#     role = db.relationship('Role',
#                            backref=db.backref('auth_roles'))
#     role_id = db.Column(db.Integer, db.ForeignKey('auth_roles.id'))

#     def __str__(self):
#         return self.name


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        # if current_user.has_role('superuser'):
        #     return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        # if not self.is_accessible():
        #     if current_user.is_authenticated:
        #         # permission denied
        #         abort(403)
        #     else:
        #         # login
        #         return redirect(url_for('security.login', next=request.url))


class RoleModelView(MyModelView):
    column_labels = {'name': '角色名', 'description': '描述'}


class PermissionModelView(MyModelView):
    form_excluded_columns = ['routers']
    column_labels = {'name': '名称'}


class UserModelView(MyModelView):
    form_excluded_columns = ['created_at']
    column_exclude_list = ['password', ]

    column_labels = {'role': '角色', 'name': '用户名', 'password': '密码',
                     'active': '激活', 'created_at': '创建时间'}


class CKTextAreaWidget(TextArea):

    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


@app.route('/admin/welcome')
def admin_welcome():
    return request.path

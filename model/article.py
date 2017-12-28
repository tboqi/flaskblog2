# from base import db, MyModelView, CKTextAreaField, User
import datetime
from flask_security import current_user
import base


class Article(base.db.Model):
    __tablename__ = 'articles'
    id = base.db.Column(base.db.Integer, primary_key=True)
    title = base.db.Column(base.db.String(255))
    content = base.db.Column(base.db.Text, nullable=False)
    created_at = base.db.Column(base.db.DateTime())
    updated_at = base.db.Column(base.db.DateTime())
    author = base.db.relationship('User',
                                  backref=base.db.backref('user'))
    author_id = base.db.Column(
        base.db.Integer, base.db.ForeignKey('user.id'))
    category = base.db.relationship('Category',
                                    backref=base.db.backref('article_categories'))
    category_id = base.db.Column(
        base.db.Integer, base.db.ForeignKey('article_categories.id'))
    tags = base.db.Column(base.db.String(80))

    def __str__(self):
        return self.title


class Category(base.db.Model):
    __tablename__ = 'article_categories'
    id = base.db.Column(base.db.Integer, primary_key=True)
    name = base.db.Column(base.db.String(40))

    def __str__(self):
        return self.name


class ArticleView(base.MyModelView):
    form_excluded_columns = ['created_at', 'updated_at', 'author', 'author_id']
    column_exclude_list = ['content', ]

    column_labels = {'author': '作者', 'title': '标题', 'content': '内容',
                     'created_at': '创建时间', 'updated_at': '更新时间'}

    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'content': base.CKTextAreaField
    }
    column_formatters = dict(tags=lambda v, c, m, p: m.tags.strip(','))

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_at = datetime.datetime.today()
            model.author_id = current_user.id
            pass

        model.updated_at = datetime.datetime.today()
        model.tags.strip(',')
        model.tags = ',' + model.tags + ','

        pass


class CategoryView(base.MyModelView):
    form_excluded_columns = ['articles']
    column_labels = {'name': '分类名'}

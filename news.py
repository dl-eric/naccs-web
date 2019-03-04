from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort
from auth import login_required, flash_errors
from db import db, Article, School
from datetime import date
from cognito_utils import is_author
from forms import ArticleForm
import functools
import mistune

markdown = mistune.Markdown()

news_page = Blueprint('news', __name__, url_prefix='/news', template_folder='templates')

def author_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'access_token' not in session:
            return redirect(url_for('auth_page.signin'))
        else:
            if (not is_author(session.get('username'))):
                return redirect(url_for('index'))
        return view(**kwargs)

    return wrapped_view

@news_page.route('/')
def news():
    author = False
    username = session.get('username', None)
    if (session.get('access_token')):
        author = is_author(username)

    articles = Article.query.order_by(Article.id.desc()).all()
    
    return render_template('news/index.html', username=username, articles=articles, author=author)

@news_page.route('/create', methods=['get', 'post'])
@author_required
def create():
    username = session.get('username', None)
    
    form = ArticleForm()
    if form.validate_on_submit():
        new_post = Article(form.title.data, form.author.data, session.get('username'), markdown(form.content.data), markdown(form.summary.data))
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('news.news'))
    else:
        flash_errors(form)
    return render_template('news/create.html', username=username, form=form)

@news_page.route('/<int:id>')
def article(id):
    username = session.get('username', None)

    # Verify that the ID is valid.
    article = Article.query.filter(Article.id == id).first()
    if article == None:
        return render_template('404.html', username=username), 404

    author = False
    if (session.get('access_token')):
        author = is_author(username)

    return render_template('news/article.html', username=username, article=article, author=author)

@news_page.route('/<int:id>/edit', methods=['get', 'post'])
@author_required
def edit(id):
    username = session.get('username', None)

    # Verify that the ID is valid.
    article = Article.query.filter(Article.id == id).first()
    if article == None:
        return render_template('404.html', username=username), 404

    form = ArticleForm()
    if form.validate_on_submit():
        # TODO
        pass
        
    return render_template('news/edit.html', username=username)

@news_page.route('/<int:id>/delete', methods=['post'])
@author_required
def delete(id):
    article = Article.query.filter(Article.id == id).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('news.news'))
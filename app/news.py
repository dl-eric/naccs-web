from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort
from auth import login_required, flash_errors, AWS_IAM_ACCESS_KEY, AWS_IAM_SECRET_KEY
from db import db, Article
from datetime import date
from cognito_utils import is_author
from forms import ArticleForm
import functools
import mistune
import boto3
import os

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

markdown = mistune.Markdown()

news_page = Blueprint('news', __name__, url_prefix='/news', template_folder='templates')

def upload_file_to_s3(file, bucket_name, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_IAM_ACCESS_KEY, aws_secret_access_key=AWS_IAM_SECRET_KEY)
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Upload Error:", e)
        return e

    return "{}{}".format(S3_LOCATION, file.filename)

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
    
    return render_template('news/index.html', articles=articles, author=author, markdown=markdown)

@news_page.route('/create', methods=['get', 'post'])
@author_required
def create():

    form = ArticleForm()
    if form.validate_on_submit():
        # Upload image
        path = upload_file_to_s3(request.files[form.image.name], S3_BUCKET)
        #print(form.image.data.filename)
        new_post = Article(form.title.data, form.author.data, session.get('username'), form.content.data, form.summary.data, path)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('news.news'))
    else:
        flash_errors(form)
    return render_template('news/create.html', form=form)

@news_page.route('/<int:id>')
def article(id):
    username = session.get('username', None)

    # Verify that the ID is valid.
    article = Article.query.filter(Article.id == id).first()
    if article == None:
        return abort(404)

    author = False
    if (session.get('access_token')):
        author = is_author(username)

    return render_template('news/article.html', article=article, author=author, markdown=markdown)

@news_page.route('/<int:id>/edit', methods=['get', 'post'])
@author_required
def edit(id):

    # Verify that the ID is valid.
    article = Article.query.filter(Article.id == id).first()
    if article == None:
        return abort(404)

    form = ArticleForm()
    if form.validate_on_submit():
        article.title   = form.title.data 
        article.author  = form.author.data
        article.content = form.content.data
        article.summary = form.summary.data

        path = upload_file_to_s3(request.files[form.image.name], S3_BUCKET)
        article.image_path = path
        
        db.session.commit()
        flash("Successfully edited.", 'success')
        return render_template('news/edit.html', form=form)
    
    form.title.data     = article.title
    form.author.data    = article.author
    form.content.data   = article.content
    form.summary.data   = article.summary

    return render_template('news/edit.html', form=form)

@news_page.route('/<int:id>/delete', methods=['post'])
@author_required
def delete(id):
    article = Article.query.filter(Article.id == id).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('news.news'))
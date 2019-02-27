from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from auth import login_required

news_page = Blueprint('news', __name__, url_prefix='/news', template_folder='templates')

@news_page.route('/')
def news():
    return 'hello'

@news_page.route('/create', methods=['get', 'post'])
def create():
    return 'create'

@news_page.route('/<int:id>/update', methods=['get', 'post'])
def update(id):
    return str(id)

@news_page.route('/<int:id>/delete', methods=['post'])
def delete(id):
    return str(id)
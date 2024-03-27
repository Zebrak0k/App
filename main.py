import datetime
from os import abort

from flask import Flask, render_template, redirect, request, make_response, session, jsonify
from flask_restful import reqparse, abort, Api, Resource

import news_api
import news_resource
from data import db_session
from data.user import User
from data.news import News
from forms.LoginForm import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForms
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_login import login_user

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key_flask'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=240)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message='Не правильный логин или пароль',
                               form=form)
    return render_template('login.html',
                           title='Авторизация',
                           form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True)
        )
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, current_user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForms()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title='Registration',
                                   form=form, message="Password don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", title='Registration',
                                   form=form, message="User already exist")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template("register.html", title='Registration',
                           form=form)


@app.route("/news", methods=["GET", "POST"])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html',
                           title='Добавление новости',
                           form=form)

@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)

@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

def main():
    db_session.global_init("db/blog_db.sqlite")
    app.register_blueprint(news_api.blueprint)
    api.add_resource(news_resource.NewsListResource, '/api/v2/news')
    api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')
    app.run()

def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f'News {news_id} not found')

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.jobs import Jobs
from data.login_form import LoginForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# Для верной работы flask-login
@login_manager.user_loader
def load_user(user_id):
    '''
    функция для получения пользователя
    '''
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # Если форма логина прошла валидацию
        db_sess = db_session.create_session()
        # находим пользователя с введенной почтой
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # проверяем, введен ли для него правильный пароль
        if user and user.check_password(form.password.data):
            # вызываем функцию login_user модуля flask-login и передаем туда объект пользователя
            login_user(user, remember=form.remember_me.data)  # и значение галочки «Запомнить меня»
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", jobs=jobs, names=names, title='Work log')


@app.route('/logout')
@login_required  # обработчики страниц, на которые может попасть только авторизованный пользователь
def logout():
    logout_user()  # «забываем» пользователя
    return redirect("/")


def main():
    db_session.global_init("db/mars_explorer.sqlite")
    app.run()


if __name__ == '__main__':
    main()

from flask import (
    flash,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    login_required,
    logout_user,
)
from werkzeug.urls import url_parse

from app import (
    app,
    db,
)
from app.forms import (
    LoginForm,
    RegistrationForm,
)
from app.models import (
    Event,
    User,
)

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home', events=Event.query.all())

@app.route('/login', methods=["GET", "POST"])
def login():
    # Skip if user already auth'd
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # login failed
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # login succeeded
        login_user(user, remember=form.remember_me.data)

        # get next page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

from flask import render_template, url_for, flash, redirect, request, session
from exercisewebapp import app, db, bcrypt
from exercisewebapp.forms import RegistrationForm, LoginForm, GroupCreateForm, PostForm
from exercisewebapp.models import User, Post, Group
from flask_login import login_user, current_user, logout_user, login_required


posts = [
    {
        'author': 'David Webber',
        'title': 'Group Video Post 1',
        'content': 'First post content text info',
        'date_posted': 'April 20, 2018',
        'reps': 10
    },
    {
        'author': 'John Cena',
        'title': 'Group Video Post 2',
        'content': 'Second post content text info',
        'date_posted': 'April 21, 2018',
        'reps': 5
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('homefeed.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/leaderboard",methods=['GET', 'POST'])
@login_required
def leaderboard():
    if current_user.is_authenticated:
        form = PostForm()
        user = current_user.id
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data(), reps=form.reps.data(), group_id=form.group_id.data())
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created', 'success')
            return redirect(url_for('home'))
    return render_template('leaderboard.html', title='Group Leaderboard',form = form)



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/group", methods=['GET', 'POST'])
@login_required
def creategroup():

    if current_user.is_authenticated:
        form = GroupCreateForm()
        user = current_user.id
        if form.validate_on_submit():
            group = Group(exercise_title=form.exercise_name.data, description=form.description.data, leader_user_id=user)
            db.session.add(group)
            db.session.commit()
            flash('Your new exercise group has been created! You are now able to invite friends and compete!', 'success')
            return redirect(url_for('home'))
        return render_template('group.html', title='Create Group', form=form)
    return render_template('group.html', title='Create Group', form=form)

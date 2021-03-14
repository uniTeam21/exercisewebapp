from flask import render_template, url_for, flash, redirect, request, session
from exercisewebapp import app, db, bcrypt
from exercisewebapp.forms import RegistrationForm, LoginForm, GroupCreateForm, PostForm
from exercisewebapp.models import User, Post, Group
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc





@app.route("/")
@app.route("/home", methods=['GET'])
def home():
    data = db.session.query(Post, User).join(User).all()
    #to show latest posts at the top
    data.reverse()
    #posts1 = Post.query.order_by(Post.date_posted).all()
    return render_template('homefeed.html', posts=data)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/leaderboard",methods=['GET', 'POST'])
@login_required
def post_leaderboard():
    if current_user.is_authenticated:
        form = PostForm()
        user = current_user.id
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, reps=int(form.reps.data), user_id=int(user),group_id=int(form.group_id.data))
            #post = User(title=form.title.data, content=form.content.data, reps=int(form.reps.data), user_id=int(user), groups=Group(id =int(form.group_id.data)))
            group = Group.query.get(form.group_id.data)
            usergroup = User.query.get(user)#.groups.insert(group)
            #usergroup.groups.append(group)
            #print(usergroup.groups)
            group.groups.append(usergroup)
            #TODO: somehow get groups to be added/appended onto User on when posted
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created', 'success')
            return redirect(url_for('home'))
    return render_template('leaderboard.html', title='Group Leaderboard',form = form)

"""
def leaderboardGroup(all_users):
    users_id = []
    for user in all_users:
        users_id.append(user.id)
        user_posts = []
        user_groups = []
        for post in user.posts:
            user_posts.append(post)
        for group in user.groups:
            user_groups.append(group)"""


#this function will get post information to leaderboards for each group
#for each unique group, get posts with highest reps for each unique person
#and sort highest to lowest
@app.route("/updateleaderboard",methods=['GET'])
@login_required
def update_leaderboard():
    if current_user.is_authenticated:
        #user_posts = User.query.get(current_user).all()
        all_users = User.query.all()
        for user in all_users:
            print(user)
        #print(all_users)
        return render_template('updateleaderboard.html',  all_users=all_users)
    return render_template('homefeed.html')



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

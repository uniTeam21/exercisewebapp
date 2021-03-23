from flask import render_template, url_for, flash, redirect, request, session
from exercisewebapp import app, db, bcrypt
from exercisewebapp.forms import RegistrationForm, LoginForm, GroupCreateForm, PostForm
from exercisewebapp.models import User, Post, Group
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
import pandas as pd





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
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created', 'success')
            return redirect(url_for('home'))
    return render_template('leaderboard.html', title='Group Leaderboard',form = form)

def getValues(df_list):
    for df in df_list:
        df_group_id = df['group_id']
        df_group_title = df['exercise_title']
        df_group_id = df_group_id.unique()
        df_group_title = df_group_title.unique()
    return df_group_id[0], df_group_title[0]


def leaderboardGroup(all_users):

    if current_user.is_authenticated:

        df = pd.DataFrame(columns =['group_id', 'exercise_title','user_id','username', 'max_rep'])
        user_group_ids = []
        post_reps = []
        for user in all_users:
            # get all current groups of a user
            if user.id == current_user.id:
                for group in user.groups:
                    user_group_ids.append(group.id)
               #get all posts ordered by date for each group
                    group_post_reps = []
                    for post in user.posts:
                        if post.group_id == group.id:
                            group_post_reps.append(post.reps)
                    post_reps.append(group_post_reps)

        print(post_reps)


        # for all users that are in the same groups as the current user
        # create row to dataframe with max rep

        for user in all_users:
            for group in user.groups:
                user_info = []
                if group.id in user_group_ids:
                    user_info.append(group.id)
                    user_info.append(group.exercise_title)
                    user_info.append(user.id)
                    user_info.append(user.username)
                    max_rep = 0
                    for post in user.posts:
                        if post.group_id == group.id:
                            if post.reps > max_rep:
                                max_rep = post.reps
                    user_info.append(max_rep)
                    #print(user_info)

                    df_user_info = pd.DataFrame([user_info], columns=['group_id','exercise_title', 'user_id','username', 'max_rep'])

                df= pd.concat([df, df_user_info])



        #TODO: test function and query csv file to seperate out the distinct groups
        # and sort based on max rep
        groups = df.group_id.unique()
        #print(groups)
        #df_sorted_collection = pd.DataFrame(columns =['group_id', 'user_id','username', 'max_rep'])
        df_sorted_collection = []
        for group in groups:
            df_group = df.loc[df['group_id'] == group]
            df_group =df_group.sort_values(by='max_rep', ascending=False)
            #print(df_group)
            #df_sorted_collection.append(df_group.to_html())
            df_sorted_collection.append(df_group)
        #print(df_sorted_collection)
        return df_sorted_collection, df, groups, post_reps




# def getReps(all_users):



#this function will get post information to leaderboards for each group
#for each unique group, get posts with highest reps for each unique person
#and sort highest to lowest
@app.route("/updateleaderboard",methods=['GET'])
@login_required
def update_leaderboard():
    if current_user.is_authenticated:
        #user_posts = User.query.get(current_user).all()

        try:
            all_users = User.query.all()
            df_html_list, df, groups, post_reps = leaderboardGroup(all_users)

            df_group_id_list = df['group_id'].unique()

            df_exercise_title_list = df['exercise_title'].unique()

            return render_template('updateleaderboard.html', tables=df_html_list, titles=df.columns.values,
                                   ids=df_group_id_list.tolist(), exercise_titles=df_exercise_title_list.tolist(),
                                   post_reps=post_reps)
        except:
            flash('You are not in any groups, make a post to a group to join first!', 'Fail')
            return redirect(url_for('home'))

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

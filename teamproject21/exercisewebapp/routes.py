from flask import render_template, url_for, flash, redirect, request, session
from exercisewebapp import app, db, bcrypt
from exercisewebapp.forms import RegistrationForm, LoginForm, GroupCreateForm, PostForm, VoteForm
from exercisewebapp.models import User, Post, Group, Postvote
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
import pandas as pd


##TODO: create seperate file to store non route functions and import them in
##TODO: Leaderboard duplicates value if two posts with same number of reps exists (FIX IT)
##TODO: maybe change home to be like first in first out post, so one post at a time people have to vote to see the next
##TODO: put current users groups in the side bar on post to leaderboard and my groups




# @app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        ##TODO:user this for my posts page --  data = db.session.query(Post, User, Postvote).join(User).join(Postvote).filter(User.id == current_user.id).all()
        groups = []
        print(Post.query.all())
        user = db.session.query(User).filter(User.id == current_user.id).one()
        for group in user.groups:
            groups.append(group.id)

        data = db.session.query(Post, User, Postvote).join(User).join(Postvote).filter(Post.group_id.in_(groups)).all()
        #to show latest posts at the top
        data.reverse()
        form = VoteForm()

        x = True

        if form.validate_on_submit():

            postvoteid = int(form.myhiddenid.data)

            if form.upvote.data:
                print('upvote')

                postvote = db.session.query(Postvote).filter(Postvote.id == postvoteid).one()


                for user in postvote.users_voted:
                    if user.id == current_user.id:
                        x = False
                if x:
                    postvote.upvote_number = int(postvote.upvote_number) + 1
                    postvote.total_votes = int(postvote.total_votes) + 1
                    postvote.users_voted.append(current_user)
                    db.session.commit()
                else:
                    flash('You have already voted in that post!')
                print(f'Upvotes: {postvote.upvote_number}')
                print(f'Downvotes: {postvote.downvote_number}')


            elif form.downvote.data:
                print('downvote')



                postvote = db.session.query(Postvote).filter(Postvote.id == postvoteid).one()


                for user in postvote.users_voted:
                    if user.id == current_user.id:
                        x = False
                if x:
                    postvote.downvote_number = int(postvote.downvote_number) + 1
                    postvote.total_votes = int(postvote.total_votes) + 1

                    postvote.users_voted.append(current_user)
                    db.session.commit()
                else:
                    flash('You have already voted in that post!')
                print(f'Upvotes: {postvote.upvote_number}')
                print(f'Downvotes: {postvote.downvote_number}')


        return render_template('homefeed.html', posts=data, current_user_id=current_user.id, form=form, x=x)

    return render_template('homefeed.html')





@app.route("/about")
def about():
    return render_template('about.html', title='About')



def getMemberCount(group_id):
    all_users = User.query.all()
    membercount = 0
    for user in all_users:
        for group in user.groups:
            if group.id == group_id:
                membercount +=1
    return membercount



@app.route("/leaderboard",methods=['GET', 'POST'])
@login_required
def post_leaderboard():
    if current_user.is_authenticated:
        form = PostForm()
        user = current_user.id
        # list all groups the current user is in
        current_user_groups_list = get_current_user_groups()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, reps=int(form.reps.data), user_id=int(user),group_id=int(form.group_id.data))

            group = Group.query.get(form.group_id.data)
            usergroup = User.query.get(user)
            group.groups.append(usergroup)
            db.session.add(post)
            db.session.commit()
            membercount = getMemberCount(form.group_id.data)
            last_post =  Post.query.order_by(-Post.id).first()
            post_vote = Postvote(post_id=int(last_post.id), group_id = int(last_post.group_id),post=last_post,upvote_number=0, downvote_number = 0, total_votes = 0, member_count=membercount, decided=False)
            db.session.add(post_vote)
            db.session.commit()

            all_post_votes = Postvote.query.filter(Postvote.group_id == int(form.group_id.data)).all()
            for postvote in all_post_votes:
                if postvote.decided == False:
                    postvote.member_count = membercount
            db.session.commit()



            flash('Your post has been created', 'success')

            return redirect(url_for('home'))
        return render_template('leaderboard.html', title='Group Leaderboard',form = form, current_user_groups_list=current_user_groups_list)
    return render_template('leaderboard.html', title='Group Leaderboard',form = form)

def getValues(df_list):
    for df in df_list:
        df_group_id = df['group_id']
        df_group_title = df['exercise_title']
        df_group_id = df_group_id.unique()
        df_group_title = df_group_title.unique()
    return df_group_id[0], df_group_title[0]


def leaderboardGroup(all_users, accepted_posts):

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




        # for all users that are in the same groups as the current user
        # create row to dataframe with max rep

        for user in all_users:
            for group in user.groups:
                user_info = []
                if group.id in user_group_ids:

                    ##
                    for post in user.posts:

                        if post.group_id == group.id:
                            if post.id in accepted_posts:
                                print(f'post id: {post.id}, user id: {post.user_id}')
                    ##

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

        ##
        df = df.drop_duplicates(subset=None, keep='first', inplace=False)
        ##TODO:maybe another drop dupilicates with subset max rep and user id
        groups = df.group_id.unique()
        df_sorted_collection = []
        for group in groups:
            df_group = df.loc[df['group_id'] == group]
            df_group =df_group.sort_values(by='max_rep', ascending=False)
            df_sorted_collection.append(df_group)

        return df_sorted_collection, df, groups, post_reps






def processVotes(all_postvotes):
    #process voting decisions

    for postvote in all_postvotes:
        if postvote.decided == False:

            if postvote.total_votes > (postvote.member_count/2):

                if postvote.upvote_number > postvote.downvote_number:


                    #set decided to true
                    postvote.decided = True
                    postvote.decision = True
                    db.session.commit()
                elif postvote.downvote_number > postvote.upvote_number:
                    postvote.decided=True
                    postvote.decision=False
                    db.session.commit()

    #collect decided post ids that have been accepted
    decided_post_ids = []
    for postvote in all_postvotes:
        if postvote.decided == True and postvote.decision == True:
            decided_post_ids.append(postvote.post_id)
    #return list of all post ids that have been accepted to be posted leaderboard
    return decided_post_ids

def get_current_user_groups():
    # list all groups the current user is in
    current_user_groups_id_list = []
    current_user_groups_title_list = []
    for group in current_user.groups:
        current_user_groups_id_list.append(group.id)
        current_user_groups_title_list.append(group.exercise_title)
    zipped= zip(current_user_groups_id_list, current_user_groups_title_list)
    return list(zipped)


#this gets the number of reps when a user creates a post
def get_current_user_total_reps():
    total = 0
    for post in current_user.posts:
        total += post.reps
    return total

#get total post number for user
def get_current_user_total_posts():
    total = 0
    for post in current_user.posts:
        total += 1
    return total

def get_user_days_active():
    days = 0
    for post in current_user.posts:
        days = post.date_posted
    return days

#this function will get post information to leaderboards for each group
#for each unique group, get posts with highest reps for each unique person
#and sort highest to lowest
@app.route("/updateleaderboard",methods=['GET'])
@login_required
def update_leaderboard():
    if current_user.is_authenticated:

        #list all groups the current user is in
        current_user_groups_list = get_current_user_groups()

        all_postvotes = Postvote.query.all()
        #list of accepted post ids
        accepted_posts = processVotes(all_postvotes)
        if current_user_groups_list:

            try:

                all_users = User.query.all()

                df_html_list, df, groups, post_reps = leaderboardGroup(all_users, accepted_posts)

                df_group_id_list = df['group_id'].unique()

                df_exercise_title_list = df['exercise_title'].unique()
                print(current_user_groups_list)
                return render_template('updateleaderboard.html', tables=df_html_list, titles=df.columns.values,
                                       ids=df_group_id_list.tolist(), exercise_titles=df_exercise_title_list.tolist(),
                                       post_reps=post_reps, current_user_list = current_user_groups_list)
            except:

                flash('Your groups have no data yet, make a post or make sure to vote on group posts', 'Fail')
                flash('You are in groups:')
                for id, title in current_user_groups_list:
                    flash(f'Group id: {id} \nGroup Exercise: {title}')



        else:
            flash('You are not in any groups, create a group or make a post to an existing group to join first!','Fail')
            return redirect(url_for('home'))

    return render_template('homefeed.html')


# def groupProgress(all_posts):
#     if current_user.is_authenticated:
#         df_main= pd.DataFrame(columns =['post_id','group_id','user_id','date_posted', 'reps'])
#         post_info = []
#         for post in all_posts:
#             #puts info into list format
#             post_info.append(post.id)
#             post_info.append(post.group_id)
#             post_info.append(post.user_id)
#             post_info.append(post.date_posted)
#             post_info.append(post.reps)
#
#             df_inloop = pd.DataFrame([post_info], columns=['post_id', 'group_id', 'user_id', 'date_posted', 'reps'])
#             df_main = pd.concat([df_main, df_inloop])
#         print(df_main)







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
    reps = 0
    posts = 0
    # list all groups the current user is in #returns a list I believe
    current_user_groups_list = get_current_user_groups()
    groups = 0

    for id, title in current_user_groups_list:
        groups = id



    #get user total reps
    reps = get_current_user_total_reps()
    # get user total posts
    posts = get_current_user_total_posts()

    activity = get_user_days_active()

    return render_template('account.html', title='Account', reps=reps, posts=posts, groups=groups, activity=activity)
    # return render_template('account.html', title='Account')

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
            current_user.groups.append(group)
            db.session.commit()
            flash('Your new exercise group has been created! You are now able to invite friends and compete!', 'success')
            return redirect(url_for('home'))
        return render_template('group.html', title='Create Group', form=form)
    return render_template('group.html', title='Create Group', form=form)

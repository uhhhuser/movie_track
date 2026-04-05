from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from dbstruct import db, user as User, movielist

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname')

        logUser = User.query.filter_by(nickname=nickname).first()

        if logUser:
            session['username'] = logUser.nickname
            session['userID'] = logUser.id
            return redirect(url_for('home'))
        else:
            flash('user not found')
            
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userID', None)
    return redirect(url_for('home'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nickname = request.form.get('nickname')

        if not nickname or len(nickname) < 1 or len(nickname) > 16:
            flash("nickname has to be 1-16 characters")
        elif User.query.filter_by(nickname=nickname).first():
            flash("nickname exists")
        else:
            newUser = User(nickname=nickname)
            db.session.add(newUser)
            db.session.commit()

            default1 = movielist(name="want to watch", userID=newUser.id)
            default2 = movielist(name="watched", userID=newUser.id)
            db.session.add(default1)
            db.session.add(default2)
            db.session.commit()

            flash("account made, login")
            return redirect(url_for('auth.login'))

    return render_template('signup.html')

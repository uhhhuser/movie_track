from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from dbstruct import db, user, club, movielist

clubs = Blueprint('clubs', __name__)


@clubs.route('/clubs')
def list_clubs():
    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    current_user = user.query.get(session['userID'])
    user_clubs = current_user.clubs
    all_clubs = club.query.all()

    return render_template('clubs.html', clubs=user_clubs, all_clubs=all_clubs, current_user=current_user)

@clubs.route('/club/create', methods=['POST'])
def create_club():
    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    club_name = request.form.get('name')
    description = request.form.get('description', '')

    if not club_name:
        flash("club name cannot be empty")
        return redirect(request.referrer or url_for('clubs.list_clubs'))

    # create the new club
    new_club = club(
        name=club_name,
        description=description,
        creator_id=session['userID']
    )
    
    # makes first creater owner of club, need to impliment transfering ownership but that's for later 
    current_user = user.query.get(session['userID'])
    new_club.members.append(current_user)
    
    db.session.add(new_club)
    db.session.commit()

    flash(f"created club: {club_name}")
    return redirect(url_for('clubs.view_club', club_id=new_club.id))


@clubs.route('/club/<int:club_id>')
def view_club(club_id):
    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    current_user = user.query.get(session['userID'])
    club_obj = club.query.get_or_404(club_id)

    return render_template('club_detail.html', club=club_obj, current_user=current_user)


@clubs.route('/club/<int:club_id>/join', methods=['POST'])
def join_club(club_id):

    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    current_user = user.query.get(session['userID'])
    club_obj = club.query.get_or_404(club_id)

    if club_obj.is_member(current_user):
        flash("you are already a member of this club")
    else:
        club_obj.add_member(current_user)
        db.session.commit()
        flash(f"joined club: {club_obj.name}")

    return redirect(url_for('clubs.view_club', club_id=club_id))


@clubs.route('/club/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):

    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    current_user = user.query.get(session['userID'])
    club_obj = club.query.get_or_404(club_id)

    if not club_obj.is_member(current_user):
        flash("you are not a member of this club")
    else:
        club_obj.remove_member(current_user)
        db.session.commit()
        flash(f"left club: {club_obj.name}")

    return redirect(url_for('clubs.list_clubs'))


@clubs.route('/club/<int:club_id>/create_list', methods=['POST'])
def create_club_list(club_id):

    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    current_user = user.query.get(session['userID'])
    club_obj = club.query.get_or_404(club_id)

    if not club_obj.is_member(current_user):
        flash("you must be a member to create lists in this club")
        return redirect(url_for('clubs.view_club', club_id=club_id))

    list_name = request.form.get('name')
    if not list_name:
        flash("list name cannot be empty")
        return redirect(url_for('clubs.view_club', club_id=club_id))

    new_list = movielist(name=list_name, club_id=club_id)
    db.session.add(new_list)
    db.session.commit()

    flash(f"created list: {list_name}")
    return redirect(url_for('clubs.view_club', club_id=club_id))


@clubs.route('/club/<int:club_id>/delete', methods=['POST'])
def delete_club(club_id):

    if 'userID' not in session:
        flash("must be logged in")
        return redirect(url_for('auth.login'))

    club_obj = club.query.get_or_404(club_id)

    if club_obj.creator_id != session['userID']:
        flash("only the club creator can delete it")
        return redirect(url_for('clubs.view_club', club_id=club_id))

    db.session.delete(club_obj)
    db.session.commit()
    flash(f"deleted club: {club_obj.name}")

    return redirect(url_for('clubs.list_clubs'))

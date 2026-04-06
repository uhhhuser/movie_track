from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.dbstruct import db, user, club, movielist

clubs = Blueprint('clubs', __name__)

# fetch all clubs 
@clubs.route('/', methods=['GET'])
@jwt_required()
def get_clubs():
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    
    return jsonify({
        'my_clubs': [c.to_dict() for c in current_user.clubs],
        'all_clubs': [c.to_dict() for c in club.query.all()]
    }), 200

# create club
@clubs.route('/', methods=['POST'])
@jwt_required()
def create_club():
    user_id = get_jwt_identity()
    data = request.get_json()
    club_name = data.get('name', '').strip()
    description = data.get('description', '')
    
    if not club_name:
        return jsonify({'error': 'Club name cannot be empty'}), 400
    
    current_user = user.query.get(user_id)
    
    # creator becomes admin (stored in admin_id)
    new_club = club(
        name=club_name,
        description=description,
        admin_id=user_id
    )
    new_club.members.append(current_user)
    
    db.session.add(new_club)
    db.session.commit()
    
    return jsonify({
        'message': f'Created club: {club_name}',
        'club': new_club.to_dict()
    }), 201

# club details
@clubs.route('/<int:club_id>', methods=['GET'])
@jwt_required()
def get_club(club_id):
    club_obj = club.query.get_or_404(club_id)
    
    return jsonify({
        'club': club_obj.to_dict(include_members=True, include_lists=True)
    }), 200

# user join club
@clubs.route('/<int:club_id>/join', methods=['POST'])
@jwt_required()
def join_club(club_id):
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    club_obj = club.query.get_or_404(club_id)
    
    if club_obj.is_member(current_user):
        return jsonify({'error': 'Already a member'}), 400
    
    club_obj.add_member(current_user)
    db.session.commit()
    
    return jsonify({'message': f'Joined club: {club_obj.name}'}), 200

# user leave club
@clubs.route('/<int:club_id>/leave', methods=['POST'])
@jwt_required()
def leave_club(club_id):
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    club_obj = club.query.get_or_404(club_id)
    
    if not club_obj.is_member(current_user):
        return jsonify({'error': 'Not a member'}), 400
    
    club_obj.remove_member(current_user)
    db.session.commit()
    
    return jsonify({'message': f'Left club: {club_obj.name}'}), 200

# create lists IN clubs
@clubs.route('/<int:club_id>/lists', methods=['POST'])
@jwt_required()
def create_club_list(club_id):
    user_id = get_jwt_identity()
    current_user = user.query.get(user_id)
    club_obj = club.query.get_or_404(club_id)
    
    if not club_obj.is_member(current_user):
        return jsonify({'error': 'Must be a member to create lists'}), 403
    
    data = request.get_json()
    list_name = data.get('name', '').strip()
    
    if not list_name:
        return jsonify({'error': 'List name cannot be empty'}), 400
    
    new_list = movielist(name=list_name, club_id=club_id)
    db.session.add(new_list)
    db.session.commit()
    
    return jsonify({
        'message': f'Created list: {list_name}',
        'list': new_list.to_dict()
    }), 201

# delete clubs
@clubs.route('/<int:club_id>', methods=['DELETE'])
@jwt_required()
def delete_club(club_id):
    user_id = get_jwt_identity()
    club_obj = club.query.get_or_404(club_id)
    
    if club_obj.admin_id != user_id:
        return jsonify({'error': 'Only admin can delete'}), 403
    
    club_name = club_obj.name
    db.session.delete(club_obj)
    db.session.commit()
    
    return jsonify({'message': f'Deleted club: {club_name}'}), 200

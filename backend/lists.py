from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.dbstruct import db, movielist, user

lists = Blueprint('lists', __name__)

# fetch user lists
@lists.route('/', methods=['GET'])
@jwt_required()
def get_user_lists():
    user_id = int(get_jwt_identity())
    user_lists = movielist.query.filter_by(userID=user_id).all()
    
    return jsonify({
        'lists': [lst.to_dict() for lst in user_lists]
    }), 200

# create user list
@lists.route('/', methods=['POST'])
@jwt_required()
def create_list():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    list_name = data.get('name', '').strip()
    
    if not list_name:
        return jsonify({'error': 'List name cannot be empty'}), 400
    
    new_list = movielist(name=list_name, userID=user_id)
    db.session.add(new_list)
    db.session.commit()
    
    return jsonify({
        'message': f'Created list: {list_name}',
        'list': new_list.to_dict()
    }), 201

# get specific lists
@lists.route('/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list(list_id):
    user_id = int(get_jwt_identity())
    current_user = user.query.get(user_id)
    list_obj = movielist.query.get_or_404(list_id)
    
    # visibility check
    if list_obj.is_personal_list() and list_obj.userID != user_id:
        return jsonify({'error': 'You do not have permission to view this list'}), 403
    
    if list_obj.is_club_list():
        if not list_obj.club.is_member(current_user):
            return jsonify({'error': 'You must be a club member to view this list'}), 403
    
    return jsonify({
        'list': list_obj.to_dict(include_movies=True)
    }), 200

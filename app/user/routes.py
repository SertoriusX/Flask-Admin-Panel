from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.user.service import UserService

def init_user_routes(app):
    
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        existing = UserService.get_user_by_username(data['username'])
        if existing:
            return jsonify({'error': 'Username already exists'}), 400
        
        user = UserService.create_user(data)
        return jsonify({'message': 'User created', 'user': user.to_dict()}), 201
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = UserService.get_user_by_username(data['username'])
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200
    
    @app.route('/api/me', methods=['GET'])
    def me():
        from flask_jwt_extended import jwt_required, get_jwt_identity
        from app.user.repository import UserRepository
        
        @jwt_required()
        def get_current_user():
            user_id = get_jwt_identity()
            user = UserRepository.get_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify({'user': user.to_dict()}), 200
        
        return get_current_user()

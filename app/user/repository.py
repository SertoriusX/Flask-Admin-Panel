from app import db
from app.user.model import User

class UserRepository:
    @staticmethod
    def get_all():
        return User.query.all()
    
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def create(data):
        user = User()
        user.username = data.get('username')
        user.email = data.get('email')
        if 'password' in data:
            user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update(id, data):
        user = User.query.get(id)
        if user:
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'password' in data:
                user.set_password(data['password'])
            if 'is_active' in data:
                user.is_active = data['is_active']
            db.session.commit()
        return user
    
    @staticmethod
    def delete(id):
        user = User.query.get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

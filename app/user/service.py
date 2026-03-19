from app.user.repository import UserRepository

class UserService:
    @staticmethod
    def get_all_users():
        return UserRepository.get_all()
    
    @staticmethod
    def get_user_by_id(id):
        return UserRepository.get_by_id(id)
    
    @staticmethod
    def get_user_by_username(username):
        return UserRepository.get_by_username(username)
    
    @staticmethod
    def create_user(data):
        return UserRepository.create(data)
    
    @staticmethod
    def update_user(id, data):
        return UserRepository.update(id, data)
    
    @staticmethod
    def delete_user(id):
        return UserRepository.delete(id)

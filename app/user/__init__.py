# User module
from app.admin import register_model
from app.user.model import User

# Register to admin
register_model('user', User)

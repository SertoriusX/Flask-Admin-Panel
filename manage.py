#!/usr/bin/env python
import sys
import os
import shutil

def main():
    os.environ.setdefault('FLASK_APP', 'app')
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("\n📦 Available Commands:")
        print("  run                      - Run development server")
        print("  makemigrations           - Create database migrations")
        print("  migrate                  - Apply database migrations")
        print("  show-migrations          - Show all migrations")
        print("  reset-db                 - Drop and recreate all tables")
        print("  create-app <name>        - Create new module")
        print("  delete-app <name>        - Delete a module (e.g., product)")
        print("  createadmin              - Create an admin user")
        print("  routes                   - List all registered routes")
        print("  init-project             - Reset app folder (keeps database)")
        return
    
    command = sys.argv[1]
    
    if command == 'run':
        from app import app
        app.run(debug=True)
    
    elif command == 'makemigrations':
        from flask_migrate import init as migrate_init
        from app import app, db
        
        # Create migrations directory inside app
        migrations_dir = os.path.join(os.path.dirname(__file__), 'app', 'migrations')
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
        
        with app.app_context():
            try:
                from flask_migrate import Migrate
                migrate = Migrate(app, db)
                db.create_all()
                print("✅ Migrations ready!")
            except Exception as e:
                print(f"Error: {e}")
    
    elif command == 'migrate':
        from flask_migrate import upgrade
        from app import app
        migrations_dir = os.path.join(os.path.dirname(__file__), 'app', 'migrations')
        with app.app_context():
            if os.path.exists(migrations_dir):
                upgrade()
                print("✅ Migrations applied!")
            else:
                print("❌ No migrations folder. Run 'makemigrations' first.")
    
    elif command == 'show-migrations':
        from app import app
        with app.app_context():
            print("✅ Migrations:")
            print("  Run 'migrate' to apply migrations")
    
    elif command == 'reset-db':
        from app import app, db
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database reset complete!")
    
    elif command == 'createadmin':
        from app import app
        from app.user.model import User
        from app import db
        
        username = input("Username: ")
        email = input("Email: ")
        password = input("Password: ")
        
        with app.app_context():
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✅ Admin user '{username}' created!")
    
    elif command == 'create-app':
        if len(sys.argv) < 3:
            print("Error: Please provide module name")
            print("Usage: python manage.py create-app <name>")
            return
        
        name = sys.argv[2].lower()
        create_new_module(name)
    
    elif command == 'routes':
        from app import app
        print("\n📋 Registered Routes:")
        print("-" * 60)
        for rule in app.url_map.iter_rules():
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            methods_str = ', '.join(sorted(methods)) if methods else ''
            print(f"  {methods_str:10} {rule.rule}")
        print("-" * 60)
    
    elif command == 'delete-app':
        if len(sys.argv) < 3:
            print("Error: Please provide module name to delete")
            print("Usage: python manage.py delete-app <name>")
            return
        name = sys.argv[2].lower()
        delete_module(name)
    
    elif command == 'init-project':
        delete_app()
        create_app_folder()
        print("✅ Project initialized!")
        print("Database kept. Now run:")
        print("  python manage.py run")
    
    else:
        print(f"❌ Unknown command: {command}")

def create_new_module(name):
    """Create new module with empty files"""
    module_dir = f"app/{name}"
    
    if os.path.exists(module_dir):
        print(f"❌ Module '{name}' already exists!")
        return
    
    os.makedirs(module_dir, exist_ok=True)
    
    # Create __init__.py with auto-register to admin
    init_code = f'''# {name.title()} module
from app.admin import register_model
from app.{name}.model import {name.title()}

# Register to admin
register_model('{name}', {name.title()})
'''
    
    files = {
        'model.py': '',
        'repository.py': '',
        'service.py': '',
        'routes.py': '',
        '__init__.py': init_code
    }
    
    for filename, content in files.items():
        with open(f"{module_dir}/{filename}", 'w') as f:
            f.write(content)
    
    print(f"✅ Module '{name}' created successfully!")
    print(f"\n📁 Structure:")
    print(f"  app/{name}/")
    print(f"    ├── __init__.py  (auto-registered to admin)")
    print(f"    ├── model.py")
    print(f"    ├── repository.py")
    print(f"    ├── service.py")
    print(f"    └── routes.py")
    print(f"\n⚠️  To register routes in app/__init__.py:")
    print(f"    from app.{name}.routes import init_{name}_routes")
    print(f"    init_{name}_routes(app)")
    print(f"\n📝 Add to app/__init__.py to load module:")
    print(f"    from app import {name}")

def delete_app():
    """Delete the app folder"""
    app_dir = 'app'
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
        print("🗑️  Deleted 'app' folder")

def delete_db():
    """Delete the database file"""
    db_file = 'app/app.db'
    if os.path.exists(db_file):
        os.remove(db_file)
        print("🗑️  Deleted 'app/app.db'")

def delete_module(name):
    """Delete a specific module"""
    module_dir = f'app/{name}'
    
    if not os.path.exists(module_dir):
        print(f"❌ Module '{name}' not found!")
        return
    
    if name in ['admin']:
        print(f"❌ Cannot delete '{name}' - it's a core module!")
        return
    
    shutil.rmtree(module_dir)
    print(f"🗑️  Deleted module '{name}'")
    
    # Remove import from app/__init__.py
    app_init_path = 'app/__init__.py'
    if os.path.exists(app_init_path):
        with open(app_init_path, 'r') as f:
            content = f.read()
        
        # Remove the import line
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if f'from app import {name}' in line or f'from app.{name}' in line and 'import' in line:
                continue
            if f'init_{name}_routes(app)' in line:
                continue
            new_lines.append(line)
        
        with open(app_init_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Removed '{name}' from app/__init__.py")
    
    print(f"\n✅ Module '{name}' deleted!")
    print("Restart the server to apply changes.")

def create_app_folder():
    """Create fresh Flask app structure"""
    os.makedirs('app/templates/admin', exist_ok=True)
    
    # app/__init__.py
    app_init = '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
import os

basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Config - database inside app folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes
from app.user.routes import init_user_routes
from app.admin.routes import init_admin_routes

init_user_routes(app)
init_admin_routes(app)

@app.context_processor
def inject_session():
    from flask import session, request
    return dict(session=session, request=request)

# Import modules to register them to admin
from app import user
from app import product
'''
    
    # app/admin/__init__.py
    admin_init = '''# Admin registry - register modules here
ADMIN_MODELS = {}

def register_model(name, model):
    """Register a model to admin"""
    ADMIN_MODELS[name] = model
'''
    
    # app/admin/routes.py
    admin_routes = '''from flask import render_template, request, redirect, url_for, session
from app.admin import ADMIN_MODELS
from app import db
from sqlalchemy import inspect

def init_admin_routes(app):
    
    def login_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('admin_login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/admin/login/', methods=['GET', 'POST'])
    def admin_login():
        from app.user.model import User
        error = None
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['admin_logged_in'] = True
                session['admin_user'] = username
                next_url = request.args.get('next', '/admin/')
                return redirect(next_url)
            else:
                error = "Please enter a correct username and password."
        
        return render_template('admin/login.html', error=error)
    
    @app.route('/admin/logout/')
    def admin_logout():
        session.pop('admin_logged_in', None)
        session.pop('admin_user', None)
        return redirect(url_for('admin_login'))
    
    def get_editable_fields(model_class):
        columns = inspect(model_class).columns
        editable = []
        skip_types = ['DateTime', 'Date', 'Time']
        for col in columns:
            if col.name == 'id':
                continue
            col_type = str(col.type.__class__.__name__)
            if any(t in col_type for t in skip_types):
                continue
            editable.append(col.name)
        return editable
    
    def get_field_types(model_class):
        columns = inspect(model_class).columns
        types = {}
        for col in columns:
            types[col.name] = str(col.type.__class__.__name__)
        return types
    
    def set_model_attrs(obj, model_class, form_data):
        columns = inspect(model_class).columns
        for col in columns:
            if col.name == 'id':
                continue
            
            col_type = str(col.type.__class__.__name__)
            
            if 'BOOLEAN' in col_type.upper():
                value = form_data.get(col.name)
                setattr(obj, col.name, value == 'on' or value == 'true')
            elif col.name in form_data:
                value = form_data.get(col.name)
                if 'INTEGER' in col_type.upper() or 'FLOAT' in col_type.upper() or 'NUMERIC' in col_type.upper():
                    if value:
                        try:
                            setattr(obj, col.name, float(value) if '.' in value else int(value))
                        except ValueError:
                            pass
                else:
                    setattr(obj, col.name, value)
    
    @app.route('/admin/')
    @login_required
    def admin_index():
        return render_template('admin/index.html', models=list(ADMIN_MODELS.keys()), all_models=list(ADMIN_MODELS.keys()))
    
    @app.route('/admin/<model_name>/')
    @login_required
    def admin_model_list(model_name):
        if model_name not in ADMIN_MODELS:
            return "Model not found", 404
        model_class = ADMIN_MODELS[model_name]
        items = model_class.query.all()
        fields = [c.name for c in inspect(model_class).columns]
        return render_template('admin/model_list.html', 
                              model_name=model_name, 
                              model_name_display=model_name.title(),
                              fields=fields, 
                              items=items,
                              all_models=list(ADMIN_MODELS.keys()))
    
    @app.route('/admin/<model_name>/add/', methods=['GET', 'POST'])
    @login_required
    def admin_model_add(model_name):
        if model_name not in ADMIN_MODELS:
            return "Model not found", 404
        model_class = ADMIN_MODELS[model_name]
        fields = get_editable_fields(model_class)
        field_types = get_field_types(model_class)
        
        if request.method == 'POST':
            obj = model_class()
            set_model_attrs(obj, model_class, request.form)
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for('admin_model_list', model_name=model_name))
        
        return render_template('admin/model_form.html', 
                              model_name=model_name,
                              model_name_display=model_name.title(),
                              fields=fields,
                              field_types=field_types,
                              item=None,
                              action='Add')
    
    @app.route('/admin/<model_name>/<int:id>/', methods=['GET', 'POST'])
    @login_required
    def admin_model_edit(model_name, id):
        if model_name not in ADMIN_MODELS:
            return "Model not found", 404
        model_class = ADMIN_MODELS[model_name]
        fields = get_editable_fields(model_class)
        field_types = get_field_types(model_class)
        item = model_class.query.get_or_404(id)
        
        if request.method == 'POST':
            set_model_attrs(item, model_class, request.form)
            db.session.commit()
            return redirect(url_for('admin_model_list', model_name=model_name))
        
        return render_template('admin/model_form.html',
                              model_name=model_name,
                              model_name_display=model_name.title(),
                              fields=fields,
                              field_types=field_types,
                              item=item,
                              action='Edit')
    
    @app.route('/admin/<model_name>/<int:id>/delete/', methods=['GET', 'POST'])
    @login_required
    def admin_model_delete(model_name, id):
        if model_name not in ADMIN_MODELS:
            return "Model not found", 404
        model_class = ADMIN_MODELS[model_name]
        item = model_class.query.get_or_404(id)
        fields = [c.name for c in inspect(model_class).columns]
        
        if request.method == 'POST':
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('admin_model_list', model_name=model_name))
        
        return render_template('admin/delete_confirmation.html',
                              model_name=model_name,
                              model_name_display=model_name.title(),
                              item=item,
                              fields=fields)
'''
    
    # app/user/__init__.py
    user_init = '''# User module
from app.admin import register_model
from app.user.model import User

# Register to admin
register_model('user', User)
'''
    
    # app/user/model.py
    user_model = '''from app import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''
    
    # app/user/repository.py
    user_repository = '''from app import db
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
'''
    
    # app/user/service.py
    user_service = '''from app.user.repository import UserRepository

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
'''
    
    # app/user/routes.py
    user_routes = '''from flask import request, jsonify
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
'''
    
    # app/product/__init__.py
    product_init = '''# Product module
from app.admin import register_model
from app.product.model import Product

# Register to admin
register_model('product', Product)
'''
    
    # app/product/model.py
    product_model = '''from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''
    
    # app/product/repository.py
    product_repository = '''from app import db
from app.product.model import Product

class ProductRepository:
    @staticmethod
    def get_all():
        return Product.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Product.query.get(id)
    
    @staticmethod
    def create(data):
        product = Product()
        product.name = data.get('name')
        product.description = data.get('description', '')
        product.price = float(data.get('price', 0))
        product.stock = int(data.get('stock', 0))
        product.is_active = data.get('is_active', True)
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update(id, data):
        product = Product.query.get(id)
        if product:
            if 'name' in data:
                product.name = data['name']
            if 'description' in data:
                product.description = data['description']
            if 'price' in data:
                product.price = float(data['price'])
            if 'stock' in data:
                product.stock = int(data['stock'])
            if 'is_active' in data:
                product.is_active = data['is_active']
            db.session.commit()
        return product
    
    @staticmethod
    def delete(id):
        product = Product.query.get(id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False
'''
    
    # app/product/service.py
    product_service = '''from app.product.repository import ProductRepository

class ProductService:
    @staticmethod
    def get_all_products():
        return ProductRepository.get_all()
    
    @staticmethod
    def get_product_by_id(id):
        return ProductRepository.get_by_id(id)
    
    @staticmethod
    def create_product(data):
        return ProductRepository.create(data)
    
    @staticmethod
    def update_product(id, data):
        return ProductRepository.update(id, data)
    
    @staticmethod
    def delete_product(id):
        return ProductRepository.delete(id)
'''
    
    # app/product/routes.py
    product_routes = '''from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.product.service import ProductService

def init_product_routes(app):
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        products = ProductService.get_all_products()
        return jsonify([p.to_dict() for p in products]), 200
    
    @app.route('/api/products/<int:id>', methods=['GET'])
    def get_product(id):
        product = ProductService.get_product_by_id(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product.to_dict()), 200
    
    @app.route('/api/products', methods=['POST'])
    @jwt_required()
    def create_product():
        data = request.get_json()
        product = ProductService.create_product(data)
        return jsonify({'message': 'Product created', 'product': product.to_dict()}), 201
    
    @app.route('/api/products/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_product(id):
        data = request.get_json()
        product = ProductService.update_product(id, data)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify({'message': 'Product updated', 'product': product.to_dict()}), 200
    
    @app.route('/api/products/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_product(id):
        if ProductService.delete_product(id):
            return jsonify({'message': 'Product deleted'}), 200
        return jsonify({'error': 'Product not found'}), 404
'''
    
    # Write all files
    files = {
        'app/__init__.py': app_init,
        'app/admin/__init__.py': admin_init,
        'app/admin/routes.py': admin_routes,
        'app/user/__init__.py': user_init,
        'app/user/model.py': user_model,
        'app/user/repository.py': user_repository,
        'app/user/service.py': user_service,
        'app/user/routes.py': user_routes,
        'app/product/__init__.py': product_init,
        'app/product/model.py': product_model,
        'app/product/repository.py': product_repository,
        'app/product/service.py': product_service,
        'app/product/routes.py': product_routes,
    }
    
    for filepath, content in files.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create templates
    os.makedirs('app/templates/admin', exist_ok=True)
    
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask Admin{% endblock %}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #818cf8;
            --secondary: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #f1f5f9;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text: #1e293b;
            --text-light: #64748b;
            --sidebar-bg: #1e293b;
            --sidebar-text: #94a3b8;
        }
        body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.5; min-height: 100vh; display: flex; flex-direction: column; }
        a { color: var(--primary); text-decoration: none; }
        a:hover { color: var(--primary-dark); }
        
        .header { background: var(--surface); height: 64px; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; border-bottom: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); position: fixed; top: 0; left: 0; right: 0; z-index: 100; }
        .header-left { display: flex; align-items: center; gap: 16px; }
        .logo { font-size: 20px; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 8px; }
        .logo svg { width: 28px; height: 28px; }
        .header-right { display: flex; align-items: center; gap: 20px; }
        .user-info { display: flex; align-items: center; gap: 10px; color: var(--text-light); font-size: 14px; }
        .user-avatar { width: 36px; height: 36px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; }
        .logout-btn { background: none; border: 1px solid var(--border); padding: 8px 16px; border-radius: 6px; cursor: pointer; color: var(--text-light); font-size: 14px; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
        .logout-btn:hover { background: var(--bg); color: var(--text); }
        
        .sidebar { width: 260px; background: var(--sidebar-bg); position: fixed; top: 64px; left: 0; bottom: 0; padding: 24px 0; overflow-y: auto; }
        .sidebar-section { margin-bottom: 24px; }
        .sidebar-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--sidebar-text); padding: 0 24px; margin-bottom: 8px; font-weight: 600; }
        .sidebar-menu { list-style: none; }
        .sidebar-menu li a { display: flex; align-items: center; gap: 12px; padding: 10px 24px; color: var(--sidebar-text); font-size: 14px; transition: all 0.2s; }
        .sidebar-menu li a:hover { background: rgba(255,255,255,0.05); color: white; }
        .sidebar-menu li a.active { background: rgba(99, 102, 241, 0.2); color: var(--primary-light); border-right: 3px solid var(--primary); }
        .sidebar-menu li a svg { width: 20px; height: 20px; }
        
        .main { margin-left: 260px; padding: 88px 32px 32px; flex: 1; }
        
        .card { background: var(--surface); border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
        .card-header { padding: 20px 24px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .card-title { font-size: 16px; font-weight: 600; color: var(--text); }
        .card-body { padding: 24px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px; }
        .stat-card { background: var(--surface); border-radius: 12px; padding: 24px; border: 1px solid var(--border); display: flex; align-items: center; gap: 20px; }
        .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .stat-icon.primary { background: rgba(99, 102, 241, 0.1); color: var(--primary); }
        .stat-icon svg { width: 28px; height: 28px; }
        .stat-content h3 { font-size: 28px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
        .stat-content p { color: var(--text-light); font-size: 14px; }
        
        .table { width: 100%; border-collapse: collapse; }
        .table th { text-align: left; padding: 12px 16px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-light); font-weight: 600; border-bottom: 2px solid var(--border); }
        .table td { padding: 16px; border-bottom: 1px solid var(--border); }
        .table tbody tr:hover { background: var(--bg); }
        .table tbody tr:last-child td { border-bottom: none; }
        
        .btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; border: none; text-decoration: none; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: var(--primary-dark); color: white; }
        .btn-secondary { background: var(--bg); color: var(--text); border: 1px solid var(--border); }
        .btn-secondary:hover { background: var(--border); }
        .btn-danger { background: var(--danger); color: white; }
        .btn-danger:hover { background: #dc2626; color: white; }
        .btn-sm { padding: 6px 12px; font-size: 13px; }
        
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text); font-size: 14px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; transition: all 0.2s; }
        .form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
        .form-check { display: flex; align-items: center; gap: 10px; }
        .form-check input { width: 18px; height: 18px; accent-color: var(--primary); }
        
        .alert { padding: 16px 20px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        .alert-danger { background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2); }
        
        .breadcrumbs { display: flex; align-items: center; gap: 8px; margin-bottom: 24px; font-size: 14px; color: var(--text-light); }
        .breadcrumbs a { color: var(--text-light); }
        .breadcrumbs a:hover { color: var(--primary); }
        .breadcrumbs span { color: var(--text); }
        
        .page-header { margin-bottom: 32px; }
        .page-header h1 { font-size: 24px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
        .page-header p { color: var(--text-light); font-size: 15px; }
        
        .model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
        .model-card { background: var(--surface); border-radius: 12px; border: 1px solid var(--border); overflow: hidden; transition: all 0.2s; }
        .model-card:hover { border-color: var(--primary-light); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .model-card-header { padding: 20px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; display: flex; align-items: center; gap: 12px; }
        .model-card-header svg { width: 24px; height: 24px; opacity: 0.9; }
        .model-card-header h3 { font-size: 16px; font-weight: 600; }
        .model-card-body { padding: 20px; }
        .model-card-body a { display: block; padding: 10px 0; color: var(--text); border-bottom: 1px solid var(--border); }
        .model-card-body a:last-child { border-bottom: none; }
        .model-card-body a:hover { color: var(--primary); }
        
        .actions-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-light); }
        .empty-state svg { width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.5; }
        .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--text); }
        
        .footer { background: var(--surface); border-top: 1px solid var(--border); padding: 20px 32px; margin-left: 260px; }
        .footer-content { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; color: var(--text-light); font-size: 13px; }
        .footer-links { display: flex; align-items: center; gap: 12px; }
        .footer-links a { color: var(--text-light); }
        .footer-links a:hover { color: var(--primary); }
        .footer-links span { color: var(--border); }
        
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; }
            .stats-grid { grid-template-columns: 1fr; }
            .model-grid { grid-template-columns: 1fr; }
            .footer { margin-left: 0; text-align: center; }
            .footer-content { flex-direction: column; gap: 10px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-left">
            <div class="logo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                Flask Admin
            </div>
        </div>
        <div class="header-right">
            <div class="user-info">
                <div class="user-avatar">{{ session.get('admin_user', 'A')[0]|upper }}</div>
                <span>Welcome, <strong>{{ session.get('admin_user', 'admin') }}</strong></span>
            </div>
            <a href="/admin/logout/" class="logout-btn">Logout</a>
        </div>
    </header>
    
    <nav class="sidebar">
        <div class="sidebar-section">
            <div class="sidebar-title">Main</div>
            <ul class="sidebar-menu">
                <li><a href="/admin/">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                    Dashboard
                </a></li>
            </ul>
        </div>
        <div class="sidebar-section">
            <div class="sidebar-title">Models</div>
            <ul class="sidebar-menu">
                {% for model_name in all_models %}
                <li><a href="/admin/{{ model_name }}/">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    {{ model_name|title }}
                </a></li>
                {% endfor %}
            </ul>
        </div>
    </nav>
    
    <main class="main">
        {% block content %}{% endblock %}
    </main>
    
    <footer class="footer">
        <div class="footer-content">
            <p>&copy; 2026 Flask Admin Panel</p>
            <div class="footer-links">
                <a href="/admin/">Home</a>
            </div>
        </div>
    </footer>
</body>
</html>
'''
    
    index_html = '''{% extends "admin/base.html" %}
{% block content %}
<div class="page-header" style="text-align: center;">
    <h1>Dashboard</h1>
    <p>Welcome to Flask Admin Panel</p>
</div>

<div style="display: flex; justify-content: center;">
    <div style="width: 100%; max-width: 1000px;">
        <div class="stats-grid">
            {% for model_name in models %}
            <div class="stat-card">
                <div class="stat-icon primary">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </div>
                <div class="stat-content">
                    <h3>{{ model_name|title }}</h3>
                    <p><a href="/admin/{{ model_name }}/">Manage {{ model_name }}s</a></p>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">Quick Actions</span>
            </div>
            <div class="card-body">
                <div class="model-grid">
                    {% for model_name in models %}
                    <div class="model-card">
                        <div class="model-card-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                            <h3>{{ model_name|title }}s</h3>
                        </div>
                        <div class="model-card-body">
                            <a href="/admin/{{ model_name }}/add/">+ Add New {{ model_name|title }}</a>
                            <a href="/admin/{{ model_name }}/">View All {{ model_name|title }}s</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    model_list_html = '''{% extends "admin/base.html" %}
{% block content %}
<div style="display: flex; justify-content: center;">
    <div style="width: 100%; max-width: 1200px;">
        <div class="breadcrumbs" style="justify-content: center;">
            <a href="/admin/">Home</a>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            <span>{{ model_name_display }}s</span>
        </div>

        <div class="page-header" style="text-align: center;">
            <h1>{{ model_name_display }}s</h1>
            <p>Manage your {{ model_name_display.lower() }}s</p>
        </div>

        <div class="actions-row">
            <div></div>
            <a href="/admin/{{ model_name }}/add/" class="btn btn-primary">+ Add {{ model_name_display }}</a>
        </div>

        <div class="card">
            <div class="card-body" style="padding: 0;">
                {% if items %}
                <table class="table">
                    <thead>
                        <tr>
                            {% for field in fields %}
                            <th>{{ field|title }}</th>
                            {% endfor %}
                            <th style="width: 180px;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            {% for field in fields %}
                            <td>{{ item[field] if item[field] is not none else '' }}</td>
                            {% endfor %}
                            <td>
                                <a href="/admin/{{ model_name }}/{{ item.id }}/" class="btn btn-secondary btn-sm">Edit</a>
                                <a href="/admin/{{ model_name }}/{{ item.id }}/delete/" class="btn btn-danger btn-sm">Delete</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    <h3>No {{ model_name_display }}s yet</h3>
                    <p>Get started by adding your first {{ model_name_display.lower() }}.</p>
                    <a href="/admin/{{ model_name }}/add/" class="btn btn-primary" style="margin-top: 16px;">+ Add {{ model_name_display }}</a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    model_form_html = '''{% extends "admin/base.html" %}
{% block content %}
<div class="breadcrumbs" style="justify-content: center;">
    <a href="/admin/">Home</a>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    <a href="/admin/{{ model_name }}/">{{ model_name_display }}s</a>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    <span>{{ action }}</span>
</div>

<div class="page-header" style="text-align: center;">
    <h1>{{ action }} {{ model_name_display }}</h1>
</div>

<div class="card" style="max-width: 600px; margin: 0 auto;">
    <div class="card-body">
        <form method="POST">
            {% for field in fields %}
            <div class="form-group">
                <label for="id_{{ field }}">{{ field|title }}</label>
                {% if field_types.get(field) == 'Boolean' %}
                <div class="form-check">
                    <input type="checkbox" name="{{ field }}" id="id_{{ field }}"{% if item and item[field] %} checked{% endif %}>
                    <label for="id_{{ field }}">Yes / No</label>
                </div>
                {% else %}
                <input type="text" name="{{ field }}" id="id_{{ field }}" class="form-control" value="{{ item[field] if item else '' }}">
                {% endif %}
            </div>
            {% endfor %}
            
            <div style="display: flex; gap: 12px; margin-top: 24px; justify-content: center;">
                <button type="submit" class="btn btn-primary">{{ action }} {{ model_name_display }}</button>
                <a href="/admin/{{ model_name }}/" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''
    
    delete_html = '''{% extends "admin/base.html" %}
{% block content %}
<div class="breadcrumbs" style="justify-content: center;">
    <a href="/admin/">Home</a>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    <a href="/admin/{{ model_name }}/">{{ model_name_display }}s</a>
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    <span>Delete</span>
</div>

<div class="page-header" style="text-align: center;">
    <h1>Delete {{ model_name_display }}</h1>
</div>

<div class="card" style="max-width: 500px; margin: 0 auto;">
    <div class="card-body">
        <div class="alert alert-danger" style="text-align: center;">
            <strong>Warning!</strong> Are you sure you want to delete "{{ item[fields[1]] if fields|length > 1 else item.id }}"?
        </div>
        <p style="margin-bottom: 20px; color: var(--text-light); text-align: center;">This action cannot be undone.</p>
        
        <form method="POST">
            <div style="display: flex; gap: 12px; justify-content: center;">
                <button type="submit" class="btn btn-danger">Yes, Delete</button>
                <a href="/admin/{{ model_name }}/" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''
    
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | Flask Admin</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --bg: #f1f5f9;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text: #1e293b;
            --danger: #ef4444;
        }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        
        .login-container { width: 100%; max-width: 400px; padding: 20px; }
        .login-card { background: var(--surface); border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
        .login-header { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); padding: 40px 30px; text-align: center; color: white; }
        .login-header h1 { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
        .login-header p { font-size: 14px; opacity: 0.9; }
        .login-body { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 14px; }
        .form-group input { width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: var(--primary); }
        .btn-login { width: 100%; padding: 14px; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn-login:hover { background: var(--primary-dark); }
        .alert-danger { padding: 14px 16px; border-radius: 8px; margin-bottom: 20px; background: rgba(239,68,68,0.1); color: var(--danger); font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <h1>Flask Admin</h1>
                <p>Sign in to your account</p>
            </div>
            <div class="login-body">
                {% if error %}
                <div class="alert-danger">{{ error }}</div>
                {% endif %}
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required autofocus>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn-login">Sign In</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''
    
    templates = {
        'app/templates/admin/base.html': base_html,
        'app/templates/admin/index.html': index_html,
        'app/templates/admin/model_list.html': model_list_html,
        'app/templates/admin/model_form.html': model_form_html,
        'app/templates/admin/delete_confirmation.html': delete_html,
        'app/templates/admin/login.html': login_html,
    }
    
    for filepath, content in templates.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("📁 Created app structure with:")
    print("   - admin module (routes, CRUD)")
    print("   - user module (model, repo, service, API routes)")
    print("   - product module (model, repo, service, API routes)")
    print("   - admin templates (base, index, model_list, model_form, delete, login)")
    print("   - modern Flask-style design")

if __name__ == '__main__':
    main()
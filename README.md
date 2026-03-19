# Flask Admin Panel

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A modern, Django-like admin panel for Flask with auto-discovering models and CRUD operations. Built with simplicity and elegance in mind.

## Features

- **Auto-discovering Models** - Register models to admin panel automatically
- **Full CRUD Operations** - Create, Read, Update, Delete out of the box
- **User Authentication** - Login-protected admin panel
- **RESTful API** - JWT-based authentication for API endpoints
- **Modern UI** - Clean, responsive Flask-style design
- **Modular Structure** - Easy to extend with new modules

## Quick Start

```bash
# Clone the repository
git clone https://github.com/SertoriusX/Flask-Admin-Panel.git
cd Flask-Admin-Panel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize project
python manage.py init-project

# Create database
python manage.py reset-db

# Create admin user
python manage.py createadmin

# Run server
python manage.py run
```

Visit: http://127.0.0.1:5000/admin/

## Commands

| Command | Description |
|---------|-------------|
| `python manage.py run` | Run development server |
| `python manage.py reset-db` | Reset database |
| `python manage.py createadmin` | Create admin user |
| `python manage.py routes` | List all routes |
| `python manage.py create-app <name>` | Create new module |
| `python manage.py delete-app <name>` | Delete a module |

## Creating a New Module

### 1. Create module structure
```bash
python manage.py create-app category
```

### 2. Add routes in `app/__init__.py`
```python
from app.category.routes import init_category_routes
init_category_routes(app)
```

### 3. Register to admin in `app/category/__init__.py`
```python
from app.admin import register_model
from app.category.model import Category
register_model('category', Category)
```

### 4. Define model in `app/category/model.py`
```python
from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
```

The module automatically appears in the admin panel!

## Project Structure

```
Flask-Admin-Panel/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── admin/               # Admin panel module
│   │   ├── __init__.py      # Model registry
│   │   └── routes.py        # CRUD routes
│   ├── user/                # User authentication
│   │   ├── model.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── routes.py
│   ├── product/             # Example module
│   │   ├── model.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── routes.py
│   └── templates/admin/     # Admin templates
├── manage.py                # CLI commands
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/register` - Register user
- `POST /api/login` - Login (returns JWT)
- `GET /api/me` - Get current user

### Products (Example)
- `GET /api/products` - List all
- `GET /api/products/<id>` - Get one
- `POST /api/products` - Create (JWT required)
- `PUT /api/products/<id>` - Update (JWT required)
- `DELETE /api/products/<id>` - Delete (JWT required)

## Admin Panel Preview

The admin panel features:
- Modern indigo color scheme
- Responsive sidebar navigation
- Centered content layouts
- Clean form designs
- Table views with actions
- Delete confirmations

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt
- **Database**: SQLite (easily swappable)
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Auth**: Session-based (admin), JWT (API)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**SertoriusX**
- GitHub: [@SertoriusX](https://github.com/SertoriusX)

---

⭐ Star this repo if you find it helpful!

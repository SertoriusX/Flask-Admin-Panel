from flask import render_template, request, redirect, url_for, session
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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import login_manager, LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

db = SQLAlchemy()
DB_NAME = 'database.db'
migrate = Migrate()

def create_app():
    load_dotenv()  

    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:8501"], 
            "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"]
        }
    }, supports_credentials=True)
    
    # Debugging: Check loaded environment variables
    # print("Loaded SECRET_KEY:", os.getenv('SECRET_KEY'))
    # print("Loaded SQLALCHEMY_DATABASE_URI:", os.getenv('SQLALCHEMY_DATABASE_URI'))

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False')

    db.init_app(app) 
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth
    from .rag import rag
    from .users import users
    from .rag_api import rag_api
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(rag, url_prefix='/rag')
    app.register_blueprint(users, url_prefix='/')
    app.register_blueprint(rag_api, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    from .models import User, RAGQuery, Admin
    
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        admin = Admin.query.get(int(id))
        if admin:
            return admin
        
        return User.query.get(int(id))

    return app 

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        # Use the application context
        with app.app_context():
            db.create_all()
        print('Created Database!')

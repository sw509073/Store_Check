from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Update with your MySQL database credentials
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Satish509073@localhost/store_monitoring'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Create database tables (initial creation, not migrations)
        db.create_all()
    
    return app

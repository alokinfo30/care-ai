# app/__init__.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

load_dotenv()

def create_app():
    """Application factory pattern for Flask app"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    try:
        from app.main import main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        logging.warning(f"Main blueprint not loaded: {e}")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return app
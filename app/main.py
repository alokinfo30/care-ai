# app/main.py
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import json
import uuid
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Import crew
try:
    from app.crew import SmartphoneRobotCrew
    CREW_AVAILABLE = True
    logger.info("✅ SmartphoneRobotCrew imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Crew not available: {e}")
    CREW_AVAILABLE = False

# Service mapping
SERVICES = {
    "perceive": {
        "name": "Sensor Analysis",
        "icon": "📱",
        "description": "Analyze smartphone sensor data"
    },
    "reason": {
        "name": "Context Understanding",
        "icon": "🧠",
        "description": "Understand user context and needs"
    },
    "act": {
        "name": "Smart Actions",
        "icon": "⚡",
        "description": "Execute helpful actions automatically"
    },
    "monitor": {
        "name": "Health Monitoring",
        "icon": "❤️",
        "description": "Monitor health and safety"
    }
}

SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,hi,es,fr,de,zh').split(',')

@main_bp.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                         services=SERVICES, 
                         languages=SUPPORTED_LANGUAGES)

@main_bp.route('/api/process', methods=['POST'])
def process_sensor_data():
    """Process sensor data and generate actions"""
    try:
        data = request.json
        user_id = data.get('user_id', str(uuid.uuid4()))
        sensor_data = data.get('sensor_data', '')
        language = data.get('language', 'en')
        
        if not sensor_data:
            return jsonify({
                'error': 'Missing sensor data',
                'status': 'error'
            }), 400
        
        if not CREW_AVAILABLE:
            return jsonify({
                'error': 'CrewAI not available',
                'status': 'error'
            }), 500

        # Enqueue processing to background worker to keep API event-driven
        try:
            from redis import Redis
            from rq import Queue
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            redis_conn = Redis.from_url(redis_url)
            q = Queue('default', connection=redis_conn)
            job = q.enqueue('app.worker.handle_sensor_job', sensor_data, user_id, language, job_timeout=900)

            return jsonify({
                'status': 'accepted',
                'job_id': job.get_id(),
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        except Exception as e:
            logger.error(f"Queueing failed: {e}")
            # Fallback to synchronous processing if queueing fails
            try:
                crew = SmartphoneRobotCrew()
                result = crew.process_sensor_data(sensor_data, user_id, language)
                if result.get('status') == 'error':
                    return jsonify({'error': result.get('error', 'Unknown error'), 'status': 'error'}), 500
                return jsonify({'status': 'success', 'result': result, 'timestamp': datetime.utcnow().isoformat()})
            except Exception as e2:
                logger.error(f"Synchronous fallback failed: {e2}")
                return jsonify({'error': str(e2), 'status': 'error'}), 500
        
    except Exception as e:
        logger.error(f"Error processing: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'crew_available': CREW_AVAILABLE,
        'version': '1.0.0',
        'features': list(SERVICES.keys()),
        'languages_supported': len(SUPPORTED_LANGUAGES)
    })

@main_bp.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    try:
        from app.model_manager import model_manager
        results = model_manager.test_providers()
        available = [m for m, v in results.items() if v]
        
        return jsonify({
            'status': 'success',
            'models': {
                'primary': os.getenv('OPENROUTER_PRIMARY_MODEL', 'openai/gpt-4o-mini'),
                'fallbacks': os.getenv('OPENROUTER_FALLBACK_MODELS', '').split(','),
                'available': available,
                'all_tested': results
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
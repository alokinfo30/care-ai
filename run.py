# run.py
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("=" * 70)
    print("🤖 Smartphone Robot - AI Ambient Companion")
    print("=" * 70)
    print(f"🚀 Server running at: http://localhost:{port}")
    print(f"📱 Open in your browser")
    print("=" * 70)
    print("🤖 AI Agents:")
    print("  1. 📱 Perception Agent - Analyzes sensor data")
    print("  2. 🧠 Reasoning Agent - Understands context")
    print("  3. ⚡ Action Agent - Executes tasks")
    print("  4. 📊 Context Agent - Manages memory")
    print("=" * 70)
    print("🌍 Supported Languages:")
    print("  English, Hindi, Spanish, French, German, Chinese")
    print("=" * 70)
    print("🤖 Turning Smartphones into Intelligent Companions")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
# care-ai
AI-Powered Smartphone-as-a-Robotic Care

AI-powered "Smartphone-as-a-Robot" system that turns any smartphone into an intelligent ambient companion using CrewAI and OpenRouter.

SmartphoneRobot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── model_manager.py
│   ├── agents.py
│   ├── tasks.py
│   ├── crew.py
│   ├── models.py
│   └── utils.py
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── data/
│   └── .gitkeep
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md


# 🤖 Smartphone Robot - AI Ambient Companion

Turn your smartphone into an intelligent companion that understands, monitors, and helps you in daily life.

## Features

- 📱 **Sensor Analysis**: Understand user activity from smartphone sensors
- 🧠 **Context Understanding**: Know what the user is doing and what they need
- ⚡ **Smart Actions**: Automate digital tasks and provide proactive assistance
- ❤️ **Health Monitoring**: Detect falls, monitor activity, and alert caregivers
- 🌍 **Multi-Language Support**: 6+ languages available

## Architecture

### AI Agents

1. **Perception Agent**: Analyzes sensor data (accelerometer, gyroscope, GPS, camera, microphone)
2. **Reasoning Agent**: Understands user context and determines appropriate actions
3. **Action Agent**: Executes actions through voice, notifications, and automation
4. **Context Agent**: Maintains user memory, preferences, and history

### Technology Stack

- **CrewAI** - Multi-agent orchestration
- **OpenRouter** - Multi-model support with auto-fallback
- **Flask** - Web framework
- **Pydantic** - Data validation
- **HTML/CSS/JS** - Responsive frontend

### Models Used

| Model | Provider | Use Case |
|-------|----------|----------|
| `openai/gpt-4o-mini` | OpenAI | Perception & Analysis |
| `mistralai/mixtral-8x22b-instruct` | Mistral | Reasoning |
| `meta-llama/llama-3.1-8b-instruct` | Meta | Action Execution |
| `deepseek/deepseek-chat` | DeepSeek | Context Memory |

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd SmartphoneRobot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your OpenRouter API key
# (see .env.example for template)

# 5. Run the application
python run.py



Configuration
Environment Variables
Variable	Description
OPENROUTER_API_KEY	Your OpenRouter API key
OPENROUTER_PRIMARY_MODEL	Primary model to use
OPENROUTER_FALLBACK_MODELS	Fallback models
SUPPORTED_LANGUAGES	Comma-separated language codes
API Endpoints
Endpoint	Method	Description
/	GET	Web interface
/api/process	POST	Process sensor data
/api/models	GET	List available models
/api/health	GET	Health check





## Step 19: Final Commands

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenRouter API key to .env

# 5. Run the application
python run.py

# 6. Open browser
# http://localhost:5000




Start Redis (platform-specific). Example: redis-server
Start an RQ worker:
rq worker default --url redis://localhost:6379/0
Start the web app (as you already run):
gunicorn --workers 1 -k gevent --timeout 120 --access-logfile - --error-logfile - --bind 0.0.0.0:$PORT run:app


✅ Features:


4 Specialized AI Agents for perception, reasoning, action, and context
6+ Languages support
Sensor Analysis from accelerometer, gyroscope, GPS, and more
Health Monitoring with fall detection and activity tracking
Task Automation for digital tasks
Auto-Fallback between 4 models
Responsive Design for mobile and desktop

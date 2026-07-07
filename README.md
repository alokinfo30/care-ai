# care-ai

An AI-powered system that turns any smartphone into an intelligent ambient companion for proactive care using CrewAI and OpenRouter.

# 🤖 Care AI - Your Ambient Companion

Turn your smartphone into an intelligent companion that understands your context, monitors for risks, and provides proactive assistance.

## Features

- 📱 **Sensor Analysis**: Understand user activity from smartphone sensors
- 🧠 **Context Understanding**: Know what the user is doing and what they need
- ⚡ **Smart Actions**: Automate digital tasks and provide proactive assistance
- ❤️ **Health Monitoring**: Detect falls, monitor activity, and alert caregivers
- 🌍 **Multi-Language Support**: 6+ languages available
- 🔄 **Automatic Model Fallback**: Ensures reliability by switching between multiple LLMs.
- 🔊 **Text-to-Speech**: Provides voice-based reminders and alerts.
- 🔋 **Efficient Event Handling**: Uses client-side and server-side debouncing to conserve battery life.
- 🐳 **Containerized**: Ready for deployment with Docker.

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

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An OpenRouter API Key
- Redis (for production mode)

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/care-ai.git
cd care-ai

# 2. Create and activate a virtual environment
python -m venv venv
# On macOS/Linux:
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file from the example
cp .env.example .env

# 5. Add your OpenRouter API key to the .env file
# OPENROUTER_API_KEY="sk-or-..."
```

### Running the Application

#### Development Mode

This mode is suitable for local development and testing.

```bash
# Run the Flask application
python run.py
```
Now, open your browser and navigate to `http://localhost:5000`.

#### Production Mode (with Redis & RQ)

This mode uses `gunicorn` for the web server and `rq` with `redis` for background job processing, which is recommended for production deployments.

```bash
# 1. Start your Redis server (platform-specific)
redis-server

# 2. In a new terminal, start the RQ worker
rq worker default --url redis://localhost:6379/0

# 3. In another terminal, start the Gunicorn web server
gunicorn --workers 1 -k gevent --timeout 120 --bind 0.0.0.0:5000 run:app
```

## ⚙️ Configuration

The application can be configured via environment variables in the `.env` file.

| Variable                   | Description                                             | Default                        |
| -------------------------- | ------------------------------------------------------- | ------------------------------ |
| `OPENROUTER_API_KEY`       | **Required.** Your OpenRouter API key.                  | `""`                           |
| `OPENROUTER_PRIMARY_MODEL` | The main model for processing.                          | `openai/gpt-4o-mini`           |
| `OPENROUTER_FALLBACK_MODELS`| Comma-separated list of fallback models.                | `""`                           |
| `SUPPORTED_LANGUAGES`      | Comma-separated list of supported language codes.       | `en,hi,es,fr,de,zh`            |
| `REDIS_URL`                | The connection URL for your Redis instance.             | `redis://localhost:6379/0`     |
| `DEBOUNCE_SECS`            | Server-side debounce interval in seconds for sensor jobs. | `5`                            |

## 🧪 Running Tests

The project uses `pytest` for testing. Ensure your `OPENROUTER_API_KEY` is set in the environment.

```bash
pytest
```

## 🐳 Docker

You can build and run the application using Docker.

```bash
# 1. Build the Docker image
docker build -t care-ai .

# 2. Run the container (don't forget to pass the API key)
docker run -p 5000:5000 -e OPENROUTER_API_KEY="your_api_key" care-ai
```

## 🌐 API Endpoints

| Endpoint      | Method | Description                               |
| ------------- | ------ | ----------------------------------------- |
| `/`           | `GET`  | Renders the main web interface.           |
| `/api/process`| `POST` | Processes sensor data via background job. |
| `/api/models` | `GET`  | Lists available and tested AI models.     |
| `/api/health` | `GET`  | Provides a health check of the service.   |

---

*This project is a demonstration of building a proactive, multi-agent AI system.*

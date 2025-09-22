# 🤖 AI Task Planner

A modern, intelligent travel planning application powered by AI agents and built with Streamlit.

## ✨ Features

- **AI-Powered Planning**: Uses CrewAI agents to generate intelligent travel plans
- **Modern Interface**: Beautiful, responsive Streamlit web interface
- **Real-time Progress**: Live progress tracking during plan generation
- **Plan Management**: Save, view, search, and manage your travel plans
- **Export Functionality**: Download plans as JSON files
- **Database Integration**: Persistent storage of all your plans

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Option 1: Using the run script
python run_streamlit.py

# Option 2: Direct Streamlit command
streamlit run streamlit_app.py
```

### 3. Access the Application

- **URL**: http://localhost:8501
- **Auto-opens** in your default browser

## 🛠️ Configuration (Optional)

Set environment variables for enhanced functionality:

```bash
# For real web search results
set SERPAPI_KEY=your_serpapi_key_here

# For weather information
set OPENWEATHER_API_KEY=your_openweather_key_here
```

## 📱 Usage

### Create New Plan
1. Enter your travel goal in the text area
2. Click "🚀 Generate Plan" to start AI planning
3. Watch real-time progress and status updates
4. View your generated plan with detailed steps and recommendations

### View Plans History
1. Browse all your saved plans
2. Search and filter plans
3. View, edit, or delete existing plans
4. Export plans as JSON files

## 🏗️ Project Structure

```
ai_task_planner/
├── agents/
│   └── planner_agent.py      # AI agent with tools
├── database/
│   ├── database.py           # Database connection
│   └── models.py             # Data models
├── streamlit_app.py          # Main Streamlit application
├── run_streamlit.py          # Run script
├── test_agent.py             # Test script
├── requirements.txt          # Dependencies
├── task_planner.db          # SQLite database
└── README.md                # This file
```

## 🔧 Technology Stack

- **Frontend**: Streamlit (Modern web interface)
- **AI Framework**: CrewAI (Multi-agent AI system)
- **Database**: SQLite (Lightweight, file-based)
- **Tools**: Web search, Weather forecasting
- **APIs**: SerpAPI, OpenWeatherMap

## 🎯 Key Components

### AI Agent (`agents/planner_agent.py`)
- **Travel Planner Agent**: Specialized in creating detailed travel plans
- **Web Search Tool**: Gathers current information about destinations
- **Weather Tool**: Provides weather forecasts for planning
- **Plan Generation**: Creates structured, actionable travel plans

### Database (`database/`)
- **SQLite Database**: Stores all generated plans
- **Models**: TaskPlan model with steps and enriched information
- **Persistence**: All plans are automatically saved

### Streamlit Interface (`streamlit_app.py`)
- **Modern UI**: Clean, professional interface
- **Real-time Updates**: Live progress tracking
- **Interactive Elements**: Search, filter, export functionality
- **Responsive Design**: Works on all devices

## 🐛 Troubleshooting

1. **Port Already in Use**: Streamlit will automatically use the next available port
2. **Database Issues**: Ensure the database file has proper permissions
3. **API Keys**: Check that environment variables are set correctly
4. **Dependencies**: Make sure all packages are installed in the virtual environment

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal to stop the Streamlit server.

## 📊 Performance

- **Fast Loading**: Optimized for quick startup and response times
- **Efficient Database**: SQLite for fast data access
- **Background Processing**: Non-blocking plan generation
- **Caching**: Streamlit's built-in caching for better performance



# run_streamlit.py
import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    print("🚀 Starting AI Task Planner with Streamlit...")
    print("📱 The app will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Task Planner...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()

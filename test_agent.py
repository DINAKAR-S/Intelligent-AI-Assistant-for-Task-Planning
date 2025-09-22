# test_agent.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_basic_imports():
    """Test if all modules can be imported"""
    try:
        from agents.planner_agent import planner_agent
        from database.database import create_tables, SessionLocal
        from database.models import TaskPlan
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection"""
    try:
        from database.database import create_tables, SessionLocal
        create_tables()
        db = SessionLocal()
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_agent():
    """Test agent with simple goal"""
    try:
        from agents.planner_agent import planner_agent
        from crewai import Task, Crew

        print("🤖 Testing agent with simple goal...")

        task = Task(
            description="Plan a 1-day local exploration of San Francisco, including popular attractions, restaurants, and activities. Create a detailed itinerary with specific times and locations.",
            agent=planner_agent,
            expected_output="A comprehensive 1-day itinerary for San Francisco with specific attractions, restaurants, activities, and logistics including timing and transportation."
        )

        crew = Crew(agents=[planner_agent], tasks=[task])
        result = crew.kickoff()  # Standard method

        if result:
            print("✅ Agent test successful - Got a response")
            print("Sample output:", str(result)[:200], "...")
            return True
        else:
            print("❌ Agent test failed - No result returned")
            return False

    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False


def run_tests():
    """Run all tests"""
    print("🧪 Running AI Task Planner Tests...\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Database Connection", test_database),
        ("Agent Functionality", test_agent)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run 'python run_streamlit.py' to start the Streamlit application")
        print("2. Open http://localhost:8501 in your browser")
        print("3. Create your first task plan!")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    run_tests()
# agents/planner_agent.py
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests, os, re
from dotenv import load_dotenv

load_dotenv()

# ------------------ TOOLS ------------------ #
class WebSearchInput(BaseModel):
    query: str = Field(description="Search query to look up information")

class WeatherInput(BaseModel):
    city: str = Field(description="City name to get weather information for")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for current information about topics, resources, guides, best practices, etc."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            actual_query = query.get('query') if isinstance(query, dict) else str(query)
            serpapi_key = os.getenv("SERPAPI_KEY")
            if serpapi_key:
                return self._serpapi_search(actual_query)
            return self._duckduckgo_search(actual_query)
        except Exception as e:
            return f"Search failed: {str(e)}"

    def _serpapi_search(self, query: str) -> str:
        url = "https://serpapi.com/search"
        params = {"q": query, "engine": "google", "api_key": os.getenv("SERPAPI_KEY"), "num": 5}
        response = requests.get(url, params=params)
        data = response.json()
        results = []
        for result in data.get("organic_results", [])[:5]:
            results.append(f"Title: {result.get('title','')}\nSnippet: {result.get('snippet','')}\n")
        return "\n".join(results) if results else "No results found"

    def _duckduckgo_search(self, query: str) -> str:
        return f"Demo search results for '{query}':\n1. Best practices\n2. Guides\n3. Resources\n4. Step-by-step approaches\n5. Tips"

class WeatherTool(BaseTool):
    name: str = "weather_forecast"
    description: str = "Get current weather and forecast for any city"
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, city: str) -> str:
        try:
            actual_city = city.get('city') if isinstance(city, dict) else str(city)
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key: return "Weather API key not configured"
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": actual_city, "appid": api_key, "units": "metric"}
            response = requests.get(url, params=params)
            if response.status_code != 200: return f"Weather data not available for {actual_city}"
            data = response.json()
            return f"{data['main']['temp']}°C, {data['weather'][0]['description'].title()}, Humidity: {data['main']['humidity']}%"
        except Exception as e:
            return f"Weather lookup failed: {str(e)}"

# Initialize tools
web_search_tool = WebSearchTool()
weather_tool = WeatherTool()
available_tools = [web_search_tool, weather_tool]

# ------------------ PLANNER AGENT ------------------ #
class TaskPlannerAgent:
    def __init__(self):
        self.llm = LLM(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

    def create_plan(self, goal: str) -> dict:
        """Create structured day-wise plan with enrichment"""
        # Step 1: Get main steps from LLM
        planner_agent = Agent(
            role='Task Planning Specialist',
            goal='Break down complex goals into actionable steps',
            backstory='You excel at creating detailed, step-by-step plans for any type of goal.',
            llm=self.llm,
            verbose=True
        )

        task = Task(
            description=f"Goal: '{goal}'. Create a detailed, actionable, day-wise plan including travel, food, sightseeing, and rest.",
            expected_output="Numbered day-wise plan with steps",
            agent=planner_agent
        )

        crew = Crew(
            agents=[planner_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        raw_result = crew.kickoff()
        result_text = str(raw_result.raw) if hasattr(raw_result, 'raw') else str(raw_result)

        return self._parse_result(result_text, goal)

    # ------------------ PARSING ------------------ #
    def _parse_result(self, text: str, goal: str) -> dict:
        """Parse raw LLM output into structured plan"""
        steps = []
        day_plan = {}
        current_day = None

        for line in text.split('\n'):
            line = line.strip()
            day_match = re.match(r'Day\s*(\d+)', line, re.I)
            step_match = re.match(r'^\s*\d+[\.\)]\s+(.*)', line)

            if day_match:
                current_day = f"Day {day_match.group(1)}"
                day_plan[current_day] = []
            elif step_match and current_day:
                day_plan[current_day].append(step_match.group(1))

        # If no day-wise, fallback to plain numbered steps
        if not day_plan:
            day_plan = {"Day 1": [line for line in text.split('\n') if line.strip()][:10]}

        # Add enrichment
        enriched_info = {
            "weather_considerations": self._get_weather(goal),
            "recommendations": self._get_recommendations(goal),
            "budget_tips": self._get_budget_tips(goal)
        }

        return {
            "goal": goal,
            "steps": [{"day": day, "tasks": tasks} for day, tasks in day_plan.items()],
            "enriched_info": enriched_info,
            "full_result": text
        }

    # ------------------ ENRICHMENT ------------------ #
    def _get_weather(self, goal: str) -> str:
        city_match = re.search(r'\b(?:in|to)\s+([A-Za-z\s]+)', goal)
        city = city_match.group(1) if city_match else "destination"
        return weather_tool._run(city)

    def _get_recommendations(self, goal: str) -> str:
        return web_search_tool._run(f"best things to do, food, and attractions in {goal}")

    def _get_budget_tips(self, goal: str) -> str:
        return web_search_tool._run(f"budget tips for {goal}")

# Initialize agent
planner_agent = TaskPlannerAgent()

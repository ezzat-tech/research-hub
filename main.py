import os
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any
import traceback

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3.1:free"

# Initialize FastAPI app
app = FastAPI(title="Research Hub", description="AI-powered research report generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files from frontend directory"""
    return FileResponse(f"frontend/{file_path}")

# Pydantic models
class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str
    status: str
    session_id: str = ""
    queue_position: int = 0

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8001",
            "X-Title": "Research Hub"
        }
    
    def generate_research_plan(self, topic: str) -> str:
        """Generate a research plan for the given topic"""
        prompt = f"""
        Create a comprehensive research plan for the topic: "{topic}"
        
        The plan should include:
        1. Key research questions to investigate
        2. Important subtopics to explore
        3. Specific search terms and queries to use
        4. Areas of focus for data collection
        
        Format the response as a clear, structured research plan that can guide web searches and information gathering.
        """
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(
                f"OpenRouter model {OPENROUTER_MODEL} failed with status {response.status_code}: {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]

    def generate_report(self, topic: str, research_data: str) -> str:
        """Generate a comprehensive research report"""
        prompt = f"""
        Based on the research data provided, create a comprehensive research report on the topic: "{topic}"
        
        Research Data:
        {research_data}
        
        Please structure the report with the following sections:
        
        1. Executive Summary (brief overview of key findings)
        2. Introduction (context and background)
        3. Key Findings (main findings, organized by themes)
        4. Conclusion (summary and implications)
        5. Thesis (main argument or position)
        
        Important formatting rules:
        - Use exact section headers: "Executive Summary", "Introduction", "Key Findings", "Conclusion", "Thesis"
        - Do NOT include "Body:" prefix before "Key Findings"
        - Ensure each section header is on its own line
        - Make the report professional and academic in tone
        - Include specific details and evidence from the research data
        - Use clear, concise language
        - Ensure proper paragraph structure with each section clearly separated
        """
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7
        }

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(
                f"OpenRouter model {OPENROUTER_MODEL} failed with status {response.status_code}: {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]

class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"

    def search(self, query: str, max_results: int = 5) -> str:
        """Search for information using Tavily API"""
        try:
            response = httpx.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": False,
                    "max_results": max_results,
                    "include_domains": [],
                    "exclude_domains": []
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Tavily API error: {response.status_code}")
            
            data = response.json()
            
            # Extract and format the search results
            results = []
            if "results" in data:
                for result in data["results"]:
                    title = result.get("title", "No title")
                    content = result.get("content", "No content")
                    url = result.get("url", "No URL")
                    results.append(f"Title: {title}\nContent: {content}\nSource: {url}\n")
            
            # Include the answer if available
            if "answer" in data and data["answer"]:
                results.insert(0, f"Summary: {data['answer']}\n")
            
            return "\n".join(results) if results else "No search results found."
            
        except Exception as e:
            raise Exception(f"Tavily search failed: {str(e)}")

# Initialize clients only if API keys are available
if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
    openrouter_client = OpenRouterClient(OPENROUTER_API_KEY)
else:
    openrouter_client = None
    print("WARNING: OpenRouter client not initialized - API key missing")

if TAVILY_API_KEY and TAVILY_API_KEY != "your_tavily_api_key_here":
    tavily_client = TavilyClient(TAVILY_API_KEY)
else:
    tavily_client = None
    print("WARNING: Tavily client not initialized - API key missing")


# Batching configuration
MAX_CONCURRENT_REQUESTS = 3
research_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


def perform_research(topic: str) -> str:
    """Run the research pipeline synchronously away from the event loop."""
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic:
        raise ValueError("Research topic cannot be empty")

    if not openrouter_client:
        raise ValueError("OpenRouter API key not configured")

    if not tavily_client:
        raise ValueError("Tavily API key not configured")

    print(f"Starting research for topic: {cleaned_topic}")

    # Generate research plan
    print("Generating research plan...")
    research_plan = openrouter_client.generate_research_plan(cleaned_topic)
    if not research_plan:
        raise RuntimeError("Failed to generate research plan")

    print(f"Research plan generated: {research_plan[:100]}...")

    # Conduct research using Tavily
    print("Conducting research with Tavily...")
    research_data = tavily_client.search(cleaned_topic, max_results=5)
    if not research_data:
        raise RuntimeError("Failed to gather research data")

    print(f"Research data gathered: {len(research_data)} characters")

    # Generate final report
    print("Generating final report...")
    report = openrouter_client.generate_report(cleaned_topic, research_data)
    if not report:
        raise RuntimeError("Failed to generate report")

    print("Research completed successfully")
    return report

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    return FileResponse("frontend/index.html")

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given topic"""
    try:
        async with research_semaphore:
            report = await asyncio.to_thread(perform_research, request.topic)

        return ResearchResponse(
            report=report,
            status="success",
            session_id="",
            queue_position=0
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Research error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
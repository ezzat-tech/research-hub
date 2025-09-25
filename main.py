from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Research Agent", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Request/Response models
class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str
    status: str

# API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENROUTER_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY and TAVILY_API_KEY in your .env file")

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Research Agent"
        }
    
    async def generate_research_plan(self, topic: str) -> List[str]:
        """Generate a research plan using deepseek-r1"""
        prompt = f"""
        Create a comprehensive research plan for the topic: "{topic}"
        
        Generate 5-7 specific research questions that would help create a thorough research report.
        Each question should be focused and specific to gather relevant information.
        
        Return only the research questions, one per line, without numbering or bullet points.
        """
        
        async with httpx.AsyncClient() as client:
            # Use free DeepSeek models optimized for research planning
            models_to_try = [
                "deepseek/deepseek-chat",
                "deepseek/deepseek-coder",
                "meta-llama/llama-3.1-8b-instruct",
                "microsoft/phi-3-medium-128k-instruct"
            ]
            
            response = None
            successful_model = None
            
            for model in models_to_try:
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }
                    )
                    
                    if response.status_code == 200:
                        print(f"Successfully used model: {model}")
                        successful_model = model
                        break
                    else:
                        print(f"Model {model} failed with status {response.status_code}")
                        continue
                        
                except Exception as e:
                    print(f"Model {model} failed with exception: {str(e)}")
                    continue
            
            if response is None or response.status_code != 200:
                error_msg = "All models failed to generate research plan"
                if response:
                    error_msg += f": {response.text}"
                raise HTTPException(status_code=500, detail=error_msg)
            
            result = response.json()
            plan_text = result["choices"][0]["message"]["content"]
            
            # Parse research questions
            questions = [q.strip() for q in plan_text.split('\n') if q.strip()]
            return questions

    async def generate_report(self, topic: str, research_data: List[Dict[str, Any]]) -> str:
        """Generate final research report using deepseek-r1"""
        
        # Format research data
        research_context = "\n\n".join([
            f"Source: {item.get('title', 'Unknown')}\nURL: {item.get('url', 'N/A')}\nContent: {item.get('content', '')[:500]}..."
            for item in research_data
        ])
        
        prompt = f"""
        Create a comprehensive research report on the topic: "{topic}"
        
        Use the following research data to create a well-structured report:
        
        {research_context}
        
        Structure the report with the following sections:
        1. Executive Summary (2-3 paragraphs)
        2. Introduction (background and context)
        3. Key Findings (main findings, organized by themes)
        4. Conclusion (key takeaways and implications)
        5. Thesis (main argument or position)
        
        IMPORTANT FORMATTING RULES:
        - Each section should start with a clear heading on its own line
        - Use "Executive Summary", "Introduction", "Key Findings", "Conclusion", "Thesis" as exact headings
        - Do NOT use "Body:" prefix - just use "Key Findings" as the heading
        - Each heading should be on a separate line from the content
        - Make the report informative, well-organized, and professional
        """
        
        async with httpx.AsyncClient() as client:
            # Use free DeepSeek models optimized for research planning
            models_to_try = [
                "deepseek/deepseek-chat",
                "deepseek/deepseek-coder",
                "meta-llama/llama-3.1-8b-instruct",
                "microsoft/phi-3-medium-128k-instruct"
            ]
            
            response = None
            successful_model = None
            
            for model in models_to_try:
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 4000
                        }
                    )
                    
                    if response.status_code == 200:
                        print(f"Successfully used model for report: {model}")
                        successful_model = model
                        break
                    else:
                        print(f"Model {model} failed with status {response.status_code}")
                        continue
                        
                except Exception as e:
                    print(f"Model {model} failed with exception: {str(e)}")
                    continue
            
            if response is None or response.status_code != 200:
                error_msg = "All models failed to generate report"
                if response:
                    error_msg += f": {response.text}"
                raise HTTPException(status_code=500, detail=error_msg)
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for information using Tavily API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": True,
                    "max_results": max_results
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Tavily API error: {response.text}")
            
            result = response.json()
            return result.get("results", [])

# Initialize clients
openrouter_client = OpenRouterClient(OPENROUTER_API_KEY)
tavily_client = TavilyClient(TAVILY_API_KEY)

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    return FileResponse("frontend/index.html")

@app.get("/test-formatting")
async def serve_test_formatting():
    """Serve the formatting test page"""
    return FileResponse("frontend/test_formatting.html")

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given topic"""
    try:
        print(f"Starting research for topic: {request.topic}")
        
        # Validate API keys
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
            raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
        
        if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
            raise HTTPException(status_code=500, detail="Tavily API key not configured")
        
        # Step 1: Generate research plan
        print("Step 1: Generating research plan...")
        research_questions = await openrouter_client.generate_research_plan(request.topic)
        print(f"Generated {len(research_questions)} research questions")
        
        if not research_questions:
            raise HTTPException(status_code=500, detail="Failed to generate research questions")
        
        # Step 2: Search for information using Tavily
        print("Step 2: Searching for information...")
        all_research_data = []
        for i, question in enumerate(research_questions):
            print(f"Searching question {i+1}/{len(research_questions)}: {question[:50]}...")
            try:
                search_results = await tavily_client.search(question, max_results=3)
                all_research_data.extend(search_results)
                print(f"Found {len(search_results)} results")
            except Exception as e:
                print(f"Search failed for question {i+1}: {str(e)}")
                # Continue with other questions even if one fails
                continue
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        print(f"Total research data collected: {len(all_research_data)} items")
        
        if not all_research_data:
            raise HTTPException(status_code=500, detail="No research data collected from searches")
        
        # Step 3: Generate final report
        print("Step 3: Generating final report...")
        report = await openrouter_client.generate_report(request.topic, all_research_data)
        print("Report generated successfully!")
        
        if not report or len(report.strip()) < 100:
            raise HTTPException(status_code=500, detail="Generated report is too short or empty")
        
        return ResearchResponse(report=report, status="success")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Research failed with error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

# PDF generation is now handled client-side for better performance

# PDF generation functions removed - now handled client-side

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Research Agent is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

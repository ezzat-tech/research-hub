from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import requests
import asyncio
import re
from datetime import datetime, timedelta
from collections import deque
import uuid

# Try to load environment variables, but don't fail if .env file has issues
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Make sure to set environment variables manually or fix the .env file")

# Rate limiting and queuing system
MAX_CONCURRENT_REQUESTS = 3
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_TIMEOUT = 300  # 5 minutes

# Global state management
active_requests = 0
request_queue = deque()
request_history = {}  # Store request results by session_id
rate_limit_tracker = deque()  # Track requests per minute

class RequestSession:
    def __init__(self, session_id: str, topic: str):
        self.session_id = session_id
        self.topic = topic
        self.created_at = datetime.now()
        self.status = "queued"
        self.result = None
        self.error = None

def check_rate_limit():
    """Check if user has exceeded rate limit"""
    now = datetime.now()
    
    # Remove old entries (older than 1 minute)
    while rate_limit_tracker and rate_limit_tracker[0] < now - timedelta(minutes=1):
        rate_limit_tracker.popleft()
    
    # Check if under limit
    if len(rate_limit_tracker) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add current request
    rate_limit_tracker.append(now)
    return True

def cleanup_old_sessions():
    """Remove sessions older than 1 hour"""
    cutoff = datetime.now() - timedelta(hours=1)
    to_remove = []
    
    for session_id, session in request_history.items():
        if session.created_at < cutoff:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del request_history[session_id]

async def process_queue():
    """Process the request queue"""
    global active_requests
    
    while request_queue and active_requests < MAX_CONCURRENT_REQUESTS:
        session = request_queue.popleft()
        active_requests += 1
        session.status = "processing"
        
        try:
            # Process the research request
            result = await conduct_research_internal(session.topic)
            session.result = result
            session.status = "completed"
        except Exception as e:
            session.error = str(e)
            session.status = "failed"
        finally:
            active_requests -= 1
            # Continue processing queue if there are more items
            if request_queue:
                asyncio.create_task(process_queue())

# API configuration - with better error handling
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
    print("ERROR: OPENROUTER_API_KEY not set or still has placeholder value")
    print("Please set your OpenRouter API key in the .env file or as an environment variable")
    print("Get your API key from: https://openrouter.ai/")
    # Don't exit, just warn - let the user fix it

if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
    print("ERROR: TAVILY_API_KEY not set or still has placeholder value")
    print("Please set your Tavily API key in the .env file or as an environment variable")
    print("Get your API key from: https://tavily.com/")
    # Don't exit, just warn - let the user fix it

# Initialize FastAPI app
app = FastAPI(title="Research Hub API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the main HTML file
@app.get("/")
async def read_root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Serve test formatting page
@app.get("/test-formatting")
async def test_formatting():
    with open("frontend/test_formatting.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Pydantic models
class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str
    status: str
    session_id: str = None
    queue_position: int = None

class QueueStatusResponse(BaseModel):
    status: str
    queue_position: int = None
    estimated_wait_time: int = None
    result: str = None
    error: str = None

# OpenRouter client
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
        
        # Use only confirmed FREE models from OpenRouter
        models = [
            "openrouter/auto",  # Automatically selects the best free model
            "meta-llama/llama-3-8b-instruct",  # Meta's free model
            "mistralai/mistral-7b-instruct",  # Mistral's free model
            "openchat/openchat-3.5-0106",  # OpenChat free model
            "nousresearch/nous-capybara-7b"  # Nous Research free model
        ]
        
        response = None
        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"Successfully used model: {model}")
                    break
                else:
                    print(f"Model {model} failed with status {response.status_code}")
                    if response.status_code == 401:
                        print("Authentication error - check your API key")
                    elif response.status_code == 402:
                        print("Payment required - this model is not free")
                    
            except Exception as e:
                print(f"Error with model {model}: {str(e)}")
                continue
        
        if response is None or response.status_code != 200:
            raise Exception("All models failed to generate research plan")
        
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
        
        # Use only confirmed FREE models from OpenRouter
        models = [
            "openrouter/auto",  # Automatically selects the best free model
            "meta-llama/llama-3-8b-instruct",  # Meta's free model
            "mistralai/mistral-7b-instruct",  # Mistral's free model
            "openchat/openchat-3.5-0106",  # OpenChat free model
            "nousresearch/nous-capybara-7b"  # Nous Research free model
        ]
        
        response = None
        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    print(f"Successfully used model: {model}")
                    break
                else:
                    print(f"Model {model} failed with status {response.status_code}")
                    if response.status_code == 401:
                        print("Authentication error - check your API key")
                    elif response.status_code == 402:
                        print("Payment required - this model is not free")
                    
            except Exception as e:
                print(f"Error with model {model}: {str(e)}")
                continue
        
        if response is None or response.status_code != 200:
            raise Exception("All models failed to generate report")
        
        return response.json()["choices"][0]["message"]["content"]

# Tavily client
class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"

    def search(self, query: str, max_results: int = 5) -> str:
        """Search for information using Tavily API"""
        try:
            response = requests.post(
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

async def conduct_research_internal(topic: str) -> str:
    """Internal research function that does the actual work"""
    if not openrouter_client:
        raise Exception("OpenRouter API key not configured")
    if not tavily_client:
        raise Exception("Tavily API key not configured")
    
    try:
        # Step 1: Generate research plan
        print(f"Generating research plan for: {topic}")
        research_plan = openrouter_client.generate_research_plan(topic)
        
        if not research_plan or research_plan.strip() == "":
            raise Exception("Failed to generate research plan")
        
        # Step 2: Conduct web searches based on the plan
        print(f"Conducting web searches for: {topic}")
        search_queries = [
            f"{topic} overview",
            f"{topic} key findings",
            f"{topic} recent developments",
            f"{topic} expert opinions"
        ]
        
        all_search_results = []
        for query in search_queries:
            try:
                results = tavily_client.search(query, max_results=3)
                if results and results.strip():
                    all_search_results.append(f"Search Query: {query}\n{results}\n")
            except Exception as e:
                print(f"Search failed for query '{query}': {str(e)}")
                continue
        
        if not all_search_results:
            raise Exception("No search results found")
        
        research_data = "\n".join(all_search_results)
        
        # Step 3: Generate comprehensive report
        print(f"Generating report for: {topic}")
        report = openrouter_client.generate_report(topic, research_data)
        
        if not report or report.strip() == "":
            raise Exception("Failed to generate report")
        
        return report
        
    except Exception as e:
        print(f"Research failed: {str(e)}")
        raise Exception(f"Research failed: {str(e)}")

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given topic with queuing and rate limiting"""
    global active_requests  # This line fixes the error
    
    try:
        # Clean up old sessions
        cleanup_old_sessions()
        
        # Check rate limit
        if not check_rate_limit():
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before making another request.")
        
        # Create session
        session_id = str(uuid.uuid4())
        session = RequestSession(session_id, request.topic)
        request_history[session_id] = session
        
        # Check if we can process immediately
        if active_requests < MAX_CONCURRENT_REQUESTS and not request_queue:
            # Process immediately
            session.status = "processing"
            active_requests += 1
            
            try:
                result = await conduct_research_internal(request.topic)
                session.result = result
                session.status = "completed"
                return ResearchResponse(
                    report=result, 
                    status="success",
                    session_id=session_id,
                    queue_position=0
                )
            except Exception as e:
                session.error = str(e)
                session.status = "failed"
                raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")
            finally:
                active_requests -= 1
        else:
            # Add to queue
            queue_position = len(request_queue) + 1
            request_queue.append(session)
            
            # Start processing queue if not already running
            if active_requests == 0:
                asyncio.create_task(process_queue())
            
            return ResearchResponse(
                report="", 
                status="queued",
                session_id=session_id,
                queue_position=queue_position
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in research endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/queue-status/{session_id}", response_model=QueueStatusResponse)
async def get_queue_status(session_id: str):
    """Get the status of a specific research request"""
    if session_id not in request_history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = request_history[session_id]
    
    # Calculate estimated wait time
    estimated_wait_time = 0
    if session.status == "queued":
        queue_position = list(request_queue).index(session) + 1 if session in request_queue else 0
        estimated_wait_time = queue_position * 60  # Assume 1 minute per request
    
    return QueueStatusResponse(
        status=session.status,
        queue_position=estimated_wait_time // 60 if estimated_wait_time > 0 else 0,
        estimated_wait_time=estimated_wait_time,
        result=session.result,
        error=session.error
    )

@app.get("/api/queue-info")
async def get_queue_info():
    """Get general queue information"""
    return {
        "active_requests": active_requests,
        "queue_length": len(request_queue),
        "max_concurrent": MAX_CONCURRENT_REQUESTS,
        "max_per_minute": MAX_REQUESTS_PER_MINUTE
    }

def format_markdown_text(text: str) -> str:
    """Convert markdown formatting to HTML"""
    if not text:
        return ""
    
    # Convert bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert italic text
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert bullet points
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if stripped:
                formatted_lines.append(f'<p>{stripped}</p>')
    
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
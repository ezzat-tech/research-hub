# Research Hub

A full-stack research platform that generates comprehensive research reports using free DeepSeek models (via OpenRouter) and Tavily Search APIs.

## Features

- **Modern Web Interface**: Clean, responsive HTML/CSS/JavaScript frontend
- **AI-Powered Research**: Uses free DeepSeek models for intelligent research planning and report generation
- **Real-time Web Search**: Integrates Tavily API for up-to-date information gathering
- **Structured Reports**: Generates reports with Executive Summary, Introduction, Body, Conclusion, and Thesis
- **Async Support**: FastAPI backend with async/await for optimal performance
- **Error Handling**: Comprehensive error handling and user feedback

## Project Structure

```
research_agent/
├── main.py              # FastAPI server
├── frontend/
│   ├── index.html       # Main web interface
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
├── .env                 # Environment variables (API keys)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd research_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   - Copy `.env` template and add your API keys:
   ```bash
   # Get your OpenRouter API key from: https://openrouter.ai/
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # Get your Tavily API key from: https://tavily.com/
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Run the application**
   ```bash
   python start.py
   ```
   
   Or alternatively:
   ```bash
   python main.py
   ```

5. **Open your browser**
   The application will be available at `http://localhost:8001`

## API Keys Required

- **OpenRouter API Key**: Get from [https://openrouter.ai/](https://openrouter.ai/)
  - Used to access free DeepSeek models for research planning and report generation
- **Tavily API Key**: Get from [https://tavily.com/](https://tavily.com/)
  - Used for real-time web search and information gathering

## Technologies Used

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Models**: DeepSeek (via OpenRouter) - Free models only
- **Search**: Tavily Search API
- **Async**: asyncio for concurrent operations

## Usage

1. Enter your research topic in the input field
2. Click "Start Research" to begin the process
3. The system will:
   - Generate a research plan using AI
   - Search the web for relevant information
   - Generate a comprehensive report
4. View and download your research report

## Development

### Running in Development Mode

```bash
# Using the start script (recommended)
python start.py

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Project Structure Details

- `main.py`: FastAPI server with research endpoints
- `frontend/`: Static web files served by FastAPI
- `.env`: Environment variables for API keys
- `requirements.txt`: Python package dependencies

## Features in Detail

### Research Process

1. **Research Planning**: AI generates a comprehensive research plan
2. **Web Search**: Multiple targeted searches using Tavily API
3. **Report Generation**: AI creates structured, academic-quality reports
4. **Formatting**: Professional formatting with proper headings and sections

### Report Structure

- **Executive Summary**: Brief overview of key findings
- **Introduction**: Context and background information
- **Key Findings**: Main findings organized by themes
- **Conclusion**: Summary and implications
- **Thesis**: Main argument or position

### Error Handling

- Graceful handling of API failures
- User-friendly error messages
- Fallback mechanisms for model failures
- Comprehensive logging for debugging

## Troubleshooting

### Common Issues

1. **API Key Errors**: Make sure your API keys are correctly set in the `.env` file
2. **Port Already in Use**: The application uses port 8001 by default
3. **Model Failures**: The system automatically tries multiple free models

### Getting Help

If you encounter issues:
1. Check that your API keys are valid and active
2. Ensure all dependencies are installed
3. Check the console output for specific error messages

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
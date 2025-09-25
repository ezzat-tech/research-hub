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
│   ├── style.css        # Modern CSS styling
│   └── script.js        # Frontend JavaScript
├── requirements.txt     # Python dependencies
├── config_template.txt  # API keys template
└── README.md           # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

1. Copy `config_template.txt` to `.env`
2. Get your API keys:
   - **OpenRouter API Key**: Sign up at [openrouter.ai](https://openrouter.ai/)
   - **Tavily API Key**: Sign up at [tavily.com](https://tavily.com/)
3. Add your keys to the `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Usage

1. **Enter Research Topic**: Type your research topic in the input field
2. **Start Research**: Click "Start Research" or press Enter
3. **Wait for Processing**: The system will:
   - Generate a research plan using DeepSeek R1
   - Search for relevant information using Tavily
   - Generate a comprehensive report
4. **View Results**: The formatted report will be displayed with options to copy or download

## API Endpoints

- `GET /` - Serve the main web interface
- `POST /api/research` - Conduct research on a given topic
- `GET /api/health` - Health check endpoint

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenRouter**: Access to DeepSeek R1 model
- **Tavily**: Real-time web search API
- **httpx**: Async HTTP client
- **Pydantic**: Data validation

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: No frameworks, pure JS
- **Responsive Design**: Mobile-friendly interface

## Features in Detail

### Research Workflow
1. **Research Planning**: DeepSeek Chat generates 5-7 specific research questions
2. **Information Gathering**: Tavily searches for relevant information for each question
3. **Report Generation**: DeepSeek Chat synthesizes findings into a structured report

### Report Structure
- **Executive Summary**: 2-3 paragraph overview
- **Introduction**: Background and context
- **Body**: Main findings organized by themes
- **Conclusion**: Key takeaways and implications
- **Thesis**: Main argument or position

### User Interface
- **Modern Design**: Gradient backgrounds, smooth animations
- **Responsive**: Works on desktop, tablet, and mobile
- **Accessibility**: Keyboard shortcuts, focus management
- **Feedback**: Loading states, progress indicators, error handling

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for OpenRouter service | Yes |
| `TAVILY_API_KEY` | API key for Tavily search service | Yes |

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in the `.env` file
2. **Rate Limiting**: The app includes delays between API calls to avoid rate limits
3. **Network Issues**: Check your internet connection and API service status

### Error Messages

- **"Research Failed"**: Check API keys and network connection
- **"OpenRouter API error"**: Verify your OpenRouter API key and credits
- **"Tavily API error"**: Verify your Tavily API key and usage limits

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

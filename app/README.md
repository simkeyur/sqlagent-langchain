# Employee Database Query Application

This is a Flask-based web application that uses LangChain and Google's Gemini API to query an employee database using natural language.

## Features

- 🔍 Natural language query interface for employee database
- 🎨 Mobile-optimized responsive UI with minimal padding
- ⚙️ Settings panel for Gemini API key configuration
- 📊 LangChain SQL Agent for intelligent database queries
- 🚀 Fast and lightweight Flask backend

## Setup Instructions

### 1. Install Dependencies

```bash
cd app
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

### 4. Configure API Key

1. Click the ⚙️ settings button in the top-right corner
2. Enter your Google Gemini API key
3. Click Save

## Usage Examples

Try these natural language queries:

- "Show me all employees with Python skills"
- "List employees in the Engineering department"
- "Who are the managers?"
- "Find employees with Advanced or Expert SQL skills"
- "Show me all employees hired in the last year"
- "List employees assigned to the Mobile App Development project"
- "How many employees are in each department?"

## Project Structure

```
app/
├── app.py                 # Flask application and routes
├── sql_agent.py          # LangChain SQL agent configuration
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Frontend UI (HTML/CSS/JS)
└── static/              # Static assets (if needed)
```

## How It Works

1. **Frontend**: User enters a natural language query in the search bar
2. **Backend**: Flask receives the query and passes it to the LangChain SQL Agent
3. **LangChain**: The SQL agent uses Gemini to understand the query and generate SQL
4. **Database**: SQLite query is executed against the employee database
5. **Response**: Results are displayed in the UI

## API Endpoints

- `GET /` - Serves the main UI
- `POST /api/query` - Execute a natural language query
- `GET /api/settings` - Get current settings status
- `POST /api/settings` - Save API key
- `GET /api/health` - Health check endpoint

## Database Schema

The application queries an SQLite database with the following tables:

- `employees` - Employee information with manager relationships
- `departments` - Department listings
- `projects` - Project information
- `employee_projects` - Many-to-many employee-project assignments
- `skills` - Available skills
- `employee_skills` - Employee skill proficiency levels

## Security Notes

- API keys are stored locally in `settings.json`
- Passwords are never transmitted to the frontend
- In production, use secure environment variables and encrypted storage
- Add proper authentication and authorization

## Troubleshooting

### "API key not configured" error
Make sure to enter your Gemini API key in the settings panel.

### "Query execution failed"
- Check your internet connection
- Verify the API key is valid
- Try a simpler query

### "Database not found"
Make sure `employee_database.db` is in the parent directory of the app folder.

## Future Enhancements

- Add result pagination
- Export query results to CSV
- Query history
- Saved queries
- Multi-turn conversations
- Result filtering and sorting

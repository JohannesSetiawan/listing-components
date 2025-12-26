# Listing Helper

A simple Python Streamlit app with basic frontend and API functionality.

## Features

- 🎨 Interactive frontend built with Streamlit
- 🚀 Hello World API endpoint
- ☁️ Ready for Streamlit Cloud deployment

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and `app.py` as the main file
6. Click "Deploy"

## Project Structure

```
listing-helper/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Usage

### Home Page
- Welcome screen with app information
- Quick stats display
- Interactive input example

### API Test Page
- Test the Hello World API endpoint
- View JSON response
- See formatted metrics

## API Endpoint

The app includes a simulated API endpoint:

**Hello World API**
- Returns a JSON response with:
  - `message`: "Hello World!"
  - `timestamp`: Current timestamp
  - `status`: "success"

## License

MIT License

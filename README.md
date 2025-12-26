# DeployTrack Low-Code

**Centralized deployment manifest for complex low-code ecosystems**

A specialized management tool designed to document, categorize, and track components slated for deployment. It bridges the gap between development and operations by providing a single source of truth for **Visual Programming** assets, **Experience Manager** layouts, and **Data Manager** schemas.

## 🌟 Features

### Core Component Categories

#### 1. **Visual Programming (VP)**
Logic-heavy assets with custom types:
- API
- DJOB (Data Jobs)
- Function
- Workflow
- Integration

#### 2. **Experience Manager (EM)**
Frontend and UI assets:
- Single UI
- Multiple UI
- Dashboard
- Form
- Report

#### 3. **Data Manager (DM)**
Database schemas and data orchestration:
- Schema
- Table
- View
- Stored Procedure
- ETL Pipeline

### Key Functionality

✅ **Unified & Specialized List Views**
- Master List: Global view of all components
- Categorized Tabs: Dedicated pages for VP, EM, and DM
- Advanced Filtering: Search by type, name, or description
- Flexible Pagination: 10, 50, 100, or 1,000 items per page

✅ **Component Lifecycle Management**
- Detail View: Dedicated page for each component
- Change Tracking: Components flagged as "New" or "Updated"
- Audit Trail: Automated `created_at` and `updated_at` timestamps
- CRUD Operations: Create, Read, Update, Delete components

✅ **Data Schema**
- `uid`: Primary key (UUID)
- `component_id`: Unique identifier from low-code platform
- `name`: Human-readable title
- `url_link`: Direct link to component in editor
- `change_type`: New or Updated
- `description`: Deployment context
- `category`: VP, EM, or DM
- `type`: Specific component type
- `created_at` / `updated_at`: Timestamps

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone this repository

2. Create a `.env` file in the root directory:
```env
DB_URL=sqlite:///deploytrack.db
```

For other databases:
```env
# PostgreSQL
DB_URL=postgresql://user:password@localhost/dbname

# MySQL
DB_URL=mysql://user:password@localhost/dbname
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database with sample data (optional):
```bash
python init_db.py
```

### Running the App

```bash
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 Usage

### Workflow Example

1. **Entry**: Developer finishes a new API in Visual Programming
2. **Logging**: Navigate to VP List Page → Click "Add New" → Input details
3. **Review**: Release Manager filters Master List by "Updated" components
4. **Deployment**: Update description in Detail Page to reflect live status

### Features by Page

#### 🏠 Home
- Dashboard with component statistics
- Quick overview of all categories
- Recent component activity

#### 📊 Master List
- View all components across categories
- Filter by type, change type, or search
- Pagination controls
- Add new components

#### ⚙️ Visual Programming
- VP-specific components
- Filter by API, DJOB, Function, etc.
- Category-focused view

#### 🎨 Experience Manager
- EM-specific components
- Filter by UI types
- Frontend asset management

#### 💾 Data Manager
- DM-specific components
- Database and ETL pipeline tracking
- Schema management

## 🌐 Deployment on Streamlit Cloud

1. Ensure `.env` is in `.gitignore` (it already is)
2. Push your code to GitHub
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Sign in with GitHub
5. Click "New app"
6. Select repository, branch, and `app.py`
7. Add Secrets in Streamlit Cloud:
   - Go to App Settings → Secrets
   - Add: `DB_URL = "your_database_url"`
8. Click "Deploy"

**Note**: For Streamlit Cloud, use a cloud database (PostgreSQL on Heroku, Supabase, etc.) instead of SQLite.

## 📁 Project Structure

```
listing-helper/
├── app.py              # Main Streamlit application
├── database.py         # Database models and operations
├── init_db.py         # Database initialization script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── feat.md            # Feature documentation
└── README.md          # This file
```

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLAlchemy (SQLite/PostgreSQL/MySQL)
- **Data Processing**: Pandas
- **Environment**: python-dotenv

## 📝 API Endpoint

Test the Hello World API from the sidebar:
```json
{
  "message": "Hello World!",
  "timestamp": "2025-12-27 10:30:00",
  "status": "success",
  "total_components": 9
}
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

MIT License

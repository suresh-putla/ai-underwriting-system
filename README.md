# LOUS - Loan Origination & Underwriting System

**AI Automated Loan Origination Underwriting System**

A modern, AI-powered web application for processing home mortgage loans with automated underwriting capabilities.

## Features

- **Modern UI**: Professional design with glassmorphism effects, gradient accents, and smooth animations
- **User Authentication**: Secure login system with role-based access control
- **Real-time Dashboard**: Live loan portfolio overview with key metrics
- **AI-Powered**: Ready for AI/ML integration for automated underwriting
- **Single Container**: Easy deployment with Docker

## Tech Stack

### Frontend
- React.js 18
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Axios (API client)

### Backend
- Python 3.11
- FastAPI (web framework)
- SQLite (database)
- ChromaDB (vector database for RAG)
- python-dotenv (environment management)

## Project Structure

```
lous/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
├── backend/
│   ├── routers/
│   │   ├── health.py
│   │   └── auth.py
│   ├── db/
│   │   └── database.py
│   ├── agents/
│   ├── tools/
│   ├── rag/
│   ├── core/
│   ├── main.py
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites
- Docker and Docker Compose (for containerized deployment)
- OR Node.js 20+ and Python 3.11+ (for local development)

### Quick Start with Docker

1. **Build and run the container:**
   ```bash
   cd lous
   docker-compose up --build
   ```

2. **Access the application:**
   - Open browser to `http://localhost:8000`
   - The backend API will serve the frontend

### Local Development

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd lous/backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend:**
   ```bash
   python main.py
   ```
   Backend runs on `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd lous/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

## Default Login Credentials

The system comes with pre-configured test users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| loan_officer | officer123 | Loan Officer |
| underwriter | under123 | Underwriter |

**Note:** Change these credentials in production!

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /api/health` - Health check endpoint
- `POST /api/user-auth` - User authentication

## Design Features

The application features a modern, professional design inspired by contemporary fintech applications:

- **Dark theme** with vibrant cyan/purple gradient accents
- **Glassmorphism** UI elements with backdrop blur effects
- **Smooth animations** on scroll and hover
- **Responsive layout** for mobile and desktop
- **Professional typography** with clear hierarchy
- **Modern card designs** with floating effects

## Development Roadmap

- [ ] Loan application submission workflow
- [ ] Document upload and management
- [ ] AI-powered underwriting engine
- [ ] Risk assessment dashboard
- [ ] Compliance checking automation
- [ ] Report generation
- [ ] Integration with credit bureaus
- [ ] Email notifications
- [ ] Advanced analytics

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.

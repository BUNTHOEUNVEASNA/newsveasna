# News Scraper - Production-Ready Django Application

A complete full-stack news aggregation platform with Django backend, React frontend, and real-time updates. Features web scraping, distributed processing, REST API, WebSocket connections, and comprehensive analytics.

## 🚀 Features
### 🎯 Core Features
- **Full-Stack Application**: Django backend + React frontend with TypeScript
- **Real-Time Updates**: WebSocket connections for live news feeds
- **Web Scraping**: Intelligent scrapers for BBC News, CNN, and other sources
- **Distributed Processing**: Hash-based node selection for scalable scraping
- **REST API**: Comprehensive API with filtering, pagination, and search
- **Analytics Dashboard**: Interactive charts and statistics
- **Responsive Design**: Modern UI with Tailwind CSS
- **Real-Time Monitoring**: System health checks and performance metrics

### 🔧 Technical Stack
- **Backend**: Django 4.2, Django REST Framework, Celery, Redis
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-Time**: Django Channels, WebSockets
- **Monitoring**: Flower, Health checks, Analytics
- **Deployment**: Docker, Docker Compose

## 📋 Requirements

- **Python 3.11+**
- **Node.js 18+** and npm
- **Redis 6+**
- **PostgreSQL 13+** (optional, SQLite for development)
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
# Make setup script executable and run
chmod +x start_project.sh
./start_project.sh
```

### Option 2: Manual Setup
See [MANUAL_SETUP.md](MANUAL_SETUP.md) for detailed step-by-step instructions.

### Option 3: Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 🌐 Running the Application

You need to run multiple services. Open **5 terminal windows**:

**Terminal 1 - Django Server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A news_scraper worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
source venv/bin/activate
celery -A news_scraper beat --loglevel=info
```

**Terminal 4 - Flower (Optional):**
```bash
source venv/bin/activate
celery -A news_scraper flower
```

**Terminal 5 - React Frontend:**
```bash
cd frontend
npm start
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main React application |
| **Backend API** | http://localhost:8000/api/ | REST API endpoints |
| **Admin Panel** | http://localhost:8000/admin/ | Django admin interface |
| **API Documentation** | http://localhost:8000/api/docs/ | Swagger UI |
| **ReDoc** | http://localhost:8000/api/redoc/ | Alternative API docs |
| **Flower** | http://localhost:5555 | Celery task monitoring |

## 🎨 Frontend Features

### 📱 Pages and Components
- **News Feed**: Paginated article listing with advanced filtering
- **Real-Time**: Live updates via WebSocket with connection status
- **Analytics**: Interactive charts and statistics dashboard
- **Settings**: System health monitoring and configuration

### 🎯 Key Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-Time Updates**: Live news feed with WebSocket connections
- **Advanced Filtering**: Search, source filtering, date ranges
- **Interactive Charts**: Bar charts, pie charts, timeline graphs
- **Status Indicators**: Connection status, system health
- **Modern UI**: Tailwind CSS with smooth animations

## 🔧 Backend Features

### 🗄️ Database Schema
- **Article Model**: Title, summary, URL, source, timestamps
- **Constraints**: Unique together (URL, source) for deduplication
- **Indexes**: Optimized for source, date, and search queries

### 🕷️ Web Scraping
- **Multiple Sources**: BBC News, CNN News (easily extensible)
- **Intelligent Parsing**: Robust HTML parsing with fallbacks
- **Error Handling**: Retry logic, exponential backoff
- **Mock Data**: Generates realistic data when scraping fails

### ⚡ Real-Time Features
- **WebSocket Support**: Django Channels for real-time updates
- **Live Notifications**: Instant updates when new articles arrive
- **Connection Management**: Auto-reconnection, status monitoring

### 🔄 Background Processing
- **Celery Integration**: Asynchronous task processing
- **Scheduled Tasks**: Automatic scraping every 10 minutes
- **Distributed Logic**: Hash-based node selection
- **Monitoring**: Flower for task monitoring

## 📚 API Documentation

### 🔗 Main Endpoints

```bash
# List all articles
curl http://localhost:8000/api/articles/

# Filter by source
curl http://localhost:8000/api/articles/?source=inshorts

# Filter by date range
curl "http://localhost:8000/api/articles/?date_from=2024-01-01&date_to=2024-12-31"

# Search articles
curl http://localhost:8000/api/articles/?search=technology

# Get statistics
curl http://localhost:8000/api/articles/stats/

# Trigger manual scraping
curl -X POST http://localhost:8000/api/articles/scrape/

# Health check
curl http://localhost:8000/api/articles/health/
```

### 📖 Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Postman Collection**: Import `postman_collection.json`

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test aggregator.tests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📊 Monitoring

### Admin Interface

Access the Django admin at http://localhost:8000/admin/ to view and manage articles.

### Flower (Celery Monitoring)

Access Flower at `http://localhost:5555/` to monitor Celery tasks and workers.

### Health Check

The application provides a health check endpoint at `/api/articles/health/` that verifies:
- Database connectivity
- Cache connectivity
- Recent scraping activity

### Real-Time Monitoring

The frontend provides real-time monitoring:
- **Connection Status**: WebSocket connection indicator
- **Live Updates**: Real-time article count and updates
- **System Health**: Database and cache status

## 🏗️ Architecture

### Project Structure

```
news_scraper/
├── news_scraper/          # Django project settings
├── aggregator/           # Main Django application
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── celery.py         # Celery configuration
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── aggregator/           # Main application
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── scrapers.py       # Web scrapers
│   ├── tasks.py          # Celery tasks
│   ├── admin.py          # Django admin
│   ├── urls.py           # App URLs
│   └── tests.py          # Test suite
├── frontend/             # React application
│   ├── public/           # Static files
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API and WebSocket services
│   │   ├── types/        # TypeScript type definitions
│   │   └── App.tsx       # Main App component
│   ├── package.json      # Node dependencies
│   └── tailwind.config.js # Tailwind configuration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── start_project.sh     # Automated setup script
├── MANUAL_SETUP.md      # Detailed setup instructions
└── README.md           # This file
```

### Technology Stack
```
└── README.md           # This file
```

### Database Schema

**Article Model**:
- `id`: Primary key
- `title`: Article title (max 500 chars)
- `summary`: Article summary/description
- `url`: Original article URL (max 1000 chars)
- `source`: News source name (max 100 chars)
- `published_at`: Publication timestamp
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

**Constraints**:
- Unique together: `(url, source)` - Prevents duplicates
- Indexes on: `source`, `published_at`, `created_at`, `(source, published_at)`

### Distributed Scraping Logic

### Frontend Architecture
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Recharts**: Interactive charts and graphs
- **Axios**: HTTP client for API calls
- **WebSocket Service**: Real-time communication

The application simulates distributed scraping using hash-based node selection:

```python
def get_scraper_node(source: str) -> str:
    node_id = hash(source) % 2
    return f"node_{node_id}"
```

This ensures consistent assignment of sources to nodes while distributing the load.

### Real-Time Architecture
- **Django Channels**: WebSocket support for Django
- **Redis Channel Layer**: Message passing between processes
- **WebSocket Consumers**: Handle real-time connections
- **Auto-Reconnection**: Robust connection management

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set appropriate production values in `.env`
2. **Database**: Use PostgreSQL in production
3. **Static Files**: Configure proper static file serving
4. **Frontend Build**: `npm run build` for production build
5. **Security**: Update `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`
5. **Monitoring**: Set up proper logging and monitoring
6. **Scaling**: Use multiple Celery workers for high load

### Docker Deployment

```bash
# Production build
docker-compose -f docker-compose.yml up -d

# Scale Celery workers
docker-compose up --scale celery=3

# Build frontend for production
cd frontend
npm run build
cd ..
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality (both backend and frontend)
5. Update documentation if needed
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 📋 Manual Setup Checklist

For detailed manual setup instructions, see [MANUAL_SETUP.md](MANUAL_SETUP.md).

Quick checklist:
- [ ] Python virtual environment activated
- [ ] Redis server running
- [ ] All Python dependencies installed
- [ ] Database migrations applied
- [ ] Django server running (port 8000)
- [ ] Celery worker and beat running
- [ ] Frontend dependencies installed
- [ ] React server running (port 3000)
- [ ] All services accessible

## 🆘 Support

For support and questions:
- Check [MANUAL_SETUP.md](MANUAL_SETUP.md) for detailed instructions
- Review the documentation
- Review the test suite for examples
- Open an issue on GitHub
- Check logs for error details

## 🔄 Changelog

### v2.0.0 (Current)
- **Full-Stack Application**: Complete React frontend + Django backend
- **Real-Time Features**: WebSocket connections and live updates
- **Modern UI**: Responsive design with Tailwind CSS
- **Enhanced Scraping**: BBC News, CNN News scrapers
- **Analytics Dashboard**: Interactive charts and statistics
- **Improved Monitoring**: System health checks and status indicators
- **Better Documentation**: Comprehensive setup guides
- **Production Ready**: Docker support, automated setup scripts

### v1.0.0
- Initial Django backend implementation
- Basic web scraping functionality
- REST API with Django REST Framework
- Celery integration for background tasks
- Basic test suite and documentation
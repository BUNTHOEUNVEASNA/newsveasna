# Manual Setup Instructions for News Scraper

This document provides step-by-step instructions to manually set up and run the complete News Scraper application.

## 🔧 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+** and npm
- **Redis 6+**
- **PostgreSQL 13+** (optional, SQLite is used by default)
- **Git**

## 📦 1. Project Setup

### Clone and Navigate
```bash
# If cloning from repository
git clone <repository-url>
cd news_scraper

# Or if already in project directory
pwd  # Should show news_scraper directory
```

### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## 🐍 2. Backend Setup (Django)

### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required .env variables:**
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_POSTGRES=False  # Set to True if using PostgreSQL
REDIS_URL=redis://localhost:6379/0
```

### Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin user
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## 🎨 3. Frontend Setup (React)

### Navigate to Frontend Directory
```bash
cd frontend
```

### Install Node Dependencies
```bash
npm install
```

### Configure Environment
```bash
# Create .env file in frontend directory
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
echo "REACT_APP_WS_URL=ws://localhost:8000/ws/news/" >> .env
```

### Build Tailwind CSS
```bash
# Tailwind should be automatically configured
# Verify by checking if tailwind.config.js exists
ls tailwind.config.js
```

### Return to Root Directory
```bash
cd ..
```

## 🔴 4. Redis Setup

### Install Redis (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
```

**macOS (with Homebrew):**
```bash
brew install redis
```

**Windows:**
Download from https://redis.io/download

### Start Redis Server
```bash
# Start Redis server
redis-server

# Or run in background
redis-server --daemonize yes

# Test Redis connection
redis-cli ping
# Should return: PONG
```

## 🗄️ 5. PostgreSQL Setup (Optional)

If you want to use PostgreSQL instead of SQLite:

### Install PostgreSQL
**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

### Create Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE news_scraper;
CREATE USER news_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE news_scraper TO news_user;
\q
```

### Update .env File
```env
USE_POSTGRES=True
DB_NAME=news_scraper
DB_USER=news_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Run Migrations Again
```bash
python manage.py migrate
```

## 🚀 6. Running the Application

You need to run multiple services. Open **5 separate terminal windows/tabs**:

### Terminal 1: Django Development Server
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Start Django server
python manage.py runserver
```
**Access:** http://localhost:8000

### Terminal 2: Celery Worker
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Start Celery worker
celery -A news_scraper worker --loglevel=info
```

### Terminal 3: Celery Beat Scheduler
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Start Celery beat
celery -A news_scraper beat --loglevel=info
```

### Terminal 4: Flower (Celery Monitoring)
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Start Flower
celery -A news_scraper flower
```
**Access:** http://localhost:5555

### Terminal 5: React Frontend
```bash
# Navigate to frontend directory
cd frontend

# Start React development server
npm start
```
**Access:** http://localhost:3000

## 🌐 7. Access Points

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main React application |
| **Backend API** | http://localhost:8000/api/ | REST API endpoints |
| **Admin Panel** | http://localhost:8000/admin/ | Django admin interface |
| **API Documentation** | http://localhost:8000/api/docs/ | Swagger UI |
| **ReDoc** | http://localhost:8000/api/redoc/ | Alternative API docs |
| **Flower** | http://localhost:5555 | Celery task monitoring |

## 🧪 8. Testing the Application

### Test Backend API
```bash
# Test articles endpoint
curl http://localhost:8000/api/articles/

# Test health check
curl http://localhost:8000/api/articles/health/

# Trigger manual scraping
curl -X POST http://localhost:8000/api/articles/scrape/
```

### Test Frontend
1. Open http://localhost:3000
2. Navigate through different pages
3. Check real-time updates
4. Verify WebSocket connection

### Run Tests
```bash
# Run Django tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔧 9. Troubleshooting

### Common Issues

**1. Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
redis-server
```

**2. Database Migration Issues**
```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial

# Or delete db.sqlite3 and run migrations again
rm db.sqlite3
python manage.py migrate
```

**3. Frontend Build Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**4. Celery Worker Not Starting**
```bash
# Check Redis connection
redis-cli ping

# Restart Celery with verbose logging
celery -A news_scraper worker --loglevel=debug
```

**5. WebSocket Connection Issues**
```bash
# Check if Django Channels is properly configured
python manage.py shell -c "
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
print('Channel layer:', channel_layer)
"
```

### Log Files
Check log files for detailed error information:
```bash
# Django logs
tail -f logs/news_scraper.log

# Celery logs (if configured)
tail -f logs/celery.log
```

## 🔄 10. Development Workflow

### Making Changes

**Backend Changes:**
1. Modify Python files
2. Django auto-reloads (no restart needed)
3. For model changes: `python manage.py makemigrations && python manage.py migrate`

**Frontend Changes:**
1. Modify React files
2. Hot reload automatically updates browser
3. For new dependencies: `npm install <package>`

**Database Changes:**
```bash
# Create new migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# View migration SQL
python manage.py sqlmigrate aggregator 0001
```

### Adding New Scrapers
1. Add scraper class to `aggregator/scrapers.py`
2. Register in `SCRAPERS` dictionary
3. Update frontend source filters
4. Test with manual scraping

## 📊 11. Monitoring and Maintenance

### Check System Health
```bash
# API health check
curl http://localhost:8000/api/articles/health/

# Database status
python manage.py dbshell

# Redis status
redis-cli info
```

### View Logs
```bash
# Django logs
tail -f logs/news_scraper.log

# Celery worker logs
# Check terminal where worker is running
```

### Database Maintenance
```bash
# Clean old articles (older than 30 days)
python manage.py shell -c "
from aggregator.tasks import cleanup_old_articles
cleanup_old_articles.delay(30)
"
```

## 🐳 12. Docker Alternative (Optional)

If you prefer using Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📝 13. Production Deployment

For production deployment:

1. Set `DEBUG=False` in .env
2. Configure proper `SECRET_KEY`
3. Set up proper database (PostgreSQL)
4. Configure web server (Nginx + Gunicorn)
5. Set up SSL certificates
6. Configure monitoring and logging
7. Set up backup procedures

## 🆘 14. Getting Help

If you encounter issues:

1. Check this manual setup guide
2. Review error logs
3. Check Django and Celery documentation
4. Verify all services are running
5. Test individual components

## ✅ 15. Verification Checklist

- [ ] Python virtual environment activated
- [ ] All Python dependencies installed
- [ ] Database migrations applied
- [ ] Redis server running
- [ ] Django server running (port 8000)
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Frontend dependencies installed
- [ ] React server running (port 3000)
- [ ] Can access frontend at http://localhost:3000
- [ ] Can access API at http://localhost:8000/api/
- [ ] WebSocket connection working
- [ ] Manual scraping works
- [ ] Real-time updates working

Once all items are checked, your News Scraper application should be fully operational!
#!/bin/bash

# News Scraper Project Startup Script

echo "🚀 Starting News Scraper Application..."

# Install Python dependencies
echo "📥 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Run Django migrations
echo "🗄️ Running database migrations..."
python3 manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser (if needed)..."
python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "1. Start Django: python3 manage.py runserver"
echo "2. Start Celery Worker: python3 -m celery -A news_scraper worker --loglevel=info"
echo "3. Start Celery Beat: python3 -m celery -A news_scraper beat --loglevel=info"
echo "4. Start Frontend: cd frontend && npm start"
echo ""
echo "🌐 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000/api/"
echo "- Admin Panel: http://localhost:8000/admin/"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- Flower (Celery): http://localhost:5555"
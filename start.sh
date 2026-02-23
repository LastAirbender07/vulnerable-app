#!/bin/bash

echo "🚨 Starting Vulnerable Blog Application..."
echo "⚠️  WARNING: For security testing only!"
echo ""

cd "$(dirname "$0")"

# Start services
docker-compose up --build -d

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access Points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "🔑 Test Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"

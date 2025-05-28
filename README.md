# Image Moderation API

A FastAPI-based image moderation service with MongoDB backend and React frontend.

## Features

- **Image Content Moderation**: Analyze uploaded images for harmful content across 8 categories
- **Token-based Authentication**: Secure API access with admin and user roles
- **MongoDB Integration**: Persistent storage for tokens and usage analytics
- **Docker Containerization**: Easy deployment with Docker Compose
- **React Frontend**: Modern web interface for interacting with the API
- **Comprehensive Testing**: Unit tests for authentication and core functionality

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. **Clone and navigate to the project:**

   ```bash
   git clone https://github.com/saif2012004/image-moderation-for-nudity-and-drugs-detection
   cd image-moderation-api
   ```

2. **Create environment file:**

   ```bash
   cp env.example .env
   ```

3. **Start the application:**

   ```bash
   docker-compose up --build -d
   ```

4. **Access the services:**
   - API Documentation: http://localhost:7000/docs
   - Frontend Application: http://localhost:3000
   - MongoDB: localhost:27017

## API Documentation

### Authentication

All endpoints except `/health` require Bearer token authentication.

#### Admin Endpoints

**Create Token**

```
POST /auth/tokens
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "isAdmin": false
}
```

**Get All Tokens**

```
GET /auth/tokens
Authorization: Bearer <admin_token>
```

**Delete Token**

```
DELETE /auth/tokens/{token_value}
Authorization: Bearer <admin_token>
```

#### Moderation Endpoint

**Moderate Image**

```
POST /moderate
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
```

Response:

```json
{
  "filename": "example.jpg",
  "safe": true,
  "categories": [
    {
      "category": "nudity",
      "confidence": 0.05,
      "flagged": false
    },
    {
      "category": "drugs",
      "confidence": 0.12,
      "flagged": false
    },
    {
      "category": "weapons",
      "confidence": 0.08,
      "flagged": false
    },
    {
      "category": "hate_symbols",
      "confidence": 0.03,
      "flagged": false
    }
  ],
  "overall_confidence": 0.07,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Health Check

**Health Status**

```
GET /health
```

## 🎯 **Detection Categories**

This system detects **2 categories** of inappropriate content:

1. **nudity**: Nudity and sexual content using AI-powered NudeNet detection
2. **drugs**: Drug-related content using advanced computer vision algorithms

## 📊 **API Response Example**

```json
{
  "filename": "test_image.jpg",
  "safe": false,
  "overall_confidence": 0.75,
  "categories": [
    {
      "category": "nudity",
      "confidence": 0.95,
      "flagged": true
    },
    {
      "category": "drugs",
      "confidence": 0.12,
      "flagged": false
    }
  ],
  "timestamp": "2024-01-20T10:30:45.123456Z"
}
```

## Development

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Local Development (without Docker)

1. **Start MongoDB:**

   ```bash
   docker run -d -p 27017:27017 --name mongo mongo:7.0
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API:**

   ```bash
   uvicorn app.main:app --reload --port 7000
   ```

4. **Run the frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Environment Variables

| Variable              | Description               | Default                     |
| --------------------- | ------------------------- | --------------------------- |
| `MONGODB_URI`         | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME`             | Database name             | `image_moderation`          |
| `API_HOST`            | API host                  | `0.0.0.0`                   |
| `API_PORT`            | API port                  | `7000`                      |
| `MONGO_ROOT_USERNAME` | MongoDB root username     | `admin`                     |
| `MONGO_ROOT_PASSWORD` | MongoDB root password     | `password123`               |

## Initial Setup

When the application starts for the first time, it automatically creates an initial admin token. Check the API container logs to find this token:

```bash
docker logs image_moderation_api
```

Look for: `Initial admin token created: <token_value>`

## Troubleshooting

### Common Issues

1. **API container restarting:**

   ```bash
   docker logs image_moderation_api
   ```

2. **MongoDB connection issues:**

   - Ensure MongoDB container is running
   - Check network connectivity between containers
   - Verify MongoDB credentials in environment variables

3. **Frontend not loading:**

   - Check if API is accessible at http://localhost:7000
   - Verify CORS configuration
   - Check browser console for errors

4. **Permission denied errors:**
   - Ensure Docker has proper permissions
   - Check file ownership in mounted volumes

### Useful Commands

```bash
# View all container logs
docker-compose logs

# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up --build

# Stop all services
docker-compose down

# Remove all data (including database)
docker-compose down -v
```

## Architecture

```
Frontend (React) <-> API (FastAPI) <-> Database (MongoDB)
     :3000              :7000              :27017
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB 7.0
- **Frontend**: React 18, Axios
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest, Pytest-asyncio
- **Image Processing**: Pillow (PIL), NumPy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

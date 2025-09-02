# Renais Gin: Craft Your Perfect World 🍸✨

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.2%2B-green)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A transformative Django web application that turns premium gin consumption into a global sustainability movement. Renais Gin combines blockchain technology, AI validation, and community engagement to create a participatory ecosystem where every bottle purchase contributes to positive global impact.

![Renais Gin Dashboard](https://via.placeholder.com/800x400/2c3e50/ffffff?text=Renais+Gin+Dashboard)

## 🌟 Vision

> "We don't sell gin. We sell a key. A key to a locked room in the human spirit where the desire to create, to connect, and to leave things better than we found it resides."

## ✨ Features

### 🍾 Digital-Physical Integration
- **QR Code Authentication**: Each bottle features a unique QR code linking physical products to digital experiences
- **Blockchain Verification**: Immutable recording of sustainability pledges on the blockchain
- **Smart Rebate System**: $5 rebate program tied to verified environmental actions

### 🤖 AI-Powered Validation
- **Sentiment Analysis**: Natural language processing to validate pledge authenticity
- **Karma Economy**: Community-driven validation system requiring peer approval
- **Impact Categorization**: Automatic classification of pledges into environmental, community, or educational impact

### 🌍 Sustainability Focus
- **Terroir Tracking**: Detailed geographical and agricultural data for each batch
- **Impact Metrics**: Real-time dashboard showing global community impact
- **Circular Economy**: Upcycled grape usage from renowned wine regions

### 👥 Community Ecosystem
- **Renais Circles**: User-led local chapters for community action
- **Global Network**: Connect with like-minded individuals worldwide
- **Story Sharing**: Share and discover impact stories through the Karma Chronicle

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Redis (for celery tasks)
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/renais-gin.git
cd renais-gin
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load sample data**
```bash
python manage.py add_test_bottles --count 10
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the application in action!

## 🏗️ Project Structure

```
renais-gin/
├── core/                 # Main Django application
│   ├── management/
│   │   └── commands/    # Custom management commands
│   ├── migrations/      # Database migrations
│   ├── models.py        # Database models
│   ├── services.py      # Business logic and services
│   ├── views.py         # View controllers
│   └── urls.py          # Application URL routes
├── static/              # Static assets
│   ├── css/
│   │   └── renais.css   # Custom styles
│   ├── js/
│   │   └── renais.js    # Custom JavaScript
│   └── images/          # Images and icons
├── templates/           # Django templates
│   ├── base.html        # Base template
│   └── core/            # App-specific templates
├── media/               # User-uploaded files
└── renais_gin/          # Project settings
    ├── settings/        # Environment-specific settings
    ├── urls.py          # Root URL configuration
    └── wsgi.py          # WSGI application
```

## 🎯 Core Functionality

### Bottle Registration Flow
1. **Scan QR Code**: Users scan the QR code on their Renais Gin bottle
2. **Terroir Verification**: System verifies bottle authenticity and displays terroir data
3. **Pledge Creation**: User submits a sustainability pledge for their $5 rebate
4. **Community Validation**: Pledge is validated by the community through the Karma system
5. **Rebate Processing**: Upon approval, rebate is processed and impact is recorded

### AI Validation System
The application uses multiple layers of validation:
- **Sentiment Analysis**: NLP algorithms assess pledge authenticity
- **Pattern Recognition**: Identifies high-quality impact commitments
- **Community Governance**: Distributed validation through peer review
- **Blockchain Recording**: Immutable record of all validated pledges

## 🔧 Configuration

### Environment Variables

```ini
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=psql://user:pass@localhost:5432/renais_gin
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,.yourdomain.com
BLOCKCHAIN_PROVIDER=https://mainnet.infura.io/v3/your-project-id
```

### Settings Overview

The project uses a modular settings structure:
- `base.py`: Core settings shared across all environments
- `development.py`: Development-specific settings
- `production.py`: Production configuration
- `test.py`: Testing environment settings

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python manage.py test

# Run with coverage reporting
coverage run manage.py test
coverage report

# Run specific test module
python manage.py test core.tests.test_views
```

### Testing the AI Validation

To test the pledge validation system:

1. Register a test bottle:
```bash
python manage.py add_test_bottles --count 5
```

2. Use this approved pledge format for testing:
```python
pledge_text = "I pledge to use this $5 rebate to purchase and plant 10 native oak and maple saplings in partnership with the city's 'ReGreen Our Parks' initiative."
impact_plan = "I will coordinate with the Parks Department to confirm their planting schedule, purchase saplings at the local conservation nursery, and organize a community planting day within the next 30 days."
```

## 🚀 Deployment

### Production Deployment

1. **Set up production environment variables**
2. **Configure static files**
```bash
python manage.py collectstatic
```
3. **Set up database**
```bash
python manage.py migrate
```
4. **Configure WSGI server** (Gunicorn recommended)
5. **Set up reverse proxy** (Nginx recommended)
6. **Configure SSL certificate**
7. **Set up monitoring and logging**

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d --build

# Run specific services
docker-compose up web worker redis
```

## 📊 API Endpoints

The application provides RESTful API endpoints:

- `GET /api/bottles/` - List registered bottles
- `POST /api/pledges/` - Create a new pledge
- `GET /api/metrics/` - Get movement metrics
- `GET /api/impact/` - Get impact statistics

### Example API Usage

```bash
# Get movement metrics
curl -X GET http://localhost:8000/api/metrics/

# Create a new pledge
curl -X POST http://localhost:8000/api/pledges/ \
  -H "Content-Type: application/json" \
  -d '{
    "bottle_id": "TEST_001",
    "pledge_text": "Your pledge here",
    "impact_plan": "Your impact plan here"
  }'
```

## 🤝 Contributing

We welcome contributions to the Renais Gin project! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

For detailed development setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Emma & Alex Watson** for the vision and inspiration
- **Chablis winegrowers** for their sustainable practices
- **The Renais community** for their commitment to positive impact
- **Open source contributors** who make projects like this possible

## 📞 Support

For support and questions:
- 📧 Email: support@renaisgin.com
- 🐛 [Issue Tracker](https://github.com/your-username/renais-gin/issues)
- 💬 [Community Forum](https://community.renaisgin.com)

## 🌐 Connect

- 🌍 [Official Website](https://www.renaisgin.com)
- 📷 [Instagram](https://instagram.com/renaisgin)
- 🐦 [Twitter](https://twitter.com/renaisgin)
- 📖 [Documentation](https://docs.renaisgin.com)

---

**Craft Your Perfect World. One Bottle, One Pledge, One Community at a Time.** ✨

---

*This project is not affiliated with Renais Gin or its parent company. It is an open-source demonstration of sustainable technology integration in the spirits industry.*

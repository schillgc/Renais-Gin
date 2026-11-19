# Renais Gin: Craft Your Perfect World 🍸✨

[![Python Version](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.2.19-green)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django demonstration of bottle registration, sustainability pledges, community review, and aggregate movement metrics. The current default branch is a prototype: it does not execute blockchain transactions, call an AI model, or issue financial rebates. Product claims and impact records are not independently verified.

## 🌟 Vision

> "We don't sell gin. We sell a key. A key to a locked room in the human spirit where the desire to create, to connect, and to leave things better than we found it resides."

## ✨ Features

### 🍾 Digital-Physical Integration
- **QR Code Authentication**: Each bottle features a unique QR code linking physical products to digital experiences
- **Bottle records and QR codes**: Local Django records can generate a QR image for a bottle.
- **Pledge workflow**: Submitted pledges enter a review queue; the application does not issue or transfer money.

### Pledge pre-screening prototype
- **Text heuristic**: A small keyword/length heuristic rejects some submissions. It is not an AI model, fraud detector, or proof of authenticity.
- **Community review**: A Django account can validate a given pledge once; three positive votes change its status to approved.
- **Impact categorization**: A simple keyword classifier assigns an environmental, community, education, or other label.

### 🌍 Sustainability Focus
- **Terroir Tracking**: Detailed geographical and agricultural data for each batch
- **Impact Metrics**: Real-time dashboard showing global community impact
- **Data provenance**: Terroir/product fields are stored as supplied; the application does not independently verify sourcing or sustainability claims.

### 👥 Community Ecosystem
- **Renais Circles**: User-led local chapters for community action
- **Global Network**: Connect with like-minded individuals worldwide
- **Story Sharing**: Share and discover impact stories through the Karma Chronicle

## 🚀 Quick Start

### Prerequisites

- Python 3.12 (the maintained CI and domain-test baseline)
- PostgreSQL (recommended) or SQLite
- Redis (for celery tasks)
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/schillgc/renais-gin.git
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
Set the required variables in your shell or deployment platform (see `.env.example`).
# Do not commit real secret values.
```

5. **Run migrations**
```bash
python renais_gin/manage.py migrate
```

6. **Create superuser**
```bash
python renais_gin/manage.py createsuperuser
```

7. **Load sample data**
```bash
python renais_gin/manage.py add_test_bottles --count 10
```

8. **Run development server**
```bash
python renais_gin/manage.py runserver
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
3. **Pledge Creation**: The account holder submits a sustainability pledge for a registered bottle.
4. **Community Review**: The heuristic pre-screen can reject a submission; otherwise it remains in review until three distinct authenticated accounts approve it.
5. **Review Completion**: Approval changes the pledge status only. No rebate is paid and `rebate_processed` remains false because no payment integration exists.

### Validation boundaries
- The preliminary text screen is a deterministic keyword/length heuristic, not AI or machine learning.
- A heuristic result cannot approve a pledge. Accepted submissions enter the `needs_review` state.
- Community approval requires three positive votes from distinct Django accounts. The application does not establish that accounts represent unique real-world people or prevent coordinated voting across accounts.
- Approval does not trigger a payment or external blockchain transaction.

## 🔧 Configuration

### Environment Variables

```ini
DJANGO_SECRET_KEY=<generate-a-new-random-secret>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
# Configure optional service credentials separately in your deployment environment.
```

### Settings Overview

The default branch currently uses a single environment-driven settings module at `renais_gin/renais_gin/settings.py`. The test suite uses `renais_gin/renais_gin/test_settings.py` with an in-memory SQLite database. Do not assume the older modular settings layout described by previous project scaffolding is present.

## 🧪 Testing

Run the current domain tests from the `renais_gin/` directory with the isolated settings module:

```bash
python manage.py test core --settings=renais_gin.test_settings --verbosity 2
```

The suite uses an in-memory database and tests pledge submission/review integrity, one-vote-per-account enforcement, non-payment on approval, and the read-only public metrics endpoint. CI installs only the small runtime needed for these tests.

### Testing the pledge workflow

The domain test suite creates a bottle and pledge in a disposable in-memory database. It confirms that even a high-scoring heuristic submission remains `needs_review`, that one account cannot vote twice, and that three distinct positive votes can approve a pledge without marking a rebate as paid. The test data is synthetic; no live provider or payment account is called.

## 🚀 Deployment

### Production Deployment

1. **Set up production environment variables**
2. **Configure static files**
```bash
python manage.py collectstatic
```
3. **Set up database**
```bash
python renais_gin/manage.py migrate
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

The current routes are Django page/form endpoints plus one JSON metrics endpoint:

- `GET /api/metrics/` — return the last stored aggregate snapshot. This endpoint is read-only; it does not recalculate or write metrics.
- `POST /register-bottle/` — authenticated bottle registration form.
- `POST /submit-pledge/<bottle_id>/` — authenticated pledge form for a bottle registered to the current account.
- `GET` / `POST /validate-pledge/<pledge_id>/` — authenticated community review form; each account can vote once per pledge.
- `GET /download-pdf/<pdf_id>/` — authenticated download limited to the owning account.

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
- 📧 Email: support@renais.com
- 🐛 [Issue Tracker](https://github.com/schillgc/renais-gin/issues)
- 💬 [Community Forum](https://community.renais.com)

## 🌐 Connect

- 🌍 [Official Website](https://www.renais.com)
- 📷 [Instagram](https://instagram.com/renaisgin)
- 🐦 [Twitter](https://twitter.com/renaisgin)
- 📖 [Documentation](https://docs.renaisgin.com)

---

**Craft Your Perfect World. One Bottle, One Pledge, One Community at a Time.** ✨

---

*This project is not affiliated with Renais Gin or its parent company. It is an open-source demonstration of sustainable technology integration in the spirits industry.*

## Current branch and integration status

The default branch contains the current security-hardened settings baseline. A separate `full` branch holds a larger application expansion, but it is not approved for direct merging or deployment until its configuration, generated artifacts, dependencies, migrations, and application behavior pass the gates in [the integration review](docs/full-branch-integration-review.md). Do not use that branch as a production release.

## Security

See [SECURITY.md](SECURITY.md) for this repository's security, privacy, and responsible-use guidance.

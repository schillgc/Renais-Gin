# Renais Gin: Craft Your Perfect World 🍸✨

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.2%2B-green)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A transformative Django web application that turns premium gin consumption into a global sustainability movement. Renais Gin combines blockchain technology, AI validation, and community engagement to create a participatory ecosystem where every bottle purchase contributes to positive global impact.

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
- **Personalized Recommendations**: AI-driven content and cause recommendations

### 🌍 Sustainability Focus
- **Terroir Tracking**: Detailed geographical and agricultural data for each batch
- **Impact Metrics**: Real-time dashboard showing global community impact
- **Circular Economy**: Upcycled grape usage from renowned wine regions

### 👥 Community Ecosystem
- **Renais Circles**: User-led local chapters for community action
- **Global Network**: Connect with like-minded individuals worldwide
- **Story Sharing**: Share and discover impact stories through the Karma Chronicle

### 🔧 Technical Excellence
- **RESTful API**: Complete API for mobile apps and external services
- **Modular Architecture**: Clean separation of concerns with dedicated AI services
- **Environment-specific settings**: Separate development and production configuration (requires deployment review)
- **Security controls**: Production startup now requires an explicit signing key and hostname allowlist

## Integration status

This branch is an integration draft, not a production release. AI, blockchain, community-validation, rebate, background-task, and external-provider capabilities must be independently tested before they are described as operational. Blockchain mock mode, sample data, and development-only flows must not be mistaken for live services.

Do not deploy this branch or apply its migrations to an existing database until the dependency set, migration path, data preservation, reverse migrations, authentication, authorization, secrets, and end-to-end workflows have been reviewed and tested against disposable representative data. The default `master` branch remains the supported baseline.

## 🚀 Quick Start

The Django project is in `renais_gin/`; dependency declarations are in the repository root.

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
cd renais_gin
python manage.py check
```

For a fresh local development database only, apply the committed migrations with `python manage.py migrate`, then create your own administrator interactively with `python manage.py createsuperuser`. Never use shared or hard-coded demo credentials.

Production startup requires `DJANGO_SECRET_KEY` and an explicit comma-separated `DJANGO_ALLOWED_HOSTS` value. PostgreSQL Compose startup also requires `POSTGRES_PASSWORD` to be supplied through the environment. Do not commit secrets or production data.


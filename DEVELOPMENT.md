# Development Guide for Renais Gin

## 🛠 Development Environment Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (recommended) or SQLite
- Redis 6+ (for Celery tasks)
- Node.js 16+ (for frontend tooling)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-organization/renais-gin.git
   cd renais-gin
   ```

2. **Create and activate virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   
   # Using conda
   conda create -n renais-gin python=3.10
   conda activate renais-gin
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Set up database**
   ```bash
   # For PostgreSQL
   createdb renais_gin_dev
   
   # For SQLite (default)
   # No action needed
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load sample data**
   ```bash
   python manage.py add_test_bottles --count 20
   python manage.py loaddata core/fixtures/initial_data.json
   ```

9. **Start development server**
   ```bash
   python manage.py runserver
   ```

10. **Start Celery worker (optional)**
    ```bash
    celery -A renais_gin worker -l info
    ```

## 🎨 Frontend Development

### CSS and JavaScript Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Build CSS and JavaScript**
   ```bash
   # One-time build
   npm run build
   
   # Watch for changes during development
   npm run watch
   ```

3. **Using Sass (optional)**
   ```bash
   # If using Sass instead of plain CSS
   sass --watch static/scss:static/css
   ```

### Template Structure

```
templates/
├── base.html              # Base template
├── includes/              # Reusable template components
│   ├── header.html
│   ├── footer.html
│   └── navigation.html
└── core/                  # App-specific templates
    ├── dashboard.html
    ├── register_bottle.html
    ├── submit_pledge.html
    └── *.html
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test core.tests.test_models

# Run tests with coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report

# Run tests in parallel
python manage.py test --parallel
```

### Writing Tests

Follow the testing structure:

```python
# Example test structure
class BottleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
    
    def test_bottle_creation(self):
        # Test specific functionality
        bottle = Bottle.objects.create(
            bottle_id="TEST_001",
            batch_id="BATCH_123",
            production_date=date.today(),
            registered_to=self.user
        )
        self.assertEqual(bottle.bottle_id, "TEST_001")
```

### Test Data Management

Use factories for test data creation:

```python
# core/factories.py
import factory
from django.contrib.auth.models import User
from core.models import Bottle, KarmaPledge

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

class BottleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bottle
    
    bottle_id = factory.Sequence(lambda n: f'BOTTLE_{n:03d}')
    batch_id = 'BATCH_001'
    production_date = factory.Faker('date_this_year')
```

## 🔧 Development Tools

### Recommended IDE Setup

- **VS Code** with extensions:
  - Python
  - Django
  - Prettier
  - ESLint
  - SQLite
- **PyCharm** with Django support

### Debugging

1. **Using VS Code**
   - Create a `.vscode/launch.json` file:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Django",
         "type": "python",
         "request": "launch",
         "program": "${workspaceFolder}/manage.py",
         "args": ["runserver"],
         "django": true
       }
     ]
   }
   ```

2. **Using Django Debug Toolbar**
   - Already included in development requirements
   - Access at http://localhost:8000/__debug__/

3. **Print debugging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   def my_view(request):
       logger.debug("This is a debug message")
       # Your view logic
   ```

### Code Quality Tools

```bash
# Run linters
flake8 .  # PEP8 compliance
black .   # Code formatting
isort .   # Import sorting

# Run security check
bandit -r .

# Check for outdated dependencies
pip list --outdated
```

## 📦 Dependency Management

### Adding New Dependencies

1. **Production dependencies**
   ```bash
   pip install <package>
   pip freeze | grep <package> >> requirements/production.txt
   ```

2. **Development dependencies**
   ```bash
   pip install <package>
   pip freeze | grep <package> >> requirements/development.txt
   ```

3. **Update all dependencies**
   ```bash
   pip install -r requirements/development.txt --upgrade
   pip freeze > requirements/development.txt
   ```

## 🔄 Database Management

### Migrations

```bash
# Create migrations
python manage.py makemigrations

# Check migration status
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Create data migration
python manage.py makemigrations --empty core --name <migration_name>
```

### Database Fixtures

```bash
# Create fixtures from existing data
python manage.py dumpdata core.Bottle --indent 2 > core/fixtures/bottles.json

# Load fixtures
python manage.py loaddata bottles
```

## 🚀 Deployment Preparation

### Production Checks

```bash
# Run production checks
python manage.py check --deploy

# Collect static files
python manage.py collectstatic

# Create production database
python manage.py migrate --settings=renais_gin.settings.production
```

### Environment Configuration

Ensure these settings are configured in production:

```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## 🤝 Contributing Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**
   - Follow coding standards
   - Write tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python manage.py test
   flake8 .
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🐛 Common Issues and Solutions

### Database Connection Issues
```bash
# If using PostgreSQL, ensure the service is running
sudo service postgresql start

# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py loaddata initial_data
```

### Migration Conflicts
```bash
# If migrations are conflicting
python manage.py migrate --fake
# Or reset migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic

# Check STATIC_ROOT and STATIC_URL settings
# Ensure DEBUG=False in production
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## ❓ Getting Help

If you encounter issues during development:

1. Check this documentation
2. Search existing GitHub issues
3. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Your environment details

---

*Happy coding! Remember, we're not just building an application - we're crafting a better world.* 🌍✨

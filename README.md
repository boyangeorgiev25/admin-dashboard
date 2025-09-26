# Admin Dashboard

Secure admin dashboard for platform moderation with user management, audit logging, and security features.

## Setup

1. **Install**

   ```bash
   git clone <repository-url>
   cd dashboard
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure**

   ```bash
   cp .env.example .env
   # Edit .env with your database and security settings
   ```

3. **Run**
   ```bash
   streamlit run app.py
   ```

## Configuration

Required environment variables in `.env`:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `SECRET_KEY` (32+ characters)
- `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` (bcrypt)

## Features

- User lookup and management
- Direct messaging and banning
- Real-time analytics
- Comprehensive audit logging
- Security validation

## Testing

```bash
pytest                    # Run tests
black . && isort .       # Format code
pre-commit run --all-files # Quality checks
```

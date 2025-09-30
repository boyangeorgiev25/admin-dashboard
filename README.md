# Admin Dashboard

A secure, web-based admin dashboard for platform moderation and user management. Built with Streamlit and designed for scalable user administration, analytics, and audit logging.

## Features

### 🔐 Authentication & Security

- Secure admin authentication with bcrypt password hashing
- Session timeout management
- Comprehensive audit logging of all admin actions
- Input sanitization and security validation

### 👥 User Management

- **User Lookup**: Search and view detailed user profiles
- **Moderation Tools**: Ban/unban users with reason tracking
- **Direct Messaging**: Send messages to users directly
- **Bulk Operations**: Manage multiple users efficiently

### 📊 Analytics & Reporting

- Real-time user statistics and growth metrics
- Interactive charts and visualizations with Plotly
- Platform usage analytics
- Custom date range filtering

### 📝 Audit & Feedback

- Complete audit trail of all admin actions
- User feedback management and review
- Detailed activity reports
- Export capabilities for compliance

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

Configure your MySQL database and update the connection details in `.env`:

```bash
cp .env.example .env
```

### 3. Environment Configuration

Edit `.env` with your settings:

#### Generate SECRET_KEY

The SECRET_KEY is a cryptographic secret used for session management and security features. It must be:

- At least 64 characters long (hexadecimal format)
- Completely random and unpredictable
- Unique for each installation

**Generate using Python:**

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

This generates 32 random bytes and converts them to a 64-character hexadecimal string.

**Or using OpenSSL:**

```bash
openssl rand -hex 32
```

**Example output:**

```
a3f8c92b4e7d1a6f9c2b5e8d7a4f1c6b9e2a5d8c1f4b7e0a3d6c9f2b5e8a1d4c7
```

Copy this entire string and use it as your SECRET_KEY in the `.env` file.

#### Generate Password Hash

To create a secure password hash for admin login:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password_here', bcrypt.gensalt()).decode())"
```

Replace `your_password_here` with your desired password. Copy the output (starts with `$2b$12$`).

#### Update .env file

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_PORT=3306

# Security - Generate using command above (produces 64-char hex string)
SECRET_KEY=your_64_character_hex_string_here
SESSION_TIMEOUT=1800

# Admin Credentials - Generate hash using bcrypt command above
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$your_full_bcrypt_hash_here

```

### 4. Run the Application

```bash
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`

## Docker Deployment

### Running with Docker

#### 1. Set Up Environment Variables

Create a `.env` file with your credentials (see Environment Configuration above):

```bash
cp .env.example .env
```

Generate your SECRET_KEY and password hashes as described in the Environment Configuration section.

#### 2. Build and Run

For production deployment:

```bash
docker-compose up -d
```

The dashboard will be available at `http://localhost:8501` with health checks enabled.

#### 3. Verify the Container

Check if the container is running:

```bash
docker-compose ps
```

View logs:

```bash
docker-compose logs -f
```

#### 4. Stop the Container

```bash
docker-compose down
```

### Docker Environment Variables

When using Docker, environment variables can be set in multiple ways:

1. **Using .env file** (recommended): Create `.env` in the same directory as `docker-compose.yml`
2. **In docker-compose.yml**: Add environment variables under the `environment` section
3. **Pass at runtime**: Use `-e` flag with `docker run`

Example docker-compose.yml environment section:

```yaml
environment:
  - SECRET_KEY=${SECRET_KEY}
  - ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}
  - DB_HOST=db
  - DB_NAME=admin_dashboard
```

## Project Structure

```
dashboard/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Authentication and security
│   ├── services/        # Business logic and data services
│   ├── ui/              # Streamlit interface components
│   │   └── tabs/        # Individual dashboard tabs
│   └── utils/           # Utilities and error handling
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── docker-compose.yml   # Production deployment
```

## Development

### Code Quality

```bash
pytest                     # Run test suite
black . && isort .        # Format code
pre-commit run --all-files # Run all quality checks
```

### Adding New Features

1. Create new services in `src/services/`
2. Add UI components in `src/ui/tabs/`
3. Update authentication in `src/core/auth.py` if needed
4. Add tests in `tests/`

## Security Considerations

- All admin actions are logged with timestamps and user context
- Database connections use parameterized queries to prevent SQL injection
- User inputs are sanitized using the `bleach` library
- Sessions expire automatically for security
- Password hashing uses bcrypt with appropriate salt rounds

## Dependencies

- **Streamlit**: Web application framework
- **SQLAlchemy**: Database ORM
- **Plotly**: Interactive data visualization
- **bcrypt**: Secure password hashing
- **bleach**: HTML sanitization
- **MySQL Connector**: Database connectivity

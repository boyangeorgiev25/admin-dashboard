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
git clone https://github.com/boyangeorgiev25/admin-dashboard.git
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

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_PORT=3306

# Security
SECRET_KEY=your_32_character_secret_key_here
SESSION_TIMEOUT=1800

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_bcrypt_hash
```

### 4. Run the Application

```bash
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`

## Docker Deployment

For production deployment:

```bash
docker-compose up -d
```

The dashboard will be available at `http://localhost:8501` with health checks enabled.

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

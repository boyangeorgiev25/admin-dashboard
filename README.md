# Admin Dashboard

A comprehensive, secure admin dashboard for platform moderation and management. Built with Streamlit for intuitive user experience and designed for scalable administration, content moderation, and audit logging.

## 🚀 Features

### 🔐 Authentication & Security

- Secure admin authentication with bcrypt password hashing
- Session timeout management (configurable)
- Comprehensive audit logging of all critical actions
- Input sanitization and security validation
- No hardcoded credentials (environment-based configuration)
- SQL injection prevention with parameterized queries

### 👥 User Management

- **User Lookup**: Search users by ID or username with detailed profiles
- **User Activities**: View user's activities, messages, and participation history
- **Moderation Tools**: Ban/unban users with reason tracking
- **Direct Messaging**: Send messages to users as admin
- **Account Management**: View registration status, verification, statistics

### 💬 Content Moderation

#### Chat Moderation

- Monitor activity group chats
- View direct messages between users
- Search messages by keyword across all chats
- Flag inappropriate content
- View chat statistics and engagement

#### Forum Moderation

- View all community forum threads
- Monitor thread replies and discussions
- Delete inappropriate threads/replies with audit trail
- View reported content
- Search forum posts by keyword
- Track upvotes and engagement
- View community members

### 🚩 Reports & Feedback

- **User Reports**: Handle reported users and content
- **Feedback Management**: Review and respond to user feedback
- **Report Analytics**: Track report trends and patterns

### 📊 Analytics & Insights

- Real-time platform statistics
- User growth and activity metrics
- Interactive charts with Plotly
- Custom date range filtering
- Export capabilities for reporting

### ⚙️ Platform Configuration

#### Activity Types

- Manage activity categories and subtypes
- Multi-language support (EN, NL, FR)
- Custom icons and images
- Subtype codes for categorization

#### Venues

- Venue/location management
- Link venues to activity types
- Address and location data
- Venue keywords for discovery

#### Communities

- Community management (create, edit, delete)
- Starter vs. regular community distinction
- Member tracking
- Forum integration

### 🔔 Communications

#### Notifications

- Send bulk push notifications
- Filter by language, registration status, user ID range
- Preview recipient count before sending
- Track sent/failed notifications

#### ConvertKit Integration

- Sync users to ConvertKit email lists
- Bulk email export
- Tag management
- Subscriber tracking

## 📋 Quick Start

### Prerequisites

- **Python 3.9+** installed on your system
- **MySQL database** with your application data
- **Git** for cloning the repository
- **Docker** (optional, for containerized deployment)

### Step 1: Clone the Repository

```bash
git clone https://github.com/boyangeorgiev25/admin-dashboard.git
cd admin-dashboard
```

### Step 2: Set Up Python Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate          # On macOS/Linux
venv\Scripts\activate             # On Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Now edit the `.env` file with your settings:

#### 3.1 Generate SECRET_KEY

The SECRET_KEY secures your session data. Generate a random 64-character hex string:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

**Example output:**

```
a3f8c92b4e7d1a6f9c2b5e8d7a4f1c6b9e2a5d8c1f4b7e0a3d6c9f2b5e8a1d4c7
```

Copy this value and paste it as your `SECRET_KEY` in `.env`.

#### 3.2 Generate Admin Password Hash

Create a secure bcrypt hash for your admin password:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'YourSecurePassword123', bcrypt.gensalt()).decode())"
```

**Example output:**

```
$2b$12$rKx9YhZ8mVL.WzN5qP3tK.xYvZj4nHmRfGpD2wQ8eX1vC7sB6aT5u
```

Copy this entire hash and paste it as your `ADMIN_PASSWORD_HASH` in `.env`.

#### 3.3 Complete .env Configuration

Open `.env` in your text editor and fill in all values:

```env
# Database Configuration
DB_HOST=your-database-host.com      # e.g., localhost or 34.76.230.176
DB_USER=your_db_username            # MySQL username
DB_PASSWORD=your_db_password        # MySQL password
DB_NAME=your_database_name          # Database name
DB_PORT=3306                        # MySQL port (default: 3306)

# Security Settings
SECRET_KEY=paste_your_64_char_hex_here
SESSION_TIMEOUT=1800                # Session timeout in seconds (30 min)

# Admin Login Credentials
ADMIN_USERNAME=admin                # Choose your admin username
ADMIN_PASSWORD_HASH=$2b$12$paste_your_bcrypt_hash_here

# Optional: ConvertKit Email Marketing (leave empty if not using)
CONVERTKIT_API_KEY=
CONVERTKIT_API_SECRET=
CONVERTKIT_SEQUENCE_ID=
```

### Step 4: Verify Database Connection

Test your database connection before running the app:

```bash
python -c "
from src.services.database_service import DatabaseService
db = DatabaseService()
print('Database connection successful!')
"
```

If you see an error, double-check your database credentials in `.env`.

### Step 5: Run the Application

Start the dashboard:

```bash
streamlit run app.py
```

You should see output like:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

Open your browser and navigate to `http://localhost:8501`

### Step 6: Login

Use the credentials you set in `.env`:

- **Username**: The value of `ADMIN_USERNAME` (e.g., `admin`)
- **Password**: The **original password** you used when generating the hash (e.g., `YourSecurePassword123`)

 **You're now logged in to the admin dashboard!**

## 🐳 Docker Deployment

Docker provides an easier way to deploy the dashboard with all dependencies pre-configured.

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

### Step 1: Prepare Environment

Create your `.env` file following the same steps as the Quick Start guide:

```bash
cp .env.example .env
# Edit .env with your database credentials and secrets
```

### Step 2: Build and Start

Build the Docker image and start the container:

```bash
docker-compose up -d
```

This will:

- Build a Docker image with Python 3.11 and all dependencies
- Create a container named `jointly-dashboard`
- Start the Streamlit app on port 8501
- Set up health checks for monitoring

### Step 3: Verify Deployment

Check if the container is running:

```bash
docker-compose ps
```

You should see:

```
NAME                  STATUS              PORTS
jointly-dashboard     Up 2 minutes        0.0.0.0:8501->8501/tcp
```

### Step 4: View Logs

Monitor the application logs in real-time:

```bash
docker-compose logs -f
```

Press `Ctrl+C` to stop following logs.

### Step 5: Access the Dashboard

Open your browser to `http://localhost:8501`

### Managing the Container

**Stop the dashboard:**

```bash
docker-compose down
```

**Restart the dashboard:**

```bash
docker-compose restart
```

**Rebuild after code changes:**

```bash
docker-compose up -d --build
```

**View resource usage:**

```bash
docker stats jointly-dashboard
```

### Troubleshooting Docker

**Container keeps restarting:**

```bash
# Check logs for errors
docker-compose logs --tail=50

# Common issues:
# - Database connection failed (check .env)
# - Port 8501 already in use (change in docker-compose.yml)
```

**Database connection timeout:**

- Ensure your database allows connections from Docker containers
- If using `localhost`, change to `host.docker.internal` on Mac/Windows
- On Linux, use your host machine's IP address

## 📁 Project Structure

```
dashboard/
├── src/
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── config.py        # Environment config loader
│   ├── core/                # Core functionality
│   │   ├── auth.py          # Authentication system
│   │   ├── models.py        # SQLAlchemy database models (23 models)
│   │   └── security.py      # Security validators & audit logging
│   ├── services/            # Business logic layer (11 services)
│   │   ├── database_service.py           # Database connection manager
│   │   ├── user_service.py               # User management
│   │   ├── moderation_service.py         # User moderation actions
│   │   ├── chat_moderation_service.py    # Chat monitoring
│   │   ├── community_forum_service.py    # Forum moderation
│   │   ├── analytics_service.py          # Platform analytics
│   │   ├── notification_service.py       # Push notifications
│   │   ├── activity_type_service.py      # Activity type management
│   │   ├── venue_service.py              # Venue management
│   │   ├── community_service.py          # Community management
│   │   └── convertkit_service.py         # Email marketing
│   ├── ui/                  # Streamlit UI components
│   │   ├── components.py    # Reusable UI components
│   │   ├── dashboard.py     # Main dashboard layout
│   │   ├── error_handler.py # UI error handling
│   │   └── tabs/            # Dashboard tabs (12 tabs)
│   │       ├── user_lookup_tab.py
│   │       ├── user_activities_tab.py
│   │       ├── chat_moderation_tab.py
│   │       ├── forum_moderation_tab.py
│   │       ├── reports_tab.py
│   │       ├── feedback_tab.py
│   │       ├── analytics_tab.py
│   │       ├── notifications_tab.py
│   │       ├── activity_types_tab.py
│   │       ├── venues_tab.py
│   │       ├── communities_tab.py
│   │       └── convertkit_tab.py
│   └── utils/               # Utility modules
│       ├── error_handler.py # Error handling decorators
│       ├── exceptions.py    # Custom exception classes
│       └── logging_config.py # Logging configuration
├── tests/                   # Test suite
│   ├── test_auth.py
│   └── test_security.py
├── .streamlit/              # Streamlit configuration
│   └── config.toml
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Environment template
└── README.md               # This file
```

## 🗄️ Database Schema

The dashboard expects the following main tables in your MySQL database:

### Core Tables

- `users` - User accounts and profiles
- `activities` - Platform activities/events
- `messages` - Activity group chat messages
- `ind_messages` - Direct messages between users

### Moderation Tables

- `reported_users` - User reports
- `deleted_users` - Deleted user audit trail
- `feedback` - User feedback submissions

### Community Tables

- `communities` - Community groups
- `community_threads` - Forum threads
- `community_thread_replies` - Thread replies
- `community_membership` - Community members
- `community_thread_upvotes` - Thread votes
- `community_thread_reply_upvotes` - Reply votes

### Chat Tables

- `chat_meta` - Chat metadata
- `chat_user_activity` - Chat memberships
- `ind_chats` - Direct message chats
- `ind_chat_membership` - DM participants
- `message_reactions` - Message reactions
- `ind_message_reactions` - DM reactions

### Configuration Tables

- `activity_types` - Activity categories
- `places` - Venue listings
- `activity_joiners` - Activity participants

See `src/core/models.py` for complete schema definitions.

## 🔒 Security Best Practices

### Implemented Security Features

1. **Authentication**

   - Bcrypt password hashing with salt
   - Session-based authentication
   - Configurable session timeout
   - Automatic session expiration

2. **Input Validation**

   - Input sanitization using bleach library
   - SQL injection prevention (parameterized queries)
   - XSS protection
   - CSRF protection (Streamlit built-in)

3. **Audit Logging**

   - All critical actions logged
   - Timestamp and context tracking
   - Action types: USER_BAN, DELETE_THREAD, etc.
   - Log file: `audit_log.json`

4. **Data Protection**
   - Environment-based configuration
   - No credentials in code
   - Secure session management
   - Connection pooling with auto-reconnect

### Production Deployment Checklist

- [ ] Generate unique SECRET_KEY (64 chars)
- [ ] Use strong admin password
- [ ] Secure `.env` file permissions (chmod 600)
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable database SSL/TLS
- [ ] Review audit logs regularly
- [ ] Update dependencies regularly
- [ ] Monitor application logs


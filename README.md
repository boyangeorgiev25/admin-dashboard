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

### 1. Installation

```bash
git clone https://github.com/boyangeorgiev25/admin-dashboard.git
cd dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

This dashboard connects to an existing MySQL database. Ensure your database has the required tables (see Database Schema section).

### 3. Environment Configuration

Create your `.env` file from the example:

```bash
cp .env.example .env
```

#### Generate SECRET_KEY

The SECRET_KEY is a cryptographic secret used for session management. Generate it using:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

This generates a 64-character hexadecimal string.

#### Generate Password Hash

Create a secure password hash for admin login:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password_here', bcrypt.gensalt()).decode())"
```

Replace `your_password_here` with your desired password.

#### Update .env File

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_PORT=3306

# Security
SECRET_KEY=your_64_character_hex_string_here
SESSION_TIMEOUT=1800

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$your_full_bcrypt_hash_here

# Optional: ConvertKit API
CONVERTKIT_API_KEY=your_api_key
CONVERTKIT_API_SECRET=your_api_secret
```

### 4. Run the Application

```bash
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`

## 🐳 Docker Deployment

### Build and Run

```bash
# Create .env file with your credentials
cp .env.example .env

# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

The dashboard will be available at `http://localhost:8501`

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

## 📊 Dashboard Navigation

The dashboard is organized into 5 main sections:

### 1. Users
- **Lookup** - Search and view user profiles
- **Activities** - View user activity history

### 2. Moderation
- **Chats** - Monitor chat messages
- **Forums** - Moderate forum posts
- **Reports** - Handle user reports
- **Feedback** - Review user feedback

### 3. Analytics
- Platform statistics and trends
- User growth metrics
- Activity analytics

### 4. Settings
- **Activity Types** - Manage categories
- **Venues** - Manage locations
- **Communities** - Manage groups

### 5. Communications
- **Notifications** - Send push notifications
- **ConvertKit** - Email marketing sync

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints where applicable
- Comprehensive error handling
- Service layer pattern
- Clear separation of concerns

### Adding a New Feature

1. **Add Model** (if needed): Update `src/core/models.py`
2. **Create Service**: Add to `src/services/`
3. **Create UI Tab**: Add to `src/ui/tabs/`
4. **Update Dashboard**: Register in `src/ui/dashboard.py`
5. **Test**: Add tests in `tests/`

## 📈 Statistics

- **Total Code**: ~5,800 lines
- **Database Models**: 23
- **Services**: 11
- **UI Components**: 12 tabs
- **Functions**: 75+ service methods
- **Error Handlers**: 40+ decorated functions
- **Audit Points**: 16 critical actions

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "
from src.services.database_service import DatabaseService
db = DatabaseService()
print('Database connection successful!')
"
```

### Authentication Issues

- Verify `ADMIN_PASSWORD_HASH` in `.env` matches your password
- Check `SECRET_KEY` is 64 characters (hex)
- Clear browser cookies/cache

### Port Already in Use

```bash
# Change port in command
streamlit run app.py --server.port 8502
```

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review audit logs for errors

## 🔄 Changelog

### Version 2.0.0 (Current)
- ✅ Added chat moderation system
- ✅ Added forum moderation system
- ✅ Expanded activity model (32 fields)
- ✅ Reorganized navigation (5 categories)
- ✅ Removed hardcoded credentials
- ✅ Added 6 chat models
- ✅ Added 5 forum models
- ✅ Improved security
- ✅ Clean, professional UI

### Version 1.0.0
- Initial release with user management
- Basic analytics
- Report handling
- Notification system

---

**Built with ❤️ using Streamlit and Python**

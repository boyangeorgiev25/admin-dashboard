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
print('✅ Database connection successful!')
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

🎉 **You're now logged in to the admin dashboard!**

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

## 📊 How to Use the Dashboard

Once logged in, you'll see a sidebar with 5 main sections. Here's what each section does:

### 👥 1. Users

#### Lookup Tab

Search and manage individual users:

1. Enter a **User ID** or **Username** in the search box
2. Click **Search** to view the user's profile
3. See detailed information: registration date, email, phone, verification status
4. **Actions available:**
   - **Ban User**: Provide a reason and ban the user
   - **Unban User**: Remove an existing ban
   - **Send Message**: Send a direct message to the user

#### User Activities Tab

View a user's complete activity history:

1. Enter a **User ID** in the search box
2. See all activities they've created or joined
3. View their chat messages and participation
4. Track their engagement over time

### 🛡️ 2. Moderation

#### Chat Moderation Tab

Monitor all platform chat activity:

- **Activity Chats**: View group chats for each activity
  - See all participants and messages
  - Search for specific keywords across all chats
  - Flag inappropriate content
- **Direct Messages**: Monitor private conversations between users
  - View message history
  - Search by sender, receiver, or content

**How to use:**

1. Select chat type (Activity Chats or Direct Messages)
2. Browse the list of chats
3. Click on a chat to expand and view messages
4. Use the search box to find specific content

#### Forum Moderation Tab

Moderate community forum discussions:

- **Threads**: View all forum threads across communities
  - See thread title, author, community, and upvotes
  - Read full thread content
  - Delete inappropriate threads
- **Replies**: Monitor all thread replies
  - View reply content and authors
  - Delete inappropriate replies
  - Track nested conversations

**How to use:**

1. Switch between **Threads** and **Replies** tabs
2. Use filters to find specific content
3. Click **Delete** with a reason to remove content
4. All deletions are logged in the audit trail

#### Reports Tab

Handle user reports and complaints:

1. View all reported users and their report reasons
2. See who submitted the report and when
3. **Actions:**
   - Review the reported user's profile
   - Ban the user if necessary
   - Mark report as resolved

#### Feedback Tab

Review and respond to user feedback:

1. See all feedback submitted by users
2. View feedback content, category, and timestamp
3. Track response status
4. Use feedback to improve the platform

### 📈 3. Analytics

View real-time platform statistics:

- **Total Users**: Current user count and growth
- **Active Users**: Users active in the last 30 days
- **Total Activities**: Number of activities created
- **User Growth Chart**: Visual representation of user growth over time
- **Custom Date Ranges**: Filter analytics by specific periods

**How to use:**

1. View the overview metrics at the top
2. Scroll down to see interactive charts
3. Use date pickers to filter data by time period
4. Export data for reporting purposes

### ⚙️ 4. Settings

#### Activity Types Tab

Manage activity categories and subtypes:

1. View all activity types with translations (EN, NL, FR)
2. **Create New**: Add a new activity type with emoji and image
3. **Edit**: Update existing activity type details
4. **Delete**: Remove activity types (with confirmation)

**Fields:**

- Type (e.g., Sports, Arts, Social)
- Subtype in 3 languages
- Subtype code (unique identifier)
- Emoji icon
- Image URL

#### Venues Tab

Manage locations and venues:

1. View all registered venues
2. **Create New Venue**: Add a venue with:
   - Name and address
   - Linked activity type
   - Keywords for search
   - Image and website URL
   - GPS coordinates
3. **Edit/Delete**: Manage existing venues

#### Communities Tab

Manage user communities:

1. View all communities with member counts
2. **Create Community**: Add a new community group
3. **Edit**: Update community details
4. **Delete**: Remove communities (archived, not truly deleted)
5. Toggle **Starter Community** status

### 📢 5. Communications

#### Notifications Tab

Send push notifications to users:

1. **Compose Message**: Write your notification title and body
2. **Filter Recipients**:
   - Language: EN, NL, FR, or All
   - Registration status: Completed or Not Completed
   - User ID range: Specific user segments
3. **Preview**: See how many users will receive the notification
4. **Send**: Deliver the notification
5. **Track**: View sent notifications and delivery status

**Example use cases:**

- Announce new features to all users
- Send reminders to incomplete registrations
- Target specific language groups

#### ConvertKit Tab

Sync users with your email marketing platform:

1. **View Stats**: See total subscribers and sync status
2. **Export Users**: Download user emails as CSV
3. **Sync to ConvertKit**: Push user data to ConvertKit
   - Bulk sync all users or specific segments
   - Automatic tagging
   - Sequence enrollment
4. **Monitor**: Track sync history and errors

**Requirements:**

- ConvertKit API credentials in `.env`
- Valid ConvertKit account

---

### 🔍 Common Tasks

**Ban a problematic user:**

1. Go to **Users → Lookup**
2. Search for the user by ID or username
3. Scroll to **Moderation Actions**
4. Click **Ban User**, provide a reason, confirm

**Delete inappropriate forum content:**

1. Go to **Moderation → Forums**
2. Find the thread or reply
3. Click **Delete**, enter reason, confirm
4. Action is logged in audit trail

**Send a platform announcement:**

1. Go to **Communications → Notifications**
2. Write your message title and body
3. Select target audience (language, status, etc.)
4. Preview recipient count
5. Click **Send Notification**

**View platform growth:**

1. Go to **Analytics**
2. View user growth chart
3. Adjust date range to see trends
4. Export data if needed

## 🛠️ Development & Architecture

### Project Architecture

This dashboard follows a **layered architecture** pattern:

```
┌─────────────────────────────────────┐
│         UI Layer (Streamlit)        │  ← User interface & components
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← Business logic & operations
├─────────────────────────────────────┤
│      Data Layer (SQLAlchemy)        │  ← Database models & queries
├─────────────────────────────────────┤
│      Database (MySQL)               │  ← Data storage
└─────────────────────────────────────┘
```

**Key Design Principles:**
- **Separation of Concerns**: Each layer has a specific responsibility
- **Service Pattern**: All business logic is in service classes
- **DRY (Don't Repeat Yourself)**: Reusable components and utilities
- **Security First**: Input validation, sanitization, and audit logging

### How the Code is Built

#### 1. Database Models (`src/core/models.py`)

SQLAlchemy ORM models define the database structure:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(100))
```

**23 models** represent all database tables (users, activities, messages, communities, etc.)

#### 2. Service Layer (`src/services/`)

Each service handles specific business logic:

```python
class UserService:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetch user from database with error handling"""

    def ban_user(self, user_id: int, reason: str):
        """Ban user and log action to audit trail"""
```

**11 service classes**:
- `DatabaseService` - Connection management & pooling
- `UserService` - User CRUD operations
- `ModerationService` - Ban/unban functionality
- `ChatModerationService` - Chat monitoring
- `CommunityForumService` - Forum moderation
- `AnalyticsService` - Statistics & reporting
- `NotificationService` - Push notifications
- `ActivityTypeService` - Activity category management
- `VenueService` - Location management
- `CommunityService` - Community CRUD
- `ConvertKitService` - Email marketing integration

#### 3. UI Components (`src/ui/`)

Streamlit components organized by functionality:

```python
def user_lookup_tab():
    """Render the user lookup interface"""
    st.header("User Lookup")
    user_id = st.number_input("User ID")
    if st.button("Search"):
        user = st.session_state.user_service.get_user_by_id(user_id)
        display_user_profile(user)
```

**12 tab modules** handle different sections of the dashboard.

#### 4. Security & Error Handling

**Error Handler Decorator:**
```python
@ErrorHandler.handle_database_error
def risky_database_operation():
    # Automatically catches and logs errors
```

**Audit Logging:**
```python
SecurityValidator.log_audit_action(
    action="USER_BAN",
    details={"user_id": 123, "reason": "spam"}
)
```

**Input Sanitization:**
```python
clean_input = SecurityValidator.sanitize_input(user_input)
```

### Adding a New Feature

#### Step 1: Add Database Model (if needed)

Edit `src/core/models.py`:

```python
class NewFeature(Base):
    __tablename__ = "new_features"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Step 2: Create Service Class

Create `src/services/new_feature_service.py`:

```python
from src.utils.error_handler import ErrorHandler
from src.services.database_service import DatabaseService
from src.core.models import NewFeature

class NewFeatureService:
    def __init__(self):
        self.db_service = DatabaseService()

    @ErrorHandler.handle_database_error
    def get_all_features(self):
        with self.db_service.get_session() as db:
            return db.query(NewFeature).all()
```

#### Step 3: Create UI Tab

Create `src/ui/tabs/new_feature_tab.py`:

```python
import streamlit as st

def new_feature_tab():
    st.header("New Feature")
    service = st.session_state.new_feature_service
    features = service.get_all_features()

    for feature in features:
        st.write(f"- {feature.name}")
```

#### Step 4: Register in Dashboard

Edit `src/ui/dashboard.py`:

```python
from src.services.new_feature_service import NewFeatureService
from src.ui.tabs.new_feature_tab import new_feature_tab

# In initialize_services():
st.session_state.new_feature_service = NewFeatureService()

# In render_dashboard():
tabs = st.tabs([..., "New Feature"])
with tabs[-1]:
    new_feature_tab()
```

#### Step 5: Test Your Feature

Create `tests/test_new_feature.py`:

```python
import pytest
from src.services.new_feature_service import NewFeatureService

def test_get_all_features():
    service = NewFeatureService()
    features = service.get_all_features()
    assert isinstance(features, list)
```

Run tests:
```bash
pytest tests/test_new_feature.py -v
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest --cov=src tests/
```

### Code Style & Best Practices

**Follow PEP 8:**
```bash
# Format code
black src/

# Check linting
flake8 src/
```

**Use Type Hints:**
```python
def get_user(user_id: int) -> Optional[User]:
    pass
```

**Error Handling:**
- Always use `@ErrorHandler` decorators for database operations
- Log all errors with context
- Return user-friendly error messages

**Security:**
- Sanitize all user inputs
- Use parameterized queries
- Log security-sensitive actions
- Validate permissions before destructive operations

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

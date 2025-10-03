# Services Documentation

This document provides detailed information about all service classes in the admin dashboard.

## Table of Contents

- [DatabaseService](#databaseservice)
- [UserService](#userservice)
- [ModerationService](#moderationservice)
- [ChatModerationService](#chatmoderationservice)
- [CommunityForumService](#communityforumservice)
- [AnalyticsService](#analyticsservice)
- [NotificationService](#notificationservice)
- [ActivityTypeService](#activitytypeservice)
- [VenueService](#venueservice)
- [CommunityService](#communityservice)
- [ConvertKitService](#convertkitservice)

---

## DatabaseService

**Location**: `src/services/database_service.py`

Centralized database connection manager used by all other services.

### Methods

#### `__init__()`
Initializes database connection from environment variables.

**Environment Variables Required:**
- `DB_HOST` - Database host
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name
- `DB_PORT` - Database port (default: 3306)

**Raises:**
- `ValueError` - If required environment variables are missing

#### `get_session()`
Returns a new database session for queries.

**Returns:** SQLAlchemy Session object

**Usage:**
```python
from services.database_service import DatabaseService

db_service = DatabaseService()
with db_service.get_session() as db:
    users = db.query(User).all()
```

---

## UserService

**Location**: `src/services/user_service.py`

Handles all user-related operations including lookup, management, and activity tracking.

### Methods

#### `get_user(search_type: str, search_value: str) -> Dict`
Search for a user by ID or username.

**Parameters:**
- `search_type`: Either "user_id" or "username"
- `search_value`: The value to search for

**Returns:** User dictionary with profile data

**Raises:**
- `UserNotFoundError` - If user doesn't exist
- `ValidationError` - If search parameters are invalid

#### `get_user_activities(user_id: int) -> List[Dict]`
Get all activities for a specific user (both owned and joined).

**Returns:** List of activity dictionaries

#### `get_user_activity_messages(user_id: int) -> Dict[int, List[Dict]]`
Get recent messages for user's activities.

**Returns:** Dictionary mapping activity_id to list of messages

#### `ban_user(user_id: int, reason: str) -> bool`
Ban a user from the platform.

**Parameters:**
- `user_id`: User ID to ban
- `reason`: Reason for ban (min 5 characters)

**Returns:** True if successful

**Audit:** Logs `USER_BAN` action

---

## ModerationService

**Location**: `src/services/moderation_service.py`

Handles user moderation actions, reports, and feedback management.

### Methods

#### `get_reported_users() -> List[Dict]`
Get all reported users with report details.

**Returns:** List of reported users with reporter information

#### `get_feedback(status: str = None, limit: int = 50) -> List[Dict]`
Retrieve user feedback with optional status filtering.

**Parameters:**
- `status`: Filter by status ("pending", "resolved", etc.)
- `limit`: Maximum number of results

**Returns:** List of feedback entries

#### `update_feedback_status(feedback_id: int, status: str) -> bool`
Update the status of a feedback entry.

**Audit:** Logs `FEEDBACK_STATUS_UPDATE` action

#### `delete_user(user_id: int, reason: str) -> bool`
Permanently delete a user and their data.

**Warning:** This is a destructive operation that:
- Moves user to deleted_users table
- Removes user from all activities
- Deletes user's messages
- Cannot be undone

**Audit:** Logs `USER_DELETE` action

---

## ChatModerationService

**Location**: `src/services/chat_moderation_service.py`

Monitors and moderates chat messages (both activity chats and direct messages).

### Methods

#### `get_chat_stats() -> Dict`
Get overall chat statistics.

**Returns:**
```python
{
    "total_activity_chats": int,
    "total_individual_chats": int,
    "total_activity_messages": int,
    "total_individual_messages": int,
    "total_chats": int,
    "total_messages": int
}
```

#### `get_activity_chats(limit: int, offset: int, search: str) -> List[Dict]`
Get activity group chats with metadata.

**Parameters:**
- `limit`: Max results to return
- `offset`: Pagination offset
- `search`: Search in activity names, messages, or senders

**Returns:** List of chat metadata with member/message counts

#### `get_individual_chats(limit: int, offset: int, search: str) -> List[Dict]`
Get direct message chats between users.

**Returns:** List of DM chats with participant info

#### `get_chat_messages(chat_id: int, chat_type: str) -> List[Dict]`
Get all messages for a specific chat.

**Parameters:**
- `chat_id`: Chat identifier
- `chat_type`: Either "activity" or "individual"

**Returns:** Chronological list of messages with sender info

#### `search_messages(keyword: str, limit: int) -> List[Dict]`
Search all messages by keyword.

**Parameters:**
- `keyword`: Search term (min 2 characters)
- `limit`: Max results

**Returns:** List of matching messages from both chat types

#### `flag_message(message_id: int, chat_type: str, reason: str) -> bool`
Flag a message as inappropriate and mark as deleted.

**Audit:** Logs `MESSAGE_FLAGGED` action

---

## CommunityForumService

**Location**: `src/services/community_forum_service.py`

Manages community forum threads, replies, and moderation.

### Methods

#### `get_forum_stats() -> Dict`
Get forum-wide statistics.

**Returns:**
```python
{
    "total_communities": int,
    "total_threads": int,
    "total_replies": int,
    "total_posts": int,
    "reported_threads": int,
    "reported_replies": int,
    "total_reported": int,
    "total_members": int
}
```

#### `get_threads(limit: int, offset: int, community_id: int, search: str, reported_only: bool) -> List[Dict]`
Get forum threads with filters.

**Parameters:**
- `limit`: Max results
- `offset`: Pagination offset
- `community_id`: Filter by community (optional)
- `search`: Search in titles/body
- `reported_only`: Show only reported threads

**Returns:** List of threads with reply/upvote counts

#### `get_thread_replies(thread_id: int) -> List[Dict]`
Get all replies for a thread.

**Returns:** List of replies with author info and upvote counts

#### `get_reported_content() -> Dict`
Get all reported threads and replies.

**Returns:**
```python
{
    "threads": List[Dict],
    "replies": List[Dict]
}
```

#### `search_forum_content(keyword: str, limit: int) -> List[Dict]`
Search threads and replies by keyword.

**Returns:** Combined list of matching threads and replies

#### `delete_thread(thread_id: int, reason: str) -> bool`
Delete a thread and all its replies.

**Warning:** Cascade deletes:
- All replies to the thread
- All upvotes on thread and replies

**Audit:** Logs `THREAD_DELETED` action

#### `delete_reply(reply_id: int, reason: str) -> bool`
Delete a single reply.

**Audit:** Logs `REPLY_DELETED` action

#### `get_community_members(community_id: int) -> List[Dict]`
Get all members of a community.

**Returns:** List of members with last visited timestamp

---

## AnalyticsService

**Location**: `src/services/analytics_service.py`

Provides platform analytics and statistics.

### Methods

#### `get_user_statistics() -> Dict`
Get user-related statistics.

**Returns:**
```python
{
    "total_users": int,
    "active_users": int,
    "new_users_today": int,
    "verified_users": int
}
```

#### `get_activity_statistics() -> Dict`
Get activity-related statistics.

**Returns:**
```python
{
    "total_activities": int,
    "upcoming_activities": int,
    "full_activities": int
}
```

#### `get_message_statistics() -> Dict`
Get messaging statistics.

**Returns:**
```python
{
    "total_messages": int,
    "total_chats": int,
    "messages_today": int
}
```

---

## NotificationService

**Location**: `src/services/notification_service.py`

Handles bulk push notifications to users.

### Methods

#### `get_recipient_count(filters: Dict) -> int`
Count how many users match the notification filters.

**Filter Options:**
- `language`: List of language codes ["en", "nl", "fr"]
- `reg_complete`: Boolean - only complete registrations
- `min_user_id`: Integer - minimum user ID
- `max_user_id`: Integer - maximum user ID

**Returns:** Number of matching users with notification tokens

#### `send_bulk_notification(title: str, body: str, data: Dict, filters: Dict) -> Dict`
Send push notifications to filtered users.

**Parameters:**
- `title`: Notification title
- `body`: Notification message
- `data`: Custom data payload
- `filters`: User filters (see above)

**Returns:**
```python
{
    "sent": int,      # Successfully sent
    "failed": int     # Failed to send
}
```

**Audit:** Logs `BULK_NOTIFICATION_SENT` action

---

## ActivityTypeService

**Location**: `src/services/activity_type_service.py`

Manages activity type categories and subtypes.

### Methods

#### `get_all_activity_types() -> List[Dict]`
Get all activity types with translations.

**Returns:** List with fields: id, type, subtype, subtype_nl, subtype_fr, subtype_code, img_url, emoji

#### `add_activity_type(...) -> bool`
Add a new activity type.

**Parameters:**
- `type_name`: Category name (e.g., "Sports")
- `subtype`: English name (e.g., "Tennis")
- `subtype_nl`: Dutch translation
- `subtype_fr`: French translation
- `subtype_code`: Unique integer code
- `img_url`: Image URL
- `emoji`: Emoji icon

**Audit:** Logs `ADD_ACTIVITY_TYPE` action

#### `update_activity_type(type_id: int, ...) -> bool`
Update an existing activity type.

**Audit:** Logs `UPDATE_ACTIVITY_TYPE` action

#### `delete_activity_type(type_id: int) -> bool`
Delete an activity type.

**Audit:** Logs `DELETE_ACTIVITY_TYPE` action

---

## VenueService

**Location**: `src/services/venue_service.py`

Manages venue/location listings.

### Methods

#### `get_all_venues() -> List[Dict]`
Get all venues with activity type information.

**Returns:** List of venues with subtype names

#### `add_venue(...) -> bool`
Add a new venue.

**Parameters:**
- `name`: Venue name
- `subtype_id`: Link to activity type
- `keywords`: Search keywords
- `address`: Physical address
- `img_url`: Venue image
- `url`: Venue website
- `location`: Location string

**Audit:** Logs `ADD_VENUE` action

#### `update_venue(venue_id: int, ...) -> bool`
Update venue information.

**Audit:** Logs `UPDATE_VENUE` action

#### `delete_venue(venue_id: int) -> bool`
Delete a venue.

**Audit:** Logs `DELETE_VENUE` action

---

## CommunityService

**Location**: `src/services/community_service.py`

Manages community groups.

### Methods

#### `get_all_communities() -> List[Dict]`
Get all communities.

**Returns:** List with fields: id, name, description, img_url, location, is_starter

#### `add_community(...) -> bool`
Create a new community.

**Parameters:**
- `name`: Community name
- `description`: Community description
- `img_url`: Community image
- `location`: Geographic location (WKT format)
- `is_starter`: Boolean - starter community flag

**Note:** Uses spatial query ST_GeomFromText for location

**Audit:** Logs `ADD_COMMUNITY` action

#### `update_community(community_id: int, ...) -> bool`
Update community information.

**Audit:** Logs `UPDATE_COMMUNITY` action

#### `delete_community(community_id: int) -> bool`
Delete a community and all memberships.

**Warning:** Cascade deletes all community_membership records

**Audit:** Logs `DELETE_COMMUNITY` action

---

## ConvertKitService

**Location**: `src/services/convertkit_service.py`

Integrates with ConvertKit email marketing platform.

### Methods

#### `get_subscriber_count() -> int`
Get total subscribers from ConvertKit.

**Returns:** Number of subscribers

#### `sync_user_to_convertkit(user_email: str, user_name: str) -> bool`
Add a single user to ConvertKit.

**Parameters:**
- `user_email`: User's email address
- `user_name`: User's name

**Returns:** True if successful

#### `bulk_sync_users(limit: int) -> Dict`
Sync multiple users to ConvertKit.

**Parameters:**
- `limit`: Maximum users to sync

**Returns:**
```python
{
    "synced": int,
    "failed": int,
    "skipped": int
}
```

**Audit:** Logs `CONVERTKIT_BULK_SYNC` action

---

## Error Handling

All service methods use the `@ErrorHandler.handle_database_error` decorator which:

1. Catches exceptions
2. Logs errors
3. Raises appropriate custom exceptions:
   - `DatabaseError` - Database connection/query issues
   - `ValidationError` - Invalid input parameters
   - `UserNotFoundError` - User doesn't exist
   - `DashboardException` - General application errors

## Audit Logging

Critical actions are decorated with `@audit_log("ACTION_TYPE")` which:

1. Logs to `audit_log.json`
2. Records timestamp
3. Records action type
4. Records action details
5. Can be reviewed for compliance

## Usage Examples

### Example 1: Search and Ban User

```python
from services.user_service import UserService

user_service = UserService()

# Find user
user = user_service.get_user("username", "john_doe")

# Ban user
user_service.ban_user(user['id'], "Spam posting")
```

### Example 2: Moderate Forum Content

```python
from services.community_forum_service import CommunityForumService

forum_service = CommunityForumService()

# Get reported content
reported = forum_service.get_reported_content()

# Delete inappropriate thread
for thread in reported['threads']:
    forum_service.delete_thread(thread['id'], "Inappropriate content")
```

### Example 3: Send Notifications

```python
from services.notification_service import NotificationService

notif_service = NotificationService()

# Check recipient count
filters = {"language": ["en"], "reg_complete": True}
count = notif_service.get_recipient_count(filters)

# Send notification
result = notif_service.send_bulk_notification(
    title="Welcome",
    body="Thanks for joining!",
    data={},
    filters=filters
)
print(f"Sent: {result['sent']}, Failed: {result['failed']}")
```

---

## Best Practices

1. **Always use context managers** for database sessions:
   ```python
   with service.get_db_session() as db:
       # Your queries here
   ```

2. **Handle exceptions properly**:
   ```python
   try:
       result = service.some_method()
   except ValidationError as e:
       # Handle validation error
   except DatabaseError as e:
       # Handle database error
   ```

3. **Provide reasons for moderation actions**:
   ```python
   # Good
   service.delete_thread(id, "Contains spam links")

   # Bad
   service.delete_thread(id, "bad")
   ```

4. **Check audit logs regularly**:
   ```bash
   tail -f audit_log.json
   ```

5. **Use filters wisely** to avoid overloading:
   ```python
   # Good - use pagination
   threads = service.get_threads(limit=50, offset=0)

   # Bad - requesting too much
   threads = service.get_threads(limit=10000)
   ```

---

For UI usage examples, see the tab implementations in `src/ui/tabs/`.

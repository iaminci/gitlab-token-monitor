# GitLab Token Expiration Monitor

A comprehensive monitoring system for GitLab access tokens (Personal, Project, and Group tokens) with email notifications.

## 🏗️ Project Structure

```
gitlab_token_monitor/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── gitlab_api.py        # GitLab API client
├── token_analyzer.py    # Token analysis logic
├── email_reporter.py    # Email notification system
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Quick Setup

### 1. Create Project Directory and Files

```bash
mkdir gitlab_token_monitor
cd gitlab_token_monitor
```

Create the following files with the provided code:

- `main.py`
- `config.py`
- `gitlab_api.py`
- `token_analyzer.py`
- `email_reporter.py`
- `requirements.txt`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

**Required Variables:**

```bash
export GITLAB_URL="https://your-gitlab.com"
export GITLAB_ADMIN_TOKEN="your-admin-token-here"
export FROM_EMAIL="alerts@yourcompany.com"
export TO_EMAILS="admin1@company.com,admin2@company.com"
```

**SMTP Configuration:**

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USERNAME="your-smtp-username"
export SMTP_PASSWORD="your-smtp-password"
export SMTP_USE_SSL="true"
export SMTP_USE_TLS="false"
```

**Optional Configuration:**

```bash
export DAYS_THRESHOLD="7"              # Days before expiration to alert
export INCLUDE_PROJECT_TOKENS="true"   # Monitor project tokens
export INCLUDE_GROUP_TOKENS="true"     # Monitor group tokens
export SEND_ALL_TOKENS="false"         # Send reports only when problems exist
```

### 4. Create GitLab Admin Token

1. Go to GitLab → Admin Area → Overview → Users → Select your admin user
2. Go to Access Tokens tab
3. Create a personal access token with `api` scope
4. Copy the token and set it as `GITLAB_ADMIN_TOKEN`

### 5. Run the Monitor

```bash
python main.py
```

## 📧 Email Report Features

The system generates comprehensive HTML email reports with:

### Executive Summary

- **Dashboard view** with token statistics
- **Color-coded status indicators**
- **Total count breakdown** by category

### Critical Alerts Section

- **🔴 Expired tokens** (require immediate action)
- **🟠 Expiring soon** (within threshold days)
- **Complete token details** with user/project/group info

### Collapsible Sections

- **✅ Healthy tokens** (expires beyond threshold)
- **♾️ Permanent tokens** (no expiration date)
- **Click to expand/collapse** for better readability

### Token Information Included

- **Personal tokens:** User, email, scopes, expiration
- **Project tokens:** Project name, path, access level
- **Group tokens:** Group name, path, scopes, access level

## 🔄 Automation Options

### Option 1: Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily monitoring at 9 AM
0 9 * * * cd /path/to/gitlab_token_monitor && /usr/bin/python3 main.py
```

### Option 2: GitLab CI/CD Pipeline

Create `.gitlab-ci.yml`:

```yaml
token-monitoring:
  image: python:3.9
  before_script:
    - pip install -r requirements.txt
  script:
    - python main.py
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  variables:
    GITLAB_URL: "https://your-gitlab.com"
    # Add other environment variables in GitLab CI/CD settings
```

### Option 3: Docker Container

```dockerfile
FROM python:3.9-slim
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t gitlab-token-monitor .
docker run --env-file .env gitlab-token-monitor
```

## 🔧 Configuration Options

### Report Modes

**Problem-Only Mode (Default):**

```bash
export SEND_ALL_TOKENS="false"
# Only sends emails when tokens are expired/expiring
```

**Comprehensive Reports:**

```bash
export SEND_ALL_TOKENS="true"
# Always sends complete token inventory
```

### Token Type Selection

```bash
export INCLUDE_PROJECT_TOKENS="true"   # Include project access tokens
export INCLUDE_GROUP_TOKENS="true"     # Include group access tokens
export INCLUDE_PROJECT_TOKENS="false"  # Skip project tokens
```

### Threshold Configuration

```bash
export DAYS_THRESHOLD="14"  # Alert 14 days before expiration
export DAYS_THRESHOLD="3"   # Alert 3 days before expiration
```

## 📊 Sample Output

```
Starting GitLab token expiration monitoring...
Checking for tokens expiring within 7 days
Report mode: Only problematic tokens

Fetching personal access tokens...
Personal Access Tokens: 25 total, 2 expired, 5 expiring soon, 15 healthy, 3 permanent

Fetching project access tokens...
Project Access Tokens: 12 total, 0 expired, 1 expiring soon, 10 healthy, 1 permanent

Fetching group access tokens...
Group Access Tokens: 6 total, 1 expired, 0 expiring soon, 4 healthy, 1 permanent

=== SUMMARY ===
Total tokens: 43
Expired: 3
Expiring soon: 6
Healthy: 29
Permanent: 5

Sending email report...
Email notification sent successfully to admin@company.com
Monitoring complete!
```

## 🛠️ Common SMTP Configurations

### Gmail

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USE_SSL="true"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"  # Use app password, not account password
```

### Outlook/Office 365

```bash
export SMTP_SERVER="smtp-mail.outlook.com"
export SMTP_PORT="587"
export SMTP_USE_SSL="false"
export SMTP_USE_TLS="true"
```

### Custom SMTP Server

```bash
export SMTP_SERVER="mail.yourcompany.com"
export SMTP_PORT="465"
export SMTP_USE_SSL="true"
export SMTP_USERNAME="alerts@yourcompany.com"
export SMTP_PASSWORD="your-password"
```

## 🔍 Troubleshooting

### Common Issues

**"Error: GITLAB_ADMIN_TOKEN environment variable is required"**

- Set the `GITLAB_ADMIN_TOKEN` environment variable
- Ensure the token has `api` scope

**"Error fetching personal access tokens: 401"**

- Check if your admin token is valid
- Verify the token has sufficient permissions

**"Error sending email: Authentication failed"**

- For Gmail: Use app passwords instead of account passwords
- Check SMTP credentials and server settings
- Verify SSL/TLS configuration

**"No tokens found"**

- Check if your GitLab instance has access tokens
- Verify admin token has access to view all tokens

### Debug Mode

Add debug output by modifying the scripts to include more verbose logging.

## 📋 Features Summary

✅ **Complete Token Coverage:** Personal, Project, and Group access tokens  
✅ **Smart Analysis:** Categorizes tokens by expiration status  
✅ **Rich Email Reports:** HTML reports with executive summaries  
✅ **Flexible Configuration:** Environment-based settings  
✅ **Multiple Notification Modes:** Problem-only or comprehensive reports  
✅ **Automation Ready:** Cron, CI/CD, and Docker support  
✅ **Detailed Token Info:** User details, project paths, scopes, access levels  
✅ **Error Handling:** Robust error handling and logging

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

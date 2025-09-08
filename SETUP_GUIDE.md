# Google Apps Script API Setup Guide

This guide will help you set up the necessary credentials to use Module 2 (Google Apps Script Deployment & Execution).

## Prerequisites

- Google account with access to Google Workspace
- Google Cloud Console access
- Python environment with required packages

## Step 1: Enable Google Apps Script API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Library**
4. Search for "Google Apps Script API" and enable it
5. Also enable "Google Forms API" and "Google Drive API"

## Step 2: Create Credentials

### Option A: OAuth2 Credentials (Recommended for testing)

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Choose **Desktop application**
4. Name it "AI Quiz Generator"
5. Download the JSON file and save it as `credentials.json` in your project directory

### Option B: Service Account (For production/automated use)

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **Service account**
3. Fill in service account details
4. Grant necessary roles (Editor or custom roles with Apps Script permissions)
5. Create and download the JSON key file
6. Save it as `credentials.json` in your project directory

## Step 3: Install Dependencies

```bash
# Install required packages
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Or install from requirements.txt
pip install -r requirements.txt
```

## Step 4: Test Authentication

```python
from gas_deployer import GoogleAppsScriptDeployer

# Initialize deployer
deployer = GoogleAppsScriptDeployer()

# Test authentication
if deployer.authenticate_google():
    print("✓ Authentication successful!")
else:
    print("✗ Authentication failed")
```

## Step 5: Complete Workflow Example

```python
from quiz_generator import QuestionGenerator, QuizConfig
from gas_deployer import GoogleAppsScriptDeployer

# Generate quiz script
config = QuizConfig(title="My AI Quiz", question_count=10)
generator = QuestionGenerator(config)
script_content = generator.generate_quiz_from_json("l0/m1.json", "generated_quiz.gs")

# Deploy to Google Apps Script
deployer = GoogleAppsScriptDeployer()
if deployer.authenticate_google():
    published_url, edit_url = deployer.deploy_and_execute_quiz(script_content)

    if published_url:
        print(f"Quiz created! Share this URL: {published_url}")
    else:
        print("Failed to create quiz")
```

## Troubleshooting

### Common Issues:

1. **"Access blocked" error**: Make sure your OAuth consent screen is configured
2. **"Insufficient permissions"**: Verify all required APIs are enabled
3. **"Invalid credentials"**: Check that credentials.json is in the correct location
4. **"Quota exceeded"**: Check your API usage limits in Google Cloud Console

### Required Scopes:

- `https://www.googleapis.com/auth/script.projects`
- `https://www.googleapis.com/auth/script.deployments`
- `https://www.googleapis.com/auth/forms`
- `https://www.googleapis.com/auth/drive`

## Security Notes

- Keep your `credentials.json` file secure and never commit it to version control
- Add `credentials.json` and `token.json` to your `.gitignore` file
- For production use, consider using service accounts with minimal required permissions
- Regularly rotate your API keys and credentials

## Next Steps

Once authentication is working, you can proceed to Module 3 (Email Notification System) to complete the full workflow.

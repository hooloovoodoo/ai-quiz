# AI Quiz System

A complete automated system for creating Google Forms quizzes with AI questions and sending email notifications to recipients.

## Overview

This system consists of three modular components:

1. **Quiz Generator** (`quiz_generator.py`) - Loads questions from JSON, generates Google Apps Script code
2. **Google Apps Script Deployer** (`gas_deployer.py`) - Deploys scripts to Google Apps Script and creates forms
3. **Email Notifier** (`email_notifier.py`) - Sends professional HTML email notifications

## Features

- ✅ **30 AI Knowledge Questions** - Comprehensive question database covering AI fundamentals
- ✅ **Randomized Questions** - Selects random subset and shuffles answer choices
- ✅ **Automated Deployment** - Creates Google Forms automatically via API
- ✅ **Professional Emails** - Beautiful HTML email templates with responsive design
- ✅ **Flexible Configuration** - JSON config files and command-line options
- ✅ **Error Handling** - Comprehensive logging and error recovery
- ✅ **Batch Processing** - Send to multiple recipients simultaneously

## Quick Start

### 1. Setup Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Google API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Apps Script API, Forms API, and Drive API
3. Create OAuth2 credentials and download as `credentials.json`
4. See `SETUP_GUIDE.md` for detailed instructions

### 3. Test Quiz Generation

```bash
# Generate quiz script only (no deployment)
python main.py --dry-run --questions l0/m1.json --count 10
```

### 4. Complete Workflow

```bash
# Deploy quiz and send emails
python main.py \
  --questions l0/m1.json \
  --recipients recipients.txt \
  --count 10 \
  --title "AI Knowledge Assessment" \
  --sender-email your-email@gmail.com \
  --sender-password your-app-password
```

## Usage Examples

### Command Line Interface

```bash
# Basic usage with recipients file
python main.py --questions l0/m1.json --recipients recipients.txt --count 10

# Specify individual email addresses
python main.py --questions l0/m1.json --emails user1@example.com user2@example.com

# Use configuration file
python main.py --config config.json

# Generate quiz without sending emails
python main.py --questions l0/m1.json --no-email --count 5

# Verbose logging
python main.py --config config.json --verbose
```

### Configuration File

Create `config.json`:

```json
{
  "quiz": {
    "title": "AI Knowledge Quiz",
    "question_count": 10,
    "points_per_question": 5
  },
  "email": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "sender_name": "AI Quiz Team"
  },
  "questions_file": "l0/m1.json",
  "recipients_file": "recipients.txt",
  "deadline": "Friday, December 15th at 5:00 PM"
}
```

### Python API

```python
from quiz_generator import QuestionGenerator, QuizConfig
from gas_deployer import GoogleAppsScriptDeployer
from email_notifier import EmailNotifier, EmailConfig

# Configure quiz
config = QuizConfig(
    title="Advanced AI Quiz",
    question_count=15,
    points_per_question=10
)

# Generate quiz script
generator = QuestionGenerator(config)
script_content = generator.generate_quiz_from_json(
    "l0/m1.json", 
    "my_quiz.gs"
)

# Deploy to Google Apps Script
deployer = GoogleAppsScriptDeployer()
if deployer.authenticate_google():
    published_url, edit_url = deployer.deploy_and_execute_quiz(script_content)

# Send email notifications
email_config = EmailConfig(
    sender_email="your-email@gmail.com",
    sender_password="your-app-password"
)

notifier = EmailNotifier(email_config)
notifier.setup_email_client()
results = notifier.send_quiz_notification(
    recipients=["user@example.com"],
    quiz_url=published_url,
    question_count=15
)
```

## File Structure

```
ai-quiz/
├── main.py                 # Main orchestrator script
├── quiz_generator.py       # Module 1: Question generator
├── gas_deployer.py         # Module 2: Google Apps Script deployer
├── email_notifier.py       # Module 3: Email notification system
├── l0/m1.json             # Question database (30 AI questions)
├── config.json            # Sample configuration file
├── recipients.txt         # Sample recipients file
├── requirements.txt       # Python dependencies
├── SETUP_GUIDE.md         # Google API setup instructions
└── README.md              # This file
```

## Question Database

The system includes 30 comprehensive AI knowledge questions covering:

- **AI Fundamentals** - ANI, AGI, AI vs ML vs DL relationships
- **Machine Learning** - Supervised/unsupervised learning, training vs inference
- **Deep Learning** - Neural networks, layers, pattern recognition
- **Generative AI** - LLMs, prompt engineering, context windows
- **AI Ethics** - Bias, hallucinations, explainability
- **Practical AI** - Data quality, GIGO principle, real-world applications

## Email Templates

Professional HTML email templates include:

- 🤖 **Modern Design** - Clean, responsive layout with AI theme
- 📱 **Mobile Friendly** - Optimized for all device sizes
- 🎨 **Branded Styling** - Consistent color scheme and typography
- 🔗 **Clear Call-to-Action** - Prominent "Start Quiz" button
- 📋 **Quiz Details** - Question count, scoring, deadline information
- 🔧 **Fallback Support** - Plain text version for compatibility

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--config` | JSON configuration file | `--config config.json` |
| `--questions` | Questions JSON file | `--questions l0/m1.json` |
| `--recipients` | Recipients file (one email per line) | `--recipients emails.txt` |
| `--emails` | Individual email addresses | `--emails user1@example.com user2@example.com` |
| `--count` | Number of questions to include | `--count 10` |
| `--title` | Quiz title | `--title "AI Assessment"` |
| `--deadline` | Quiz deadline (free text) | `--deadline "Friday 5PM"` |
| `--sender-email` | Sender email address | `--sender-email quiz@company.com` |
| `--sender-password` | Email password/app password | `--sender-password mypassword` |
| `--dry-run` | Generate quiz script only | `--dry-run` |
| `--no-email` | Deploy quiz but skip emails | `--no-email` |
| `--verbose` | Enable verbose logging | `--verbose` |

## Environment Variables

You can use environment variables instead of command line options:

```bash
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"

python main.py --questions l0/m1.json --recipients recipients.txt
```

## Security Best Practices

- ✅ **Credentials Protection** - Never commit `credentials.json` to version control
- ✅ **App Passwords** - Use Gmail app passwords instead of account passwords
- ✅ **Environment Variables** - Store sensitive data in environment variables
- ✅ **Minimal Permissions** - Use service accounts with minimal required scopes
- ✅ **Token Management** - OAuth tokens are automatically refreshed

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Verify `credentials.json` exists and is valid
- Check that required APIs are enabled in Google Cloud Console
- Ensure OAuth consent screen is configured

**"No module named 'yagmail'"**
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`

**"SMTP authentication error"**
- Use Gmail app passwords instead of account password
- Enable 2-factor authentication on Gmail account
- Check SMTP server and port settings

**"Questions file not found"**
- Verify file path is correct: `l0/m1.json`
- Check file exists and contains valid JSON

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
python main.py --config config.json --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:

1. Check the troubleshooting section above
2. Review `SETUP_GUIDE.md` for Google API setup
3. Open an issue on GitHub with detailed error messages

---

**Created by**: AI Quiz System  
**Version**: 1.0.0  
**Last Updated**: August 2025

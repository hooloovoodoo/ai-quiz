"""
Email Notification System Module

This module handles:
1. Email configuration and SMTP setup
2. HTML email template generation
3. Sending quiz notifications to recipients
4. Delivery status tracking
5. Batch email processing
6. Professional email formatting
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import yagmail
    YAGMAIL_AVAILABLE = True
except ImportError:
    YAGMAIL_AVAILABLE = False
    logger.warning("yagmail not available, will use smtplib only")

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logger.warning("jinja2 not available, will use basic string formatting")


class EmailConfig:
    """Configuration class for email settings"""
    
    def __init__(self,
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: str = "",
                 sender_password: str = "",
                 sender_name: str = "AI Quiz System",
                 use_yagmail: bool = True,
                 use_tls: bool = True):
        
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.sender_name = sender_name
        self.use_yagmail = use_yagmail
        self.use_tls = use_tls
        
    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Create configuration from environment variables"""
        return cls(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            sender_email=os.getenv('SENDER_EMAIL', ''),
            sender_password=os.getenv('SENDER_PASSWORD', ''),
            sender_name=os.getenv('SENDER_NAME', 'AI Quiz System'),
            use_yagmail=os.getenv('USE_YAGMAIL', 'true').lower() == 'true',
            use_tls=os.getenv('USE_TLS', 'true').lower() == 'true'
        )


class EmailNotifier:
    """Main class for sending quiz notification emails"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        """
        Initialize email notifier with configuration
        
        Args:
            config: Email configuration object
        """
        self.config = config or EmailConfig.from_env()
        self.yag_client = None
        self.smtp_client = None
        self.delivery_log = []
        
    def setup_email_client(self) -> bool:
        """
        Setup email client (yagmail or smtplib)
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            if not self.config.sender_email or not self.config.sender_password:
                logger.error("Email credentials not provided")
                return False
                
            if self.config.use_yagmail and YAGMAIL_AVAILABLE:
                self.yag_client = yagmail.SMTP(
                    user=self.config.sender_email,
                    password=self.config.sender_password,
                    host=self.config.smtp_server,
                    port=self.config.smtp_port
                )
                logger.info("Yagmail client setup successful")
            elif self.config.use_yagmail and not YAGMAIL_AVAILABLE:
                logger.warning("Yagmail requested but not available, falling back to SMTP")
                self.config.use_yagmail = False
            else:
                # Setup will be done per-send for smtplib
                logger.info("SMTP client will be setup per-send")
                
            return True
            
        except Exception as e:
            logger.error(f"Error setting up email client: {e}")
            return False
            
    def _get_html_template(self) -> str:
        """
        Get HTML email template
        
        Returns:
            HTML template string
        """
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Knowledge Quiz Invitation</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #4CAF50;
        }
        .header h1 {
            color: #4CAF50;
            margin: 0;
            font-size: 28px;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
            font-size: 16px;
        }
        .content {
            margin-bottom: 30px;
        }
        .quiz-info {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }
        .quiz-info h3 {
            margin-top: 0;
            color: #333;
        }
        .quiz-info ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .quiz-info li {
            margin: 5px 0;
        }
        .cta-button {
            display: inline-block;
            background-color: #4CAF50;
            color: white !important;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 18px;
            margin: 20px 0;
            text-align: center;
            transition: background-color 0.3s;
        }
        .cta-button:hover {
            background-color: #45a049;
        }
        .cta-container {
            text-align: center;
            margin: 30px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }
        .url-fallback {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .container {
                padding: 20px;
            }
            .header h1 {
                font-size: 24px;
            }
            .cta-button {
                display: block;
                margin: 20px auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Knowledge Quiz</h1>
            <p>Test Your Artificial Intelligence Knowledge</p>
        </div>
        
        <div class="content">
            <p>Hello{{ ' ' + recipient_name if recipient_name else '' }},</p>
            
            <p>You've been invited to take an <strong>AI Knowledge Quiz</strong>! This quiz is designed to test your understanding of artificial intelligence concepts, from basic terminology to advanced topics.</p>
            
            <div class="quiz-info">
                <h3>📋 Quiz Details:</h3>
                <ul>
                    <li><strong>Questions:</strong> {{ question_count }} multiple-choice questions</li>
                    <li><strong>Topics:</strong> AI fundamentals, machine learning, deep learning, and more</li>
                    <li><strong>Time:</strong> No time limit - take your time to think</li>
                    <li><strong>Scoring:</strong> {{ points_per_question }} points per correct answer</li>
                    <li><strong>Format:</strong> Multiple choice with immediate feedback</li>
                </ul>
            </div>
            
            <p>Click the button below to start the quiz:</p>
            
            <div class="cta-container">
                <a href="{{ quiz_url }}" class="cta-button">🚀 Start Quiz Now</a>
            </div>
            
            <p><strong>Can't click the button?</strong> Copy and paste this link into your browser:</p>
            <div class="url-fallback">{{ quiz_url }}</div>
            
            {% if deadline %}
            <p><strong>⏰ Deadline:</strong> Please complete the quiz by {{ deadline }}</p>
            {% endif %}
            
            <p>Good luck, and enjoy testing your AI knowledge!</p>
        </div>
        
        <div class="footer">
            <p>This quiz was automatically generated by the AI Quiz System</p>
            <p>Generated on {{ current_date }}</p>
            {% if edit_url %}
            <p style="font-size: 12px; color: #999;">
                <em>Quiz administrators can edit this quiz <a href="{{ edit_url }}">here</a></em>
            </p>
            {% endif %}
        </div>
    </div>
</body>
</html>
        """
        
    def _get_text_template(self) -> str:
        """
        Get plain text email template (fallback)
        
        Returns:
            Plain text template string
        """
        return """
AI KNOWLEDGE QUIZ INVITATION
============================

Hello{{ ' ' + recipient_name if recipient_name else '' }},

You've been invited to take an AI Knowledge Quiz!

Quiz Details:
- Questions: {{ question_count }} multiple-choice questions
- Topics: AI fundamentals, machine learning, deep learning, and more
- Time: No time limit - take your time to think
- Scoring: {{ points_per_question }} points per correct answer
- Format: Multiple choice with immediate feedback

Quiz URL: {{ quiz_url }}

{% if deadline %}
Deadline: Please complete the quiz by {{ deadline }}
{% endif %}

Good luck, and enjoy testing your AI knowledge!

---
This quiz was automatically generated by the AI Quiz System
Generated on {{ current_date }}
{% if edit_url %}
Quiz administrators can edit this quiz at: {{ edit_url }}
{% endif %}
        """
        
    def generate_email_content(self, 
                             quiz_url: str,
                             recipient_name: str = "",
                             question_count: int = 10,
                             points_per_question: int = 5,
                             deadline: Optional[str] = None,
                             edit_url: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate personalized email content
        
        Args:
            quiz_url: URL to the Google Form quiz
            recipient_name: Name of the recipient (optional)
            question_count: Number of questions in the quiz
            points_per_question: Points per correct answer
            deadline: Optional deadline string
            edit_url: Optional edit URL for administrators
            
        Returns:
            Tuple of (html_content, text_content)
        """
        try:
            current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            
            template_vars = {
                'recipient_name': recipient_name,
                'quiz_url': quiz_url,
                'question_count': question_count,
                'points_per_question': points_per_question,
                'deadline': deadline,
                'edit_url': edit_url,
                'current_date': current_date
            }
            
            # Generate HTML content
            if JINJA2_AVAILABLE:
                html_template = Template(self._get_html_template())
                html_content = html_template.render(**template_vars)
                
                # Generate text content
                text_template = Template(self._get_text_template())
                text_content = text_template.render(**template_vars)
            else:
                # Fallback to basic string formatting
                html_content = self._get_html_template_basic(**template_vars)
                text_content = self._get_text_template_basic(**template_vars)
            
            return html_content, text_content
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return "", ""
            
    def _get_html_template_basic(self, **kwargs) -> str:
        """Basic HTML template without Jinja2"""
        name_greeting = f" {kwargs['recipient_name']}" if kwargs.get('recipient_name') else ""
        deadline_text = f"<p><strong>⏰ Deadline:</strong> Please complete the quiz by {kwargs['deadline']}</p>" if kwargs.get('deadline') else ""
        edit_link = f"<p style='font-size: 12px; color: #999;'><em>Quiz administrators can edit this quiz <a href='{kwargs['edit_url']}'>here</a></em></p>" if kwargs.get('edit_url') else ""
        
        return f"""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>AI Knowledge Quiz Invitation</title></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1);">
<h1 style="color: #4CAF50; text-align: center;">🤖 AI Knowledge Quiz</h1>
<p>Hello{name_greeting},</p>
<p>You've been invited to take an <strong>AI Knowledge Quiz</strong>!</p>
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
<h3>📋 Quiz Details:</h3>
<ul>
<li><strong>Questions:</strong> {kwargs['question_count']} multiple-choice questions</li>
<li><strong>Scoring:</strong> {kwargs['points_per_question']} points per correct answer</li>
</ul>
</div>
<div style="text-align: center; margin: 30px 0;">
<a href="{kwargs['quiz_url']}" style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">🚀 Start Quiz Now</a>
</div>
<p><strong>Can't click the button?</strong> Copy this link: {kwargs['quiz_url']}</p>
{deadline_text}
<p>Good luck!</p>
<div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
<p>Generated on {kwargs['current_date']}</p>
{edit_link}
</div>
</div>
</body></html>
        """
        
    def _get_text_template_basic(self, **kwargs) -> str:
        """Basic text template without Jinja2"""
        name_greeting = f" {kwargs['recipient_name']}" if kwargs.get('recipient_name') else ""
        deadline_text = f"\nDeadline: Please complete the quiz by {kwargs['deadline']}" if kwargs.get('deadline') else ""
        edit_text = f"\nQuiz administrators can edit this quiz at: {kwargs['edit_url']}" if kwargs.get('edit_url') else ""
        
        return f"""
AI KNOWLEDGE QUIZ INVITATION
============================

Hello{name_greeting},

You've been invited to take an AI Knowledge Quiz!

Quiz Details:
- Questions: {kwargs['question_count']} multiple-choice questions
- Scoring: {kwargs['points_per_question']} points per correct answer

Quiz URL: {kwargs['quiz_url']}{deadline_text}

Good luck!

---
Generated on {kwargs['current_date']}{edit_text}
        """
            
    def send_email_yagmail(self, 
                          to_email: str,
                          subject: str,
                          html_content: str,
                          text_content: str) -> bool:
        """
        Send email using yagmail
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.yag_client:
                logger.error("Yagmail client not initialized")
                return False
                
            self.yag_client.send(
                to=to_email,
                subject=subject,
                contents=[text_content, html_content]
            )
            
            logger.info(f"Email sent successfully to {to_email} via yagmail")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email via yagmail to {to_email}: {e}")
            return False
            
    def send_email_smtp(self,
                       to_email: str,
                       subject: str,
                       html_content: str,
                       text_content: str) -> bool:
        """
        Send email using smtplib
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email via SMTP to {to_email}: {e}")
            return False
            
    def send_quiz_notification(self,
                             recipients: List[str],
                             quiz_url: str,
                             subject: Optional[str] = None,
                             question_count: int = 10,
                             points_per_question: int = 5,
                             deadline: Optional[str] = None,
                             edit_url: Optional[str] = None) -> Dict[str, bool]:
        """
        Send quiz notifications to multiple recipients
        
        Args:
            recipients: List of email addresses
            quiz_url: URL to the Google Form quiz
            subject: Email subject (optional)
            question_count: Number of questions in the quiz
            points_per_question: Points per correct answer
            deadline: Optional deadline string
            edit_url: Optional edit URL for administrators
            
        Returns:
            Dictionary mapping email addresses to success status
        """
        if not recipients:
            logger.warning("No recipients provided")
            return {}
            
        if not quiz_url:
            logger.error("Quiz URL is required")
            return {}
            
        # Default subject
        if not subject:
            subject = f"🤖 AI Knowledge Quiz - {question_count} Questions Await!"
            
        results = {}
        
        for email in recipients:
            try:
                # Extract name from email if possible
                recipient_name = email.split('@')[0].replace('.', ' ').title()
                
                # Generate personalized content
                html_content, text_content = self.generate_email_content(
                    quiz_url=quiz_url,
                    recipient_name=recipient_name,
                    question_count=question_count,
                    points_per_question=points_per_question,
                    deadline=deadline,
                    edit_url=edit_url
                )
                
                if not html_content or not text_content:
                    logger.error(f"Failed to generate content for {email}")
                    results[email] = False
                    continue
                    
                # Send email
                if self.config.use_yagmail and self.yag_client:
                    success = self.send_email_yagmail(email, subject, html_content, text_content)
                else:
                    success = self.send_email_smtp(email, subject, html_content, text_content)
                    
                results[email] = success
                
                # Log delivery
                self.delivery_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'recipient': email,
                    'subject': subject,
                    'success': success,
                    'quiz_url': quiz_url
                })
                
            except Exception as e:
                logger.error(f"Error processing email for {email}: {e}")
                results[email] = False
                
        return results
        
    def get_delivery_status(self) -> List[Dict[str, Any]]:
        """
        Get email delivery status log
        
        Returns:
            List of delivery log entries
        """
        return self.delivery_log.copy()
        
    def save_delivery_log(self, file_path: str) -> bool:
        """
        Save delivery log to file
        
        Args:
            file_path: Path to save the log file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            import json
            with open(file_path, 'w') as f:
                json.dump(self.delivery_log, f, indent=2)
            logger.info(f"Delivery log saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving delivery log: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = EmailConfig(
        sender_email="your-email@gmail.com",
        sender_password="your-app-password",  # Use app password for Gmail
        sender_name="AI Quiz Team"
    )
    
    # Initialize notifier
    notifier = EmailNotifier(config)
    
    print("Email Notification System Test")
    print("=" * 40)
    
    # Test email content generation
    quiz_url = "https://forms.gle/example123"
    html_content, text_content = notifier.generate_email_content(
        quiz_url=quiz_url,
        recipient_name="John Doe",
        question_count=10,
        points_per_question=5
    )
    
    if html_content and text_content:
        print("✓ Email content generation successful")
        print(f"HTML content length: {len(html_content)} characters")
        print(f"Text content length: {len(text_content)} characters")
        
        # Save sample email for preview
        with open("sample_email.html", "w") as f:
            f.write(html_content)
        print("✓ Sample email saved to sample_email.html")
        
    else:
        print("✗ Email content generation failed")
        
    print()
    print("To send actual emails:")
    print("1. Set up email credentials in EmailConfig")
    print("2. Call notifier.setup_email_client()")
    print("3. Use notifier.send_quiz_notification() with recipient list")

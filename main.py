#!/usr/bin/env python3
"""
Main Orchestrator for AI Quiz System

This script ties together all three modules:
1. Quiz Generator & Script Builder (quiz_generator.py)
2. Google Apps Script Deployment & Execution (gas_deployer.py)
3. Email Notification System (email_notifier.py)

Usage:
    python main.py --questions l0/m1.json --recipients emails.txt --count 10
    python main.py --config config.json
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from quiz_generator import QuestionGenerator, QuizConfig
from gas_deployer import GoogleAppsScriptDeployer
from email_notifier import EmailNotifier, EmailConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIQuizOrchestrator:
    """Main orchestrator class for the complete AI quiz workflow"""

    def __init__(self,
                 quiz_config: Optional[QuizConfig] = None,
                 email_config: Optional[EmailConfig] = None,
                 credentials_path: str = "credentials.json"):
        """
        Initialize the orchestrator

        Args:
            quiz_config: Configuration for quiz generation
            email_config: Configuration for email notifications
            credentials_path: Path to Google API credentials
        """
        self.quiz_config = quiz_config or QuizConfig()
        self.email_config = email_config or EmailConfig.from_env()
        self.credentials_path = credentials_path

        # Initialize modules
        self.quiz_generator = QuestionGenerator(self.quiz_config)
        self.gas_deployer = GoogleAppsScriptDeployer(credentials_path)
        self.email_notifier = EmailNotifier(self.email_config)

    def load_recipients_from_file(self, file_path: str) -> List[str]:
        """
        Load email recipients from file

        Args:
            file_path: Path to file containing email addresses (one per line)

        Returns:
            List of email addresses
        """
        try:
            recipients = []
            with open(file_path, 'r') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email:
                        recipients.append(email)

            logger.info(f"Loaded {len(recipients)} recipients from {file_path}")
            return recipients

        except Exception as e:
            logger.error(f"Error loading recipients from {file_path}: {e}")
            return []

    def create_and_deploy_quiz(self,
                              questions_file: str,
                              project_title: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
        """
        Create quiz script and deploy to Google Apps Script

        Args:
            questions_file: Path to JSON file containing questions
            project_title: Optional title for the Google Apps Script project

        Returns:
            Tuple of (project_id, edit_url) or (None, None) if failed
        """
        try:
            logger.info("=== Step 1: Generating Quiz Script ===")

            # Generate quiz script from multiple files
            file_configs = [
                {'path': 'l0/m1.json', 'count': 10},  # AI Fundamentals
                {'path': 'l0/m2.json', 'count': 13},  # AI Ethics & Bias
                {'path': 'l0/m3.json', 'count': 10}   # AI Applications
            ]

            script_content = self.quiz_generator.generate_quiz_from_multiple_files(
                file_configs=file_configs,
                output_path="generated_quiz.gs"
            )

            if not script_content:
                logger.error("Failed to generate quiz script")
                return None, None

            logger.info("=== Step 2: Deploying to Google Apps Script ===")

            # Authenticate with Google APIs
            if not self.gas_deployer.authenticate_google():
                logger.error("Failed to authenticate with Google APIs")
                return None, None

            # Deploy script
            project_id, edit_url = self.gas_deployer.deploy_quiz_script(script_content)

            if project_id and edit_url:
                return project_id, edit_url
            else:
                logger.error("Failed to deploy quiz")
                return None, None

        except Exception as e:
            logger.error(f"Error in create_and_deploy_quiz: {e}")
            return None, None

    def send_notifications(self,
                          recipients: List[str],
                          quiz_url: str,
                          edit_url: Optional[str] = None,
                          deadline: Optional[str] = None) -> dict:
        """
        Send email notifications to recipients

        Args:
            recipients: List of email addresses
            quiz_url: URL to the published quiz
            edit_url: Optional edit URL for administrators
            deadline: Optional deadline string

        Returns:
            Dictionary mapping email addresses to success status
        """
        try:
            logger.info("=== Step 3: Sending Email Notifications ===")

            # Setup email client
            if not self.email_notifier.setup_email_client():
                logger.error("Failed to setup email client")
                return {}

            # Send notifications
            results = self.email_notifier.send_quiz_notification(
                recipients=recipients,
                quiz_url=quiz_url,
                question_count=self.quiz_config.question_count,
                points_per_question=self.quiz_config.points_per_question,
                deadline=deadline,
                edit_url=edit_url
            )

            # Log results
            successful = sum(1 for success in results.values() if success)
            total = len(results)

            logger.info(f"✓ Email notifications sent: {successful}/{total} successful")

            if successful < total:
                failed_emails = [email for email, success in results.items() if not success]
                logger.warning(f"Failed to send to: {', '.join(failed_emails)}")

            return results

        except Exception as e:
            logger.error(f"Error in send_notifications: {e}")
            return {}

    def run_complete_workflow(self,
                             questions_file: str,
                             recipients: List[str],
                             project_title: Optional[str] = None,
                             deadline: Optional[str] = None) -> bool:
        """
        Run the complete workflow: generate, deploy, and notify

        Args:
            questions_file: Path to JSON file containing questions
            recipients: List of email addresses
            project_title: Optional title for the Google Apps Script project
            deadline: Optional deadline string

        Returns:
            True if workflow completed successfully, False otherwise
        """
        try:
            logger.info("🚀 Starting AI Quiz Complete Workflow")
            logger.info(f"Questions: {questions_file}")
            logger.info(f"Recipients: {len(recipients)} emails")
            logger.info(f"Quiz Config: {self.quiz_config.question_count} questions, {self.quiz_config.points_per_question} points each")
            logger.info("-" * 60)

            # Step 1 & 2: Generate and deploy quiz
            project_id, edit_url = self.create_and_deploy_quiz(
                questions_file=questions_file,
                project_title=project_title
            )

            if not project_id:
                logger.error("❌ Workflow failed at quiz deployment stage")
                return False

            # Deployment-only workflow
            logger.info("✅ Quiz script deployed - ready for manual execution")
            
            # Skip email notifications since we don't have quiz URLs yet
            if recipients:
                logger.info(f"📧 {len(recipients)} recipients waiting for quiz URL")
                logger.info("💡 Run the script manually, then send the quiz URL to recipients")

            logger.info("-" * 50)
            logger.info("🎯 DEPLOYMENT COMPLETE")
            logger.info(f"🔗 Edit URL: {edit_url}")
            logger.info("-" * 50)

            return True

        except Exception as e:
            logger.error(f"❌ Workflow failed with error: {e}")
            return False


def load_config_from_file(config_path: str) -> tuple[QuizConfig, EmailConfig, dict]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Quiz configuration
        quiz_config = QuizConfig(
            title=config.get('quiz', {}).get('title', 'AI Knowledge Quiz'),
            description=config.get('quiz', {}).get('description', 'Test your AI knowledge'),
            question_count=config.get('quiz', {}).get('question_count', 10),
            points_per_question=config.get('quiz', {}).get('points_per_question', 5)
        )

        # Email configuration
        email_config = EmailConfig(
            smtp_server=config.get('email', {}).get('smtp_server', 'smtp.gmail.com'),
            smtp_port=config.get('email', {}).get('smtp_port', 587),
            sender_email=config.get('email', {}).get('sender_email', ''),
            sender_password=config.get('email', {}).get('sender_password', ''),
            sender_name=config.get('email', {}).get('sender_name', 'AI Quiz System')
        )

        # Other settings
        other_settings = {
            'questions_file': config.get('questions_file', 'l0/m1.json'),
            'recipients_file': config.get('recipients_file', ''),
            'recipients': config.get('recipients', []),
            'project_title': config.get('project_title'),
            'deadline': config.get('deadline'),
            'credentials_path': config.get('credentials_path', 'credentials.json')
        }

        return quiz_config, email_config, other_settings

    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}")
        return QuizConfig(), EmailConfig.from_env(), {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Quiz System - Complete Workflow')

    # Configuration options
    parser.add_argument('--config', help='Path to JSON configuration file')
    parser.add_argument('--questions', default='l0/m1.json', help='Path to questions JSON file')
    parser.add_argument('--recipients-file', dest='recipients_file', help='Path to recipients file (one email per line)')
    parser.add_argument('--recipients', '--emails', dest='emails', nargs='+', help='Email addresses (space-separated)')
    parser.add_argument('--count', type=int, default=10, help='Number of questions to include')
    parser.add_argument('--title', help='Quiz title')
    parser.add_argument('--deadline', help='Quiz deadline (free text)')
    parser.add_argument('--credentials', default='credentials.json', help='Path to Google API credentials')

    # Email configuration
    parser.add_argument('--smtp-server', default='smtp.gmail.com', help='SMTP server')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port')
    parser.add_argument('--sender-email', help='Sender email address')
    parser.add_argument('--sender-password', help='Sender email password')
    parser.add_argument('--sender-name', default='AI Quiz System', help='Sender name')

    # Flags
    parser.add_argument('--dry-run', action='store_true', help='Generate quiz but don\'t deploy or send emails')
    parser.add_argument('--no-email', action='store_true', help='Deploy quiz but don\'t send emails')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    if args.config:
        quiz_config, email_config, other_settings = load_config_from_file(args.config)
        # Override with command line arguments
        if args.questions:
            other_settings['questions_file'] = args.questions
        if args.count:
            quiz_config.question_count = args.count
        if args.title:
            quiz_config.title = args.title
    else:
        # Create configuration from command line arguments
        quiz_config = QuizConfig(
            title=args.title or 'AI Knowledge Quiz',
            question_count=args.count
        )

        email_config = EmailConfig(
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            sender_email=args.sender_email or os.getenv('SENDER_EMAIL', ''),
            sender_password=args.sender_password or os.getenv('SENDER_PASSWORD', ''),
            sender_name=args.sender_name
        )

        other_settings = {
            'questions_file': args.questions,
            'recipients_file': args.recipients_file,
            'recipients': args.emails or [],
            'deadline': args.deadline,
            'credentials_path': args.credentials
        }

    # Validate required files
    if not Path(other_settings['questions_file']).exists():
        logger.error(f"Questions file not found: {other_settings['questions_file']}")
        sys.exit(1)

    if not args.dry_run and not Path(other_settings['credentials_path']).exists():
        logger.error(f"Google API credentials not found: {other_settings['credentials_path']}")
        logger.info("Please follow the setup guide in SETUP_GUIDE.md")
        sys.exit(1)

    # Load recipients
    recipients = []
    if other_settings.get('recipients_file'):
        recipients.extend(AIQuizOrchestrator().load_recipients_from_file(other_settings['recipients_file']))
    if other_settings.get('recipients'):
        recipients.extend(other_settings['recipients'])

    if not args.dry_run and not args.no_email and not recipients:
        logger.warning("No recipients specified. Quiz will be created but no emails will be sent.")

    # Initialize orchestrator
    orchestrator = AIQuizOrchestrator(
        quiz_config=quiz_config,
        email_config=email_config,
        credentials_path=other_settings['credentials_path']
    )

    try:
        if args.dry_run:
            # Just generate the script
            logger.info("🧪 Dry run mode: Generating quiz script only")
            # Generate comprehensive quiz from multiple files
            file_configs = [
                {'path': 'l0/m1.json', 'count': 10},  # AI Fundamentals
                {'path': 'l0/m2.json', 'count': 13},  # AI Ethics & Bias
                {'path': 'l0/m3.json', 'count': 10}   # AI Applications
            ]

            script_content = orchestrator.quiz_generator.generate_quiz_from_multiple_files(
                file_configs=file_configs,
                output_path="generated_quiz.gs"
            )
            if script_content:
                logger.info("✅ Quiz script generated successfully")
                logger.info("📁 Saved to: generated_quiz.gs")
            else:
                logger.error("❌ Failed to generate quiz script")
                sys.exit(1)
        else:
            # Run complete workflow
            success = orchestrator.run_complete_workflow(
                questions_file=other_settings['questions_file'],
                recipients=recipients if not args.no_email else [],
                project_title=other_settings.get('project_title'),
                deadline=other_settings.get('deadline')
            )

            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

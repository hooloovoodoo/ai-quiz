"""
Ultra-Simplified Google Apps Script Deployment Module

This module handles:
1. Google API authentication (OAuth2)
2. Creating Google Apps Script projects with timestamped names
3. Uploading script content to projects
4. Providing edit URL for manual execution
"""

import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import glob

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required scopes for Google Apps Script API
SCOPES = [
    'https://www.googleapis.com/auth/script.projects',
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/drive'
]


class GoogleAppsScriptDeployer:
    """Simplified class for deploying Google Apps Script projects"""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None):
        """
        Initialize the deployer with authentication credentials

        Args:
            credentials_path: Path to OAuth2 credentials.json
            token_path: Path to store OAuth2 token
        """
        self.credentials_path = credentials_path or "credentials.json"
        self.token_path = token_path or "token.json"
        self.creds = None
        self.script_service = None

    def authenticate_google(self) -> bool:
        """
        Authenticate with Google APIs using OAuth2

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if Path(self.token_path).exists():
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())

            # Build the service
            self.script_service = build('script', 'v1', credentials=self.creds)
            logger.info("✓ Successfully authenticated with Google APIs")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def create_timestamped_project_name(self) -> str:
        """
        Create a project name with ISO 8601 timestamp

        Returns:
            Project name in format "AI Fundamentals | 2025-09-08T12:19:18Z"
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"AI Fundamentals | {timestamp}"

    def create_script_project(self, project_title: str, script_content: str) -> Optional[str]:
        """
        Create a new Google Apps Script project with the given content

        Args:
            project_title: Title for the new project
            script_content: JavaScript code content

        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # Create project request
            request_body = {
                'title': project_title,
                'parentId': None  # Creates in root folder
            }

            # Create the project
            logger.info(f"Creating Google Apps Script project: {project_title}")
            project = self.script_service.projects().create(body=request_body).execute()
            project_id = project['scriptId']
            logger.info(f"✓ Created project with ID: {project_id}")

            # Upload script content with manifest
            logger.info("Uploading script content...")
            files = [
                {
                    'name': 'Code',
                    'type': 'SERVER_JS',
                    'source': script_content
                },
                {
                    'name': 'appsscript',
                    'type': 'JSON',
                    'source': json.dumps({
                        "timeZone": "America/New_York",
                        "dependencies": {},
                        "exceptionLogging": "STACKDRIVER",
                        "runtimeVersion": "V8"
                    })
                }
            ]

            request_body = {
                'files': files
            }

            self.script_service.projects().updateContent(
                scriptId=project_id,
                body=request_body
            ).execute()

            logger.info("✓ Script content uploaded successfully")
            return project_id

        except HttpError as e:
            logger.error(f"HTTP error creating project: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None

    def deploy_quiz_script(self, script_content: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Deploy quiz script to Google Apps Script (deployment only)

        Args:
            script_content: The generated Google Apps Script code

        Returns:
            Tuple of (project_id, edit_url) or (None, None) if failed
        """
        try:
            # Create timestamped project name
            project_title = self.create_timestamped_project_name()

            # Create and upload the project
            project_id = self.create_script_project(project_title, script_content)

            if not project_id:
                logger.error("Failed to create script project")
                return None, None

            # Generate edit URL
            edit_url = f"https://script.google.com/d/{project_id}/edit"

            logger.info("=" * 50)
            logger.info("🎉 QUIZ SCRIPT DEPLOYED!")
            logger.info("=" * 50)
            logger.info(f"📝 Project: {project_title}")
            logger.info(f"🔗 Edit URL: {edit_url}")
            logger.info("")
            logger.info("▶️ NEXT STEP: Click the URL above and run the script")
            logger.info("=" * 50)

            return project_id, edit_url

        except Exception as e:
            logger.error(f"Error deploying quiz script: {e}")
            return None, None

    def deploy_batch_quiz_scripts(self, quiz_files_pattern: str = "/tmp/AI Quiz | L0 | * | Variant *.gs") -> List[Dict[str, str]]:
        """
        Deploy multiple quiz scripts from /tmp directory

        Args:
            quiz_files_pattern: Glob pattern to find quiz files

        Returns:
            List of dictionaries with 'variant', 'project_id', 'edit_url' for each deployed quiz
        """
        try:
            # Find all quiz files matching the pattern
            quiz_files = glob.glob(quiz_files_pattern)

            if not quiz_files:
                logger.error(f"No quiz files found matching pattern: {quiz_files_pattern}")
                return []

            # Sort files to ensure consistent ordering
            quiz_files.sort()

            logger.info("=" * 60)
            logger.info("🚀 BATCH QUIZ DEPLOYMENT")
            logger.info("=" * 60)
            logger.info(f"📁 Found {len(quiz_files)} quiz files to deploy")

            deployed_quizzes = []

            for i, quiz_file in enumerate(quiz_files):
                try:
                    file_path = Path(quiz_file)
                    filename = file_path.name

                    logger.info(f"📝 Deploying {i+1}/{len(quiz_files)}: {filename}")

                    # Read the quiz script content
                    with open(quiz_file, 'r', encoding='utf-8') as f:
                        script_content = f.read()

                    # Extract variant number from filename
                    # Format: "AI Quiz | L0 | 2025-09-15 | Variant 0.gs"
                    variant_part = filename.split(" | Variant ")[-1].replace(".gs", "")

                    # Use the filename (without .gs) as the project title
                    project_title = filename.replace(".gs", "")

                    # Create and upload the project
                    project_id = self.create_script_project(project_title, script_content)

                    if project_id:
                        edit_url = f"https://script.google.com/d/{project_id}/edit"

                        deployed_quizzes.append({
                            'variant': variant_part,
                            'filename': filename,
                            'project_id': project_id,
                            'edit_url': edit_url
                        })

                        logger.info(f"✅ Variant {variant_part} deployed successfully")
                    else:
                        logger.error(f"❌ Failed to deploy variant {variant_part}")

                except Exception as e:
                    logger.error(f"❌ Error deploying {quiz_file}: {e}")
                    continue

            # Summary
            logger.info("=" * 60)
            logger.info(f"🎉 BATCH DEPLOYMENT COMPLETE")
            logger.info(f"✅ Successfully deployed: {len(deployed_quizzes)}/{len(quiz_files)} quizzes")
            logger.info("=" * 60)

            # List all deployed URLs
            if deployed_quizzes:
                logger.info("🔗 DEPLOYED QUIZ URLS:")
                for quiz in deployed_quizzes:
                    logger.info(f"   📄 Variant {quiz['variant']}: {quiz['edit_url']}")
                logger.info("=" * 60)

            return deployed_quizzes

        except Exception as e:
            logger.error(f"Error in batch deployment: {e}")
            return []

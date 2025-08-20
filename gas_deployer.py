"""
Google Apps Script Deployment & Execution Module

This module handles:
1. Google API authentication (OAuth2/Service Account)
2. Creating Google Apps Script projects
3. Uploading script content to projects
4. Executing script functions to create forms
5. Retrieving form URLs from execution results
6. Error handling for API operations
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required scopes for Google Apps Script API
SCOPES = [
    'https://www.googleapis.com/auth/script.projects',
    'https://www.googleapis.com/auth/script.deployments', 
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/drive'
]


class GoogleAppsScriptDeployer:
    """Main class for deploying and executing Google Apps Script projects"""
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize the deployer with authentication credentials
        
        Args:
            credentials_path: Path to OAuth2 credentials.json or service account key
            token_path: Path to store OAuth2 token (for user authentication)
        """
        self.credentials_path = credentials_path or "credentials.json"
        self.token_path = token_path or "token.json"
        self.service = None
        self.credentials = None
        
    def authenticate_google(self, use_service_account: bool = False) -> bool:
        """
        Authenticate with Google APIs
        
        Args:
            use_service_account: If True, use service account authentication
                               If False, use OAuth2 user authentication
                               
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if use_service_account:
                self.credentials = self._authenticate_service_account()
            else:
                self.credentials = self._authenticate_oauth2()
                
            if self.credentials:
                self.service = build('script', 'v1', credentials=self.credentials)
                logger.info("Successfully authenticated with Google APIs")
                return True
            else:
                logger.error("Failed to obtain valid credentials")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
            
    def _authenticate_service_account(self) -> Optional[service_account.Credentials]:
        """Authenticate using service account credentials"""
        try:
            if not Path(self.credentials_path).exists():
                raise FileNotFoundError(f"Service account key not found: {self.credentials_path}")
                
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            logger.info("Service account authentication successful")
            return credentials
            
        except Exception as e:
            logger.error(f"Service account authentication failed: {e}")
            return None
            
    def _authenticate_oauth2(self) -> Optional[Credentials]:
        """Authenticate using OAuth2 flow"""
        creds = None
        
        # Load existing token if available
        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
        # If no valid credentials, run OAuth2 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed existing OAuth2 token")
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    creds = None
                    
            if not creds:
                if not Path(self.credentials_path).exists():
                    raise FileNotFoundError(f"OAuth2 credentials not found: {self.credentials_path}")
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Completed OAuth2 authentication flow")
                
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
                
        return creds
        
    def create_script_project(self, title: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new Google Apps Script project
        
        Args:
            title: Name for the script project
            parent_folder_id: Optional Google Drive folder ID to store the project
            
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            if not self.service:
                raise RuntimeError("Not authenticated. Call authenticate_google() first.")
                
            request_body = {
                'title': title
            }
            
            if parent_folder_id:
                request_body['parentId'] = parent_folder_id
                
            response = self.service.projects().create(body=request_body).execute()
            project_id = response.get('scriptId')
            
            logger.info(f"Created script project '{title}' with ID: {project_id}")
            return project_id
            
        except HttpError as e:
            logger.error(f"HTTP error creating script project: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating script project: {e}")
            return None
            
    def upload_script_content(self, project_id: str, script_content: str, filename: str = "Code") -> bool:
        """
        Upload script content to a Google Apps Script project
        
        Args:
            project_id: ID of the script project
            script_content: JavaScript code to upload
            filename: Name for the script file (default: "Code")
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            if not self.service:
                raise RuntimeError("Not authenticated. Call authenticate_google() first.")
                
            # Prepare the script content
            request_body = {
                'files': [
                    {
                        'name': filename,
                        'type': 'SERVER_JS',
                        'source': script_content
                    }
                ]
            }
            
            response = self.service.projects().updateContent(
                scriptId=project_id,
                body=request_body
            ).execute()
            
            logger.info(f"Successfully uploaded script content to project {project_id}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error uploading script content: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading script content: {e}")
            return False
            
    def execute_function(self, project_id: str, function_name: str, 
                        parameters: Optional[list] = None, dev_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Execute a function in a Google Apps Script project
        
        Args:
            project_id: ID of the script project
            function_name: Name of the function to execute
            parameters: Optional list of parameters to pass to the function
            dev_mode: Whether to run in development mode
            
        Returns:
            Execution response dict if successful, None otherwise
        """
        try:
            if not self.service:
                raise RuntimeError("Not authenticated. Call authenticate_google() first.")
                
            request_body = {
                'function': function_name,
                'parameters': parameters or [],
                'devMode': dev_mode
            }
            
            logger.info(f"Executing function '{function_name}' in project {project_id}")
            
            response = self.service.scripts().run(
                scriptId=project_id,
                body=request_body
            ).execute()
            
            if 'error' in response:
                error_details = response['error']['details']
                logger.error(f"Script execution error: {error_details}")
                return None
                
            logger.info(f"Successfully executed function '{function_name}'")
            return response
            
        except HttpError as e:
            logger.error(f"HTTP error executing function: {e}")
            return None
        except Exception as e:
            logger.error(f"Error executing function: {e}")
            return None
            
    def get_execution_logs(self, project_id: str, execution_response: Dict[str, Any]) -> list:
        """
        Extract logs from script execution response
        
        Args:
            project_id: ID of the script project
            execution_response: Response from execute_function()
            
        Returns:
            List of log entries
        """
        logs = []
        
        try:
            if 'response' in execution_response:
                response_data = execution_response['response']
                
                # Check for logs in the response
                if 'result' in response_data:
                    logs.append(f"Function result: {response_data['result']}")
                    
            # Note: Getting detailed logs requires additional API calls
            # For now, we'll work with what's available in the execution response
            
        except Exception as e:
            logger.error(f"Error extracting logs: {e}")
            
        return logs
        
    def extract_form_urls(self, execution_response: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract form URLs from script execution response
        
        Args:
            execution_response: Response from execute_function()
            
        Returns:
            Tuple of (published_url, edit_url) or (None, None) if not found
        """
        try:
            if 'response' in execution_response and 'result' in execution_response['response']:
                result = execution_response['response']['result']
                
                if isinstance(result, dict):
                    published_url = result.get('publishedUrl')
                    edit_url = result.get('editUrl')
                    form_id = result.get('formId')
                    
                    if published_url and edit_url:
                        logger.info(f"Extracted form URLs - Published: {published_url}, Edit: {edit_url}")
                        return published_url, edit_url
                        
            # If direct extraction fails, try to parse from logs
            # This is a fallback for cases where the function logs URLs
            logger.warning("Could not extract URLs from function result, checking logs...")
            return None, None
            
        except Exception as e:
            logger.error(f"Error extracting form URLs: {e}")
            return None, None
            
    def deploy_and_execute_quiz(self, script_content: str, project_title: str = "AI Quiz Generator") -> Tuple[Optional[str], Optional[str]]:
        """
        Complete workflow: Create project, upload script, execute, and get URLs
        
        Args:
            script_content: Generated Google Apps Script code
            project_title: Name for the script project
            
        Returns:
            Tuple of (published_url, edit_url) or (None, None) if failed
        """
        try:
            # Create new script project
            project_id = self.create_script_project(project_title)
            if not project_id:
                logger.error("Failed to create script project")
                return None, None
                
            # Upload script content
            if not self.upload_script_content(project_id, script_content):
                logger.error("Failed to upload script content")
                return None, None
                
            # Wait a moment for the upload to process
            time.sleep(2)
            
            # Execute the quiz creation function
            execution_response = self.execute_function(project_id, 'createRandomAIQuiz')
            if not execution_response:
                logger.error("Failed to execute quiz creation function")
                return None, None
                
            # Extract form URLs
            published_url, edit_url = self.extract_form_urls(execution_response)
            
            if published_url and edit_url:
                logger.info(f"Successfully created quiz form!")
                logger.info(f"Published URL: {published_url}")
                logger.info(f"Edit URL: {edit_url}")
                return published_url, edit_url
            else:
                logger.error("Could not extract form URLs from execution response")
                return None, None
                
        except Exception as e:
            logger.error(f"Error in deploy_and_execute_quiz workflow: {e}")
            return None, None


# Example usage and testing
if __name__ == "__main__":
    # Initialize deployer
    deployer = GoogleAppsScriptDeployer()
    
    # Test authentication (you'll need to set up credentials first)
    print("Testing Google Apps Script Deployer...")
    print("Note: This requires valid Google API credentials to work.")
    print()
    
    # Example of how to use the deployer
    print("Example usage:")
    print("1. Set up Google API credentials (credentials.json)")
    print("2. Run authentication: deployer.authenticate_google()")
    print("3. Load script content from quiz_generator.py output") 
    print("4. Deploy: deployer.deploy_and_execute_quiz(script_content)")
    print()
    
    # Check if credentials file exists
    if Path("credentials.json").exists():
        print("✓ Found credentials.json file")
        try:
            # Try to authenticate (will require user interaction for OAuth2)
            if deployer.authenticate_google():
                print("✓ Authentication successful")
                
                # Load example script content
                if Path("generated_quiz.gs").exists():
                    with open("generated_quiz.gs", 'r') as f:
                        script_content = f.read()
                    
                    print("✓ Loaded script content")
                    print("Ready to deploy quiz! Call deploy_and_execute_quiz() to proceed.")
                else:
                    print("⚠ No generated_quiz.gs found. Run quiz_generator.py first.")
            else:
                print("✗ Authentication failed")
                
        except Exception as e:
            print(f"✗ Error during testing: {e}")
    else:
        print("⚠ No credentials.json found. Please set up Google API credentials first.")
        print("See: https://developers.google.com/apps-script/api/quickstart/python")

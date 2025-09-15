from quiz_generator import QuestionGenerator, QuizConfig
from gas_deployer import GoogleAppsScriptDeployer

# Generate comprehensive quiz script from multiple files
config = QuizConfig(
    title="Comprehensive AI Knowledge Quiz",
    description="Test your knowledge across AI fundamentals, ethics, and practical applications",
    question_count=33,  # Total: 10 + 13 + 10
    points_per_question=5
)

generator = QuestionGenerator(config)

# Define question distribution across files
file_configs = [
    {'path': 'l0/m1.json', 'count': 10},  # AI Fundamentals
    {'path': 'l0/m2.json', 'count': 13},  # AI Ethics & Bias  
    {'path': 'l0/m3.json', 'count': 10}   # AI Applications
]

script_content = generator.generate_quiz_from_multiple_files(
    file_configs=file_configs,
    output_path="generated_quiz.gs"
)

# Deploy to Google Apps Script with simplified deployment
deployer = GoogleAppsScriptDeployer()
if deployer.authenticate_google():
    project_id, edit_url = deployer.deploy_quiz_script(script_content)
    
    if project_id and edit_url:
        print(f"Quiz script deployed! Edit URL: {edit_url}")
        print("Please open the URL and click 'Run' to create the quiz form")
    else:
        print("Failed to deploy quiz script")

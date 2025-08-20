"""
Question Generator & Script Builder Module

This module handles:
1. Loading questions from JSON files
2. Converting JSON format to JavaScript-compatible structure
3. Randomly selecting questions for quizzes
4. Generating complete Google Apps Script code
5. Configurable quiz settings
"""

import json
import random
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuizConfig:
    """Configuration class for quiz settings"""
    
    def __init__(self, 
                 title: str = "AI Knowledge Quiz",
                 description: str = "Test your knowledge about Artificial Intelligence. Choose the best answer.",
                 question_count: int = 10,
                 points_per_question: int = 5,
                 collect_email: bool = True,
                 limit_responses: bool = True,
                 show_link_to_respond_again: bool = False,
                 confirmation_message: str = "Thanks for taking the quiz! You'll receive your score after submitting."):
        
        self.title = title
        self.description = description
        self.question_count = question_count
        self.points_per_question = points_per_question
        self.collect_email = collect_email
        self.limit_responses = limit_responses
        self.show_link_to_respond_again = show_link_to_respond_again
        self.confirmation_message = confirmation_message


class QuestionGenerator:
    """Main class for generating quiz scripts from JSON question data"""
    
    def __init__(self, config: Optional[QuizConfig] = None):
        self.config = config or QuizConfig()
        
    def load_questions(self, json_path: str) -> List[Dict[str, Any]]:
        """
        Load and validate questions from JSON file
        
        Args:
            json_path: Path to the JSON file containing questions
            
        Returns:
            List of validated question dictionaries
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON format is invalid
        """
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                raise FileNotFoundError(f"Question file not found: {json_path}")
                
            with open(json_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                
            if not isinstance(questions, list):
                raise ValueError("JSON file must contain a list of questions")
                
            # Validate question structure
            validated_questions = []
            for i, question in enumerate(questions):
                if not self._validate_question(question, i):
                    continue
                validated_questions.append(question)
                
            logger.info(f"Loaded {len(validated_questions)} valid questions from {json_path}")
            return validated_questions
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {json_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            raise
            
    def _validate_question(self, question: Dict[str, Any], index: int) -> bool:
        """
        Validate individual question structure
        
        Args:
            question: Question dictionary to validate
            index: Question index for error reporting
            
        Returns:
            True if question is valid, False otherwise
        """
        required_fields = ['question', 'answers', 'correct']
        
        for field in required_fields:
            if field not in question:
                logger.warning(f"Question {index}: Missing required field '{field}', skipping")
                return False
                
        if not isinstance(question['answers'], list) or len(question['answers']) < 2:
            logger.warning(f"Question {index}: 'answers' must be a list with at least 2 options, skipping")
            return False
            
        if question['correct'] not in question['answers']:
            logger.warning(f"Question {index}: 'correct' answer not found in 'answers' list, skipping")
            return False
            
        return True
        
    def convert_format(self, questions: List[Dict[str, Any]], shuffle_choices: bool = True) -> List[Dict[str, Any]]:
        """
        Convert JSON question format to JavaScript-compatible structure
        
        Args:
            questions: List of questions in JSON format
            shuffle_choices: Whether to randomize the order of answer choices
            
        Returns:
            List of questions in JS-compatible format
        """
        js_questions = []
        
        for question in questions:
            choices = question['answers'].copy()
            correct_answer = question['correct']
            
            if shuffle_choices:
                # Shuffle the choices and find new correct index
                random.shuffle(choices)
                correct_index = choices.index(correct_answer)
            else:
                # Keep original order
                correct_index = choices.index(correct_answer)
            
            js_question = {
                'question': question['question'],
                'choices': choices,
                'correct': correct_index
            }
            
            js_questions.append(js_question)
            
        logger.info(f"Converted {len(js_questions)} questions to JS format (shuffle_choices={shuffle_choices})")
        return js_questions
        
    def select_random_questions(self, questions: List[Dict[str, Any]], count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Randomly select questions from the pool
        
        Args:
            questions: List of available questions
            count: Number of questions to select (defaults to config.question_count)
            
        Returns:
            List of randomly selected questions
            
        Raises:
            ValueError: If requested count exceeds available questions
        """
        if count is None:
            count = self.config.question_count
            
        if count > len(questions):
            raise ValueError(f"Requested {count} questions but only {len(questions)} available")
            
        selected = random.sample(questions, count)
        logger.info(f"Selected {len(selected)} random questions")
        return selected
        
    def generate_script(self, questions: List[Dict[str, Any]]) -> str:
        """
        Generate complete Google Apps Script code with embedded questions
        
        Args:
            questions: List of questions in JS format
            
        Returns:
            Complete Google Apps Script code as string
        """
        # Convert questions to JavaScript array format
        questions_js = self._format_questions_for_js(questions)
        
        script_template = f'''function createRandomAIQuiz() {{
  const questionsPool = {questions_js};

  // Shuffle and pick {len(questions)} questions
  const selectedQuestions = shuffleArray(questionsPool).slice(0, {len(questions)});

  // Create the quiz form
  const form = FormApp.create('{self.config.title}');
  form.setIsQuiz(true);
  form.setTitle('{self.config.title}');
  form.setDescription('{self.config.description}');

  // Add selected questions to the form
  selectedQuestions.forEach(q => {{
    const item = form.addMultipleChoiceItem();
    const choices = q.choices.map((choice, index) =>
      item.createChoice(choice, index === q.correct)
    );
    item.setTitle(q.question)
      .setChoices(choices)
      .setPoints({self.config.points_per_question})
      .setRequired(true);
  }});

  // Set quiz submission settings
  form.setCollectEmail({str(self.config.collect_email).lower()});
  form.setShowLinkToRespondAgain({str(self.config.show_link_to_respond_again).lower()});
  form.setConfirmationMessage('{self.config.confirmation_message}');

  // Ensure responses are sent to the creator
  form.setPublishingSummary(true);
  form.setLimitOneResponsePerUser({str(self.config.limit_responses).lower()});
  form.setAllowResponseEdits(false);

  // Disable collaborators from editing the form after creation
  const editors = form.getEditors();
  editors.forEach(user => {{
    form.removeEditor(user);
  }});

  Logger.log("Form URL (Share this): " + form.getPublishedUrl());
  Logger.log("Edit URL (For you only): " + form.getEditUrl());
  
  return {{
    publishedUrl: form.getPublishedUrl(),
    editUrl: form.getEditUrl(),
    formId: form.getId()
  }};
}}

// Helper function to shuffle array
function shuffleArray(array) {{
  let currentIndex = array.length, temporaryValue, randomIndex;
  while (0 !== currentIndex) {{
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;
    // Swap
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }}
  return array;
}}'''

        logger.info("Generated Google Apps Script code")
        return script_template
        
    def _format_questions_for_js(self, questions: List[Dict[str, Any]]) -> str:
        """
        Format questions as JavaScript array string
        
        Args:
            questions: List of questions in JS format
            
        Returns:
            JavaScript array string representation
        """
        js_array = "[\n"
        
        for i, q in enumerate(questions):
            # Escape quotes in question text and choices
            question_text = q['question'].replace('"', '\\"').replace("'", "\\'")
            choices = [choice.replace('"', '\\"').replace("'", "\\'") for choice in q['choices']]
            
            js_array += f'''    {{
      question: "{question_text}",
      choices: {json.dumps(choices)},
      correct: {q['correct']}
    }}'''
            
            if i < len(questions) - 1:
                js_array += ","
            js_array += "\n"
            
        js_array += "  ]"
        return js_array
        
    def save_script(self, script_content: str, output_path: str) -> None:
        """
        Save generated script to file
        
        Args:
            script_content: Generated Google Apps Script code
            output_path: Path where to save the script file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
                
            logger.info(f"Script saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving script: {e}")
            raise
            
    def generate_quiz_from_json(self, json_path: str, output_path: str, question_count: Optional[int] = None) -> str:
        """
        Complete workflow: Load JSON, generate script, and save to file
        
        Args:
            json_path: Path to JSON question file
            output_path: Path to save generated script
            question_count: Number of questions to select (optional)
            
        Returns:
            Generated script content
        """
        try:
            # Load and validate questions
            questions = self.load_questions(json_path)
            
            # Convert to JS format
            js_questions = self.convert_format(questions)
            
            # Select random subset
            selected_questions = self.select_random_questions(js_questions, question_count)
            
            # Generate script
            script_content = self.generate_script(selected_questions)
            
            # Save to file
            self.save_script(script_content, output_path)
            
            logger.info(f"Successfully generated quiz script with {len(selected_questions)} questions")
            return script_content
            
        except Exception as e:
            logger.error(f"Error in quiz generation workflow: {e}")
            raise


# Example usage and testing
if __name__ == "__main__":
    # Create custom configuration
    config = QuizConfig(
        title="Advanced AI Knowledge Test",
        description="Challenge yourself with advanced AI concepts",
        question_count=10,
        points_per_question=10
    )
    
    # Initialize generator
    generator = QuestionGenerator(config)
    
    # Generate quiz from JSON file
    try:
        script_content = generator.generate_quiz_from_json(
            json_path="l0/m1.json",
            output_path="generated_quiz.gs",
            question_count=10
        )
        print("Quiz generation completed successfully!")
        print(f"Generated script length: {len(script_content)} characters")
        
    except Exception as e:
        print(f"Error: {e}")

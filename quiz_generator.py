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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuizConfig:
    """Configuration class for quiz settings"""

    def __init__(self,
                 title: str = "AI Knowledge Quiz",
                 description: str = "HLV 💚 AI",
                 question_count: int = 10,
                 points_per_question: int = 1,
                 collect_email: bool = True,
                 limit_responses: bool = True,
                 show_link_to_respond_again: bool = False,
                 confirmation_message: str = \
                    "Hvala što ste učestvovали u kvizu! / Thanks for taking the quiz!",
                 language: str = "ENG",
                 results_sheet: str = "1g9A2x0H_qP4MUz3pEWi-kgH3CWftx4CmcAkEgQ2FKX8"):

        self.title = title
        self.description = description
        self.question_count = question_count
        self.points_per_question = points_per_question
        self.collect_email = collect_email
        self.limit_responses = limit_responses
        self.show_link_to_respond_again = show_link_to_respond_again
        self.confirmation_message = confirmation_message
        self.language = language.upper()
        self.results_sheet = results_sheet


class QuestionGenerator:
    """Main class for generating quiz scripts from JSON question data"""

    def __init__(self, config: Optional[QuizConfig] = None):
        self.config = config or QuizConfig()

    def get_file_configs_for_language(
        self, language: str = "ENG") -> List[Dict[str, Any]]:
        """
        Get file configurations for the specified language

        Args:
            language: Language code ("ENG" or "SRB")

        Returns:
            List of file configurations with paths and question counts
        """
        language = language.upper()

        if language == "ENG":
            base_path = "QAPool/eng/L0"
        elif language == "SRB":
            base_path = "QAPool/srb/L0"
        else:
            raise ValueError(f"Unsupported language: {language}. Use 'ENG' or 'SRB'")

        return [
            {'path': f'{base_path}/M1/m1.json', 'count': 7},  # AI Fundamentals
            {'path': f'{base_path}/M2/m2.json', 'count': 9},  # AI Ethics & Bias
            {'path': f'{base_path}/M3/m3.json', 'count': 7}   # AI Applications
        ]

    def load_questions_from_multiple_files(
        self,
        file_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Load and validate questions from multiple JSON files with specific counts

        Args:
            file_configs: List of dicts with 'path' and 'count' keys
                         e.g., [{'path': 'l0/m1.json', 'count': 10}, ...]

        Returns:
            List of validated question dictionaries from all files

        Raises:
            FileNotFoundError: If any JSON file doesn't exist
            ValueError: If JSON format is invalid or insufficient questions
        """
        all_questions = []

        for config in file_configs:
            file_path = config['path']
            required_count = config['count']

            logger.info(f"Loading {required_count} questions from {file_path}")
            file_questions = self.load_questions(file_path)

            if len(file_questions) < required_count:
                raise ValueError(
                    "File %s has only %s questions, but %s required",
                    file_path, len(file_questions), required_count)

            selected_questions = random.sample(file_questions, required_count)
            all_questions.extend(selected_questions)

            logger.info("Selected %d questions from %s",
                        len(selected_questions), file_path)

        logger.info("Total questions loaded: %d", len(all_questions))
        return all_questions

    def load_questions(
        self,
        json_path: str) -> List[Dict[str, Any]]:
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

    def _validate_question(
        self,
        question: Dict[str, Any],
        index: int) -> bool:
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
                logger.warning(
                    "Question %d: Missing required field '%s', skipping",
                    index, field)
                return False

        if not isinstance(question['answers'], list) or len(question['answers']) != 4:
            logger.warning(
                "Question %d: 'answers' must be a list of 4 options, skipping",
                index)
            return False

        if question['correct'] not in question['answers']:
            logger.warning(
                "Question %d: 'correct' answer not found in 'answers', skipping",
                index)
            return False

        return True

    def convert_format(
        self,
        questions: List[Dict[str, Any]],
        shuffle_choices: bool = True) -> List[Dict[str, Any]]:
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

        logger.info("Converted %d questions to JS format (shuffle_choices=%s)",
                    len(js_questions), shuffle_choices)
        return js_questions

    def select_random_questions(
        self,
        questions: List[Dict[str, Any]],
        count: Optional[int] = None) -> List[Dict[str, Any]]:
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
            raise ValueError("Requested %d questions but only %d available",
                             count, len(questions))

        selected = random.sample(questions, count)
        logger.info("Selected %d random questions", len(selected))
        return selected

    def generate_script(
        self,
        questions: List[Dict[str, Any]]) -> str:
        """
        Generate complete Google Apps Script code with embedded questions

        Args:
            questions: List of questions in JS format

        Returns:
            Complete Google Apps Script code as string
        """
        # Convert questions to JavaScript array format
        questions_js = self._format_questions_for_js(questions)

        script_template = f'''/**
 * Creates an AI Knowledge Quiz with {len(questions)} questions
 * - Autograded multiple choice questions with {self.config.points_per_question} point(s) each
 * - Immediate feedback showing correct answers and score
 * - Email notification with PASS/FAIL result (70% threshold)
 * - Centralized response collection in Google Sheets: {self.config.results_sheet}
 */
function createRandomAIQuiz() {{
  const questionsPool = {questions_js};

  // Shuffle and pick {len(questions)} questions
  const selectedQuestions = shuffleArray(questionsPool).slice(0, {len(questions)});

  // Create the quiz form
  const form = FormApp.create('{self._escape_js_string(self.config.title)}')
    .setIsQuiz(true)
    .setCollectEmail(true)             // needed to email respondents
    .setShowLinkToRespondAgain(false);

  form.setTitle('{self._escape_js_string(self.config.title)}');
  form.setDescription('{self._escape_js_string(self.config.description)}');

  // Link form to Google Sheets for centralized response collection
  try {{
    const spreadsheetId = '{self.config.results_sheet}';
    form.setDestination(FormApp.DestinationType.SPREADSHEET, spreadsheetId);
    Logger.log(`✅ Form linked to Google Sheets: ${{spreadsheetId}}`);
  }} catch (error) {{
    Logger.log(`⚠️  Could not link to spreadsheet: ${{error.message}}`);
    Logger.log('Form will store responses in its own response sheet');
  }}

  // Optional settings for better UX
  form.setPublishingSummary(false);
  form.setLimitOneResponsePerUser({str(self.config.limit_responses).lower()});
  form.setConfirmationMessage('{self._escape_js_string(self.config.confirmation_message)}');

  // Helper function to add a fully-configured MC question
  const addMCQuestion = (questionData) => {{
    const item = form.addMultipleChoiceItem();
    item.setTitle(questionData.question)
        .setPoints({self.config.points_per_question})
        .setRequired(true);

    // Build choices with exactly one correct answer
    const choices = questionData.choices.map((choice, index) =>
      item.createChoice(choice, index === questionData.correct)
    );
    item.setChoices(choices);

    // Optional feedback for immediate learning
    const fbCorrect = FormApp.createFeedback().setText('Correct! ✅').build();
    const fbIncorrect = FormApp.createFeedback().setText('Review this topic.').build();
    item.setFeedbackForCorrect(fbCorrect);
    item.setFeedbackForIncorrect(fbIncorrect);

    return item;
  }};

  // Add all selected questions to the form
  selectedQuestions.forEach(questionData => {{
    addMCQuestion(questionData);
  }});

  // Clean up any existing triggers for this handler to avoid duplicates
  ScriptApp.getProjectTriggers()
    .filter(trigger => trigger.getHandlerFunction() === 'onFormSubmit')
    .forEach(trigger => ScriptApp.deleteTrigger(trigger));

  // Create the form submission trigger for PASS/FAIL email logic
  ScriptApp.newTrigger('onFormSubmit')
    .forForm(form)
    .onFormSubmit()
    .create();

  const totalPoints = selectedQuestions.length * {self.config.points_per_question};
  const passingScore = Math.ceil(totalPoints * 0.7);

  Logger.log('=== QUIZ CREATED SUCCESSFULLY ===');
  Logger.log(`Questions: ${{selectedQuestions.length}}`);
  Logger.log(`Points per question: {self.config.points_per_question}`);
  Logger.log(`Total possible points: ${{totalPoints}}`);
  Logger.log(`Passing score (70%): ${{passingScore}} points`);
  Logger.log('');
  Logger.log('Form URLs:');
  Logger.log('Edit form: ' + form.getEditUrl());
  Logger.log('Live quiz: ' + form.getPublishedUrl());
  Logger.log('');
  Logger.log('✅ Trigger installed for PASS/FAIL email notifications');

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
}}

/**
 * On submit: compute score by comparing responses to marked correct choices
 * for all Multiple Choice items, then email PASS/FAIL at 70%.
 */
function onFormSubmit(e) {{
  const form = e.source;
  const response = e.response;

  const email = response.getRespondentEmail();
  if (!email) return;

  const mcItems = form.getItems(FormApp.ItemType.MULTIPLE_CHOICE);
  let totalPoints = 0;
  let earnedPoints = 0;

  mcItems.forEach(item => {{
    const mci = item.asMultipleChoiceItem();
    const points = mci.getPoints() || 0;
    totalPoints += points;

    const ir = response.getResponseForItem(item);
    const answer = ir ? ir.getResponse() : null;

    const correctChoice = mci.getChoices().find(c => c.isCorrectAnswer());
    const correctValue = correctChoice ? correctChoice.getValue() : null;

    if (answer !== null && correctValue !== null && answer === correctValue) {{
      earnedPoints += points;
    }}
  }});

  const pct = totalPoints > 0 ? (earnedPoints / totalPoints) * 100 : 0;
  const passed = pct >= 70;

  const subject = `Your quiz result: ${{Math.round(pct)}}% — ${{passed ? 'PASS' : 'FAIL'}}`;
  const body = `Hvala što ste učestvovали u kvizu! / Thanks for taking the quiz!

🎯: ${{earnedPoints}} / ${{totalPoints}} (${{pct.toFixed(1)}}%)
🏁: ${{passed ? 'PASS ✅' : 'FAIL ❌'}}`;

  MailApp.sendEmail(email, subject, body);
}}'''

        logger.info("Generated Google Apps Script code")
        return script_template

    def _escape_js_string(
        self,
        text: str) -> str:
        """Escape special characters for JavaScript strings"""
        return text.replace(
            '\\', '\\\\').replace("'", "\\'").replace(
                '"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

    def _format_questions_for_js(
        self,
        questions: List[Dict[str, Any]]) -> str:
        """
        Format questions as JavaScript array string

        Args:
            questions: List of questions in JS format

        Returns:
            JavaScript array string representation
        """
        js_array = "[\n"

        for i, q in enumerate(questions):
            question_text = self._escape_js_string(q['question'])
            choices = [self._escape_js_string(choice) for choice in q['choices']]

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

    def save_script(
        self,
        script_content: str,
        output_path: str) -> None:
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

    def generate_quiz_from_multiple_files(
        self,
        file_configs: List[Dict[str, Any]],
        output_path: str,
        variant_number: Optional[int] = None) -> str:
        """
        Complete workflow: Load questions from multiple JSONs, generate script, save to file

        Args:
            file_configs: List of dicts with 'path' and 'count' keys
                         e.g., [{'path': 'QAPool/eng/L0/M1/m1.json', 'count': 10}, ...]
            output_path: Path to save generated script
            variant_number: Optional variant number to include in title

        Returns:
            Generated script content
        """
        try:
            # Update title with language and variant info
            original_title = self.config.title
            language_tag = f"[{self.config.language}]"

            if variant_number is not None:
                self.config.title = f"{original_title} {language_tag} Variant {variant_number}"
            else:
                self.config.title = f"{original_title} {language_tag}"

            # Load questions from multiple files
            all_questions = self.load_questions_from_multiple_files(file_configs)

            # Convert to JS format
            js_questions = self.convert_format(all_questions)

            # Shuffle all questions together
            random.shuffle(js_questions)

            # Generate script
            script_content = self.generate_script(js_questions)

            # Save to file
            self.save_script(script_content, output_path)

            total_questions = sum(config['count'] for config in file_configs)
            logger.info(
                "Successfully generated %s quiz script with %d questions from %d files",
                self.config.language,
                total_questions,
                len(file_configs))

            # Restore original title
            self.config.title = original_title

            return script_content

        except Exception as e:
            logger.error(f"Error in multi-file quiz generation workflow: {e}")
            raise

    def generate_quiz_from_json(
        self,
        json_path: str,
        output_path: str,
        question_count: Optional[int] = None,
        variant_number: Optional[int] = None) -> str:
        """
        Complete workflow: Load JSON, generate script, and save to file

        Args:
            json_path: Path to JSON question file
            output_path: Path to save generated script
            question_count: Number of questions to select (optional)
            variant_number: Optional variant number to include in title

        Returns:
            Generated script content
        """
        try:
            # Update title with language and variant info
            original_title = self.config.title
            language_tag = f"[{self.config.language}]"

            if variant_number is not None:
                self.config.title = f"{original_title} {language_tag} Variant {variant_number}"
            else:
                self.config.title = f"{original_title} {language_tag}"

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

            logger.info(
                "Successfully generated %s quiz script with %d questions",
                self.config.language,
                len(selected_questions))

            # Restore original title
            self.config.title = original_title

            return script_content

        except RuntimeError as e:
            logger.error("Error in quiz generation workflow: %s", e)
            raise

    def generate_quiz_for_language(
        self,
        language: str = "ENG",
        output_path: str = None,
        variant_number: Optional[int] = None) -> str:
        """
        Generate quiz using the standard file structure for the specified language

        Args:
            language: Language code ("ENG" or "SRB")
            output_path: Path to save generated script (optional)
            variant_number: Optional variant number to include in title

        Returns:
            Generated script content
        """
        # Update config language
        self.config.language = language.upper()

        # Get file configurations for the language
        file_configs = self.get_file_configs_for_language(language)

        # Generate default output path if not provided
        if output_path is None:
            lang_suffix = language.lower()
            if variant_number is not None:
                output_path = f"generated_quiz_{lang_suffix}_variant_{variant_number}.gs"
            else:
                output_path = f"generated_quiz_{lang_suffix}.gs"

        return self.generate_quiz_from_multiple_files(file_configs, output_path, variant_number)

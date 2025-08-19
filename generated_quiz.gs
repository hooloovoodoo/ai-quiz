function createRandomAIQuiz() {
  const questionsPool = [
    {
      question: "What is AI best suited for in terms of tasks?",
      choices: ["High-volume, repetitive tasks with clear patterns", "Tasks requiring deep emotional understanding", "One-time creative projects"],
      correct: 0
    },
    {
      question: "What makes AI systems vulnerable?",
      choices: ["They are heavily dependent on the quality of their training data", "They consume too much electricity", "They are too fast for human oversight"],
      correct: 0
    },
    {
      question: "Why do technical limitations of AI create ethical concerns?",
      choices: ["Because AI mistakes and biases can affect people\\'s lives and perpetuate unfairness", "Because AI is too expensive to develop", "Because AI learns too quickly"],
      correct: 0
    },
    {
      question: "What is the main purpose of Generative AI?",
      choices: ["Creates new content", "Classifies existing data", "Predicts future outcomes"],
      correct: 0
    },
    {
      question: "What is a key principle of good prompt engineering?",
      choices: ["Be specific and provide context", "Keep prompts as short as possible", "Use technical jargon to be precise"],
      correct: 0
    },
    {
      question: "What does LLM stand for?",
      choices: ["Large Language Model", "Long Learning Memory", "Linear Logic Machine"],
      correct: 0
    },
    {
      question: "What is a key characteristic of supervised learning?",
      choices: ["It learns from labeled examples", "It learns without any data", "It only works with images"],
      correct: 0
    },
    {
      question: "What is a limitation of AI creativity?",
      choices: ["AI lacks genuine emotion, consciousness, and lived experience", "AI cannot create any form of art", "AI creativity is too expensive to use"],
      correct: 0
    },
    {
      question: "What type of data is typically used to train AI systems?",
      choices: ["Large amounts of examples with patterns", "Only perfectly clean data", "Small, carefully selected datasets"],
      correct: 0
    },
    {
      question: "What is a context window in AI?",
      choices: ["The maximum amount of text the model can \\'see\\' at once", "The time it takes for the model to respond", "The graphical interface for interacting with AI"],
      correct: 0
    }
  ];

  // Shuffle and pick 10 questions
  const selectedQuestions = shuffleArray(questionsPool).slice(0, 10);

  // Create the quiz form
  const form = FormApp.create('Advanced AI Knowledge Test');
  form.setIsQuiz(true);
  form.setTitle('Advanced AI Knowledge Test');
  form.setDescription('Challenge yourself with advanced AI concepts');

  // Add selected questions to the form
  selectedQuestions.forEach(q => {
    const item = form.addMultipleChoiceItem();
    const choices = q.choices.map((choice, index) =>
      item.createChoice(choice, index === q.correct)
    );
    item.setTitle(q.question)
      .setChoices(choices)
      .setPoints(10)
      .setRequired(true);
  });

  // Set quiz submission settings
  form.setCollectEmail(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage('Thanks for taking the quiz! You'll receive your score after submitting.');

  // Ensure responses are sent to the creator
  form.setPublishingSummary(true);
  form.setLimitOneResponsePerUser(true);
  form.setAllowResponseEdits(false);

  // Disable collaborators from editing the form after creation
  const editors = form.getEditors();
  editors.forEach(user => {
    form.removeEditor(user);
  });

  Logger.log("Form URL (Share this): " + form.getPublishedUrl());
  Logger.log("Edit URL (For you only): " + form.getEditUrl());
  
  return {
    publishedUrl: form.getPublishedUrl(),
    editUrl: form.getEditUrl(),
    formId: form.getId()
  };
}

// Helper function to shuffle array
function shuffleArray(array) {
  let currentIndex = array.length, temporaryValue, randomIndex;
  while (0 !== currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;
    // Swap
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }
  return array;
}
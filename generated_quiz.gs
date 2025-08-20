function createRandomAIQuiz() {
  const questionsPool = [
    {
      question: "What makes AI systems vulnerable?",
      choices: ["They are heavily dependent on the quality of their training data", "They consume too much electricity", "They are too fast for human oversight"],
      correct: 0
    },
    {
      question: "What is a limitation of AI creativity?",
      choices: ["AI lacks genuine emotion, consciousness, and lived experience", "AI cannot create any form of art", "AI creativity is too expensive to use"],
      correct: 0
    },
    {
      question: "What does LLM stand for?",
      choices: ["Large Language Model", "Linear Logic Machine", "Long Learning Memory"],
      correct: 0
    },
    {
      question: "What are AI \'hallucinations\'?",
      choices: ["When AI refuses to answer questions", "When AI becomes self-aware", "When AI generates plausible but incorrect information"],
      correct: 2
    },
    {
      question: "What is AI best suited for in terms of tasks?",
      choices: ["High-volume, repetitive tasks with clear patterns", "Tasks requiring deep emotional understanding", "One-time creative projects"],
      correct: 0
    }
  ];

  // Shuffle and pick 5 questions
  const selectedQuestions = shuffleArray(questionsPool).slice(0, 5);

  // Create the quiz form
  const form = FormApp.create('AI Knowledge Quiz');
  form.setIsQuiz(true);
  form.setTitle('AI Knowledge Quiz');
  form.setDescription('Test your knowledge about Artificial Intelligence. Choose the best answer.');

  // Add selected questions to the form
  selectedQuestions.forEach(q => {
    const item = form.addMultipleChoiceItem();
    const choices = q.choices.map((choice, index) =>
      item.createChoice(choice, index === q.correct)
    );
    item.setTitle(q.question)
      .setChoices(choices)
      .setPoints(5)
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
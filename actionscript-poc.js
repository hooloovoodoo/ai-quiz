function createRandomAIQuiz() {
    const questionsPool = [
      {
        question: "What does AI stand for?",
        choices: ["Artificial Imagination", "Artificial Intelligence", "Automated Interface"],
        correct: 1
      },
      {
        question: "Which company developed ChatGPT?",
        choices: ["Google", "OpenAI", "Meta"],
        correct: 1
      },
      {
        question: "What is machine learning?",
        choices: ["Manual coding of rules", "Learning by repetition", "Training models on data"],
        correct: 2
      },
      {
        question: "What is the main function of a neural network?",
        choices: ["Storing memory", "Processing text", "Modeling patterns in data"],
        correct: 2
      },
      {
        question: "Which language is most used for AI development?",
        choices: ["Java", "Python", "C++"],
        correct: 1
      },
      {
        question: "What is supervised learning?",
        choices: ["Learning with labels", "Learning by itself", "Learning from mistakes only"],
        correct: 0
      },
      {
        question: "What is the Turing Test meant to evaluate?",
        choices: ["Speed", "Memory", "Human-likeness of AI"],
        correct: 2
      },
      {
        question: "Which field is AI NOT commonly used in?",
        choices: ["Medical diagnosis", "Weather forecasting", "Time travel"],
        correct: 2
      },
      {
        question: "Which algorithm is common in AI?",
        choices: ["Binary search", "Decision tree", "Quick sort"],
        correct: 1
      },
      {
        question: "Which of these is a type of AI?",
        choices: ["Narrow AI", "Broad AI", "Flexible AI"],
        correct: 0
      }
    ];

    // Shuffle and pick 3 random questions
    const selectedQuestions = shuffleArray(questionsPool).slice(0, 3);

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
    form.setConfirmationMessage('Thanks for taking the quiz! You’ll receive your score after submitting.');

    // Ensure responses are sent to the creator (you)
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

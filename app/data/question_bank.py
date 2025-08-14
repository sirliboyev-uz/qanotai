"""
IELTS Speaking Question Bank for Epic 2
"""
from app.models.test_models import Question, TestPart
import uuid


# US-2.2: Part 1 Interview Questions
PART1_QUESTIONS = [
    # Work/Study topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="Do you work or are you a student?",
        topic="Work/Study",
        expected_duration_seconds=30,
        difficulty_level=4,
        tags=["introduction", "common"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="What do you like about your job or studies?",
        topic="Work/Study",
        expected_duration_seconds=30,
        difficulty_level=5,
        tags=["opinion", "common"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="What would you like to change about your work or studies?",
        topic="Work/Study",
        expected_duration_seconds=30,
        difficulty_level=6,
        tags=["opinion", "future"]
    ),
    
    # Hometown topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="Where is your hometown?",
        topic="Hometown",
        expected_duration_seconds=30,
        difficulty_level=3,
        tags=["introduction", "place"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="What do you like about your hometown?",
        topic="Hometown",
        expected_duration_seconds=30,
        difficulty_level=4,
        tags=["opinion", "place"]
    ),
    
    # Technology topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="How often do you use the internet?",
        topic="Technology",
        expected_duration_seconds=30,
        difficulty_level=4,
        tags=["frequency", "technology"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART1,
        text="What do you usually do online?",
        topic="Technology",
        expected_duration_seconds=30,
        difficulty_level=5,
        tags=["habits", "technology"]
    ),
]

# US-2.3: Part 2 Cue Cards
PART2_QUESTIONS = [
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART2,
        text="Describe a person who has influenced you",
        topic="People",
        bullet_points=[
            "Who this person is",
            "How you know this person",
            "What influence they had on you",
            "Explain why this influence was important"
        ],
        preparation_time_seconds=60,
        speaking_time_seconds=120,
        difficulty_level=6,
        tags=["people", "influence", "relationships"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART2,
        text="Describe a memorable journey you have made",
        topic="Travel",
        bullet_points=[
            "Where you went",
            "How you traveled",
            "Who you went with",
            "Explain why it was memorable"
        ],
        preparation_time_seconds=60,
        speaking_time_seconds=120,
        difficulty_level=5,
        tags=["travel", "experience", "memory"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART2,
        text="Describe a skill you would like to learn",
        topic="Skills",
        bullet_points=[
            "What the skill is",
            "Why you want to learn it",
            "How you would learn it",
            "Explain how this skill would benefit you"
        ],
        preparation_time_seconds=60,
        speaking_time_seconds=120,
        difficulty_level=5,
        tags=["skills", "future", "learning"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART2,
        text="Describe a book you recently read",
        topic="Books",
        bullet_points=[
            "What the book was about",
            "Why you chose to read it",
            "What you learned from it",
            "Explain whether you would recommend it to others"
        ],
        preparation_time_seconds=60,
        speaking_time_seconds=120,
        difficulty_level=5,
        tags=["books", "education", "opinion"]
    ),
]

# US-2.4: Part 3 Discussion Questions
PART3_QUESTIONS = [
    # Related to People topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="What qualities make someone a good role model?",
        topic="People",
        expected_duration_seconds=45,
        difficulty_level=7,
        tags=["abstract", "qualities", "society"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="Do you think celebrities have a responsibility to be good role models?",
        topic="People",
        expected_duration_seconds=45,
        difficulty_level=8,
        tags=["opinion", "society", "responsibility"]
    ),
    
    # Related to Travel topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="What are the benefits of traveling to different countries?",
        topic="Travel",
        expected_duration_seconds=45,
        difficulty_level=6,
        tags=["benefits", "culture", "experience"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="How has tourism affected your country?",
        topic="Travel",
        expected_duration_seconds=45,
        difficulty_level=7,
        tags=["impact", "economy", "society"]
    ),
    
    # Related to Skills topic
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="What skills are most important for success in the modern world?",
        topic="Skills",
        expected_duration_seconds=45,
        difficulty_level=7,
        tags=["future", "work", "education"]
    ),
    Question(
        id=str(uuid.uuid4()),
        part=TestPart.PART3,
        text="How has technology changed the way people learn new skills?",
        topic="Skills",
        expected_duration_seconds=45,
        difficulty_level=7,
        tags=["technology", "education", "change"]
    ),
]


def get_question_set(test_mode: str = "full", topic: str = None):
    """Get a set of questions for a test attempt"""
    from app.models.test_models import QuestionSet, TestMode
    import random
    
    question_set = QuestionSet(test_mode=TestMode(test_mode))
    
    if test_mode in ["full", "part1"]:
        # Select 4-5 Part 1 questions
        available_p1 = PART1_QUESTIONS.copy()
        if topic:
            available_p1 = [q for q in available_p1 if q.topic == topic]
        question_set.part1_questions = random.sample(
            available_p1, 
            min(4, len(available_p1))
        )
    
    if test_mode in ["full", "part2"]:
        # Select 1 Part 2 cue card
        available_p2 = PART2_QUESTIONS.copy()
        if topic:
            available_p2 = [q for q in available_p2 if q.topic == topic]
        if available_p2:
            question_set.part2_question = random.choice(available_p2)
    
    if test_mode in ["full", "part3"]:
        # Select 4-5 Part 3 questions (preferably related to Part 2 topic)
        available_p3 = PART3_QUESTIONS.copy()
        if question_set.part2_question:
            # Try to get questions related to Part 2 topic
            related = [q for q in available_p3 if q.topic == question_set.part2_question.topic]
            if related:
                available_p3 = related
        elif topic:
            available_p3 = [q for q in available_p3 if q.topic == topic]
        
        question_set.part3_questions = random.sample(
            available_p3,
            min(4, len(available_p3))
        )
    
    if test_mode == "quick":
        # Quick test: 2 Part 1, 1 Part 2, 2 Part 3
        question_set.part1_questions = random.sample(PART1_QUESTIONS, 2)
        question_set.part2_question = random.choice(PART2_QUESTIONS)
        question_set.part3_questions = random.sample(PART3_QUESTIONS, 2)
    
    return question_set
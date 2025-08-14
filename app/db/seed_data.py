"""
Seed initial IELTS Speaking questions into database
"""
import asyncio
from uuid import uuid4
from app.core.database import AsyncSessionLocal
from app.models.question import Question
import json

SAMPLE_QUESTIONS = {
    "part1": [
        # Work/Study
        {"text": "Do you work or are you a student?", "topic": "Work/Study", "difficulty_level": 4},
        {"text": "What do you like about your job/studies?", "topic": "Work/Study", "difficulty_level": 5},
        {"text": "What would you like to change about your work/studies?", "topic": "Work/Study", "difficulty_level": 6},
        
        # Hometown
        {"text": "Where is your hometown?", "topic": "Hometown", "difficulty_level": 3},
        {"text": "What do you like about your hometown?", "topic": "Hometown", "difficulty_level": 4},
        {"text": "How has your hometown changed in recent years?", "topic": "Hometown", "difficulty_level": 6},
        
        # Technology
        {"text": "How often do you use the internet?", "topic": "Technology", "difficulty_level": 4},
        {"text": "What do you usually do online?", "topic": "Technology", "difficulty_level": 5},
        {"text": "Do you think people rely too much on technology?", "topic": "Technology", "difficulty_level": 7},
        
        # Hobbies
        {"text": "What do you like to do in your free time?", "topic": "Hobbies", "difficulty_level": 4},
        {"text": "Have your hobbies changed since you were a child?", "topic": "Hobbies", "difficulty_level": 6},
        {"text": "What hobby would you like to try in the future?", "topic": "Hobbies", "difficulty_level": 5},
    ],
    
    "part2": [
        {
            "text": "Describe a person who has influenced you",
            "topic": "People",
            "difficulty_level": 6,
            "bullet_points": [
                "Who this person is",
                "How you know this person",
                "What influence they had on you",
                "Explain why this influence was important"
            ]
        },
        {
            "text": "Describe a memorable journey you have made",
            "topic": "Travel",
            "difficulty_level": 5,
            "bullet_points": [
                "Where you went",
                "How you traveled",
                "Who you went with",
                "Explain why it was memorable"
            ]
        },
        {
            "text": "Describe a skill you would like to learn",
            "topic": "Skills",
            "difficulty_level": 5,
            "bullet_points": [
                "What the skill is",
                "Why you want to learn it",
                "How you would learn it",
                "Explain how this skill would benefit you"
            ]
        },
        {
            "text": "Describe a book you recently read",
            "topic": "Books",
            "difficulty_level": 5,
            "bullet_points": [
                "What the book was about",
                "Why you chose to read it",
                "What you learned from it",
                "Explain whether you would recommend it to others"
            ]
        },
        {
            "text": "Describe a tradition in your country",
            "topic": "Culture",
            "difficulty_level": 6,
            "bullet_points": [
                "What the tradition is",
                "When it takes place",
                "What people do",
                "Explain why this tradition is important"
            ]
        },
    ],
    
    "part3": [
        # Related to People topic
        {"text": "What qualities make someone a good role model?", "topic": "People", "difficulty_level": 7},
        {"text": "Do you think celebrities have a responsibility to be good role models?", "topic": "People", "difficulty_level": 8},
        {"text": "How has social media changed the way people influence each other?", "topic": "People", "difficulty_level": 8},
        
        # Related to Travel topic
        {"text": "What are the benefits of traveling to different countries?", "topic": "Travel", "difficulty_level": 6},
        {"text": "How has tourism affected your country?", "topic": "Travel", "difficulty_level": 7},
        {"text": "Do you think virtual travel will replace physical travel in the future?", "topic": "Travel", "difficulty_level": 8},
        
        # Related to Skills topic
        {"text": "What skills are most important for success in the modern world?", "topic": "Skills", "difficulty_level": 7},
        {"text": "How has technology changed the way people learn new skills?", "topic": "Skills", "difficulty_level": 7},
        {"text": "Should schools focus more on practical skills or academic knowledge?", "topic": "Skills", "difficulty_level": 8},
        
        # Related to Books topic
        {"text": "Do you think people read less nowadays than in the past?", "topic": "Books", "difficulty_level": 6},
        {"text": "What are the advantages of e-books over traditional books?", "topic": "Books", "difficulty_level": 6},
        {"text": "How important is it to encourage children to read?", "topic": "Books", "difficulty_level": 7},
        
        # Related to Culture topic
        {"text": "How important is it to preserve traditional culture?", "topic": "Culture", "difficulty_level": 7},
        {"text": "How has globalization affected local traditions?", "topic": "Culture", "difficulty_level": 8},
        {"text": "What role should the government play in preserving culture?", "topic": "Culture", "difficulty_level": 8},
    ]
}


async def seed_questions():
    """Seed the database with sample IELTS questions"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if questions already exist
            existing = await session.execute(
                "SELECT COUNT(*) FROM questions"
            )
            count = existing.scalar()
            
            if count > 0:
                print(f"✅ Database already has {count} questions")
                return
            
            # Add Part 1 questions
            for q_data in SAMPLE_QUESTIONS["part1"]:
                question = Question(
                    id=uuid4(),
                    part=1,
                    text=q_data["text"],
                    topic=q_data["topic"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_duration_seconds=30,
                    is_active=True
                )
                session.add(question)
            
            # Add Part 2 questions
            for q_data in SAMPLE_QUESTIONS["part2"]:
                question = Question(
                    id=uuid4(),
                    part=2,
                    text=q_data["text"],
                    topic=q_data["topic"],
                    difficulty_level=q_data["difficulty_level"],
                    bullet_points=q_data["bullet_points"],
                    preparation_time_seconds=60,
                    speaking_time_seconds=120,
                    is_active=True
                )
                session.add(question)
            
            # Add Part 3 questions
            for q_data in SAMPLE_QUESTIONS["part3"]:
                question = Question(
                    id=uuid4(),
                    part=3,
                    text=q_data["text"],
                    topic=q_data["topic"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_duration_seconds=45,
                    is_active=True
                )
                session.add(question)
            
            await session.commit()
            
            total = len(SAMPLE_QUESTIONS["part1"]) + len(SAMPLE_QUESTIONS["part2"]) + len(SAMPLE_QUESTIONS["part3"])
            print(f"✅ Seeded {total} questions successfully!")
            print(f"   - Part 1: {len(SAMPLE_QUESTIONS['part1'])} questions")
            print(f"   - Part 2: {len(SAMPLE_QUESTIONS['part2'])} questions")
            print(f"   - Part 3: {len(SAMPLE_QUESTIONS['part3'])} questions")
            
        except Exception as e:
            print(f"❌ Error seeding questions: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_questions())
"""
Populate Supabase with sample data for testing
"""
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import random

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

def populate_sample_data():
    """Populate database with sample data"""
    
    print("\n🌱 Populating Supabase with sample data...")
    
    # 1. Add question topics
    print("\n📚 Adding question topics...")
    topics = [
        {
            "id": str(uuid.uuid4()),
            "name": "Technology and Modern Life",
            "description": "Discuss the impact of technology on society, social media, and digital transformation",
            "category": "Technology",
            "difficulty_level": "intermediate",
            "tags": ["technology", "society", "digital", "internet"],
            "keywords": ["smartphone", "AI", "social media", "innovation"],
            "popularity_score": 0.95,
            "is_trending": True,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Environmental Issues",
            "description": "Climate change, sustainability, and environmental protection",
            "category": "Environment",
            "difficulty_level": "advanced",
            "tags": ["environment", "climate", "sustainability"],
            "keywords": ["global warming", "pollution", "renewable energy"],
            "popularity_score": 0.88,
            "is_trending": True,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Education Systems",
            "description": "Compare education systems, online learning, and educational technology",
            "category": "Education",
            "difficulty_level": "intermediate",
            "tags": ["education", "learning", "schools", "university"],
            "keywords": ["online learning", "curriculum", "students", "teachers"],
            "popularity_score": 0.82,
            "is_trending": False,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Health and Lifestyle",
            "description": "Physical and mental health, fitness, diet, and wellbeing",
            "category": "Health",
            "difficulty_level": "beginner",
            "tags": ["health", "fitness", "wellness", "lifestyle"],
            "keywords": ["exercise", "diet", "mental health", "stress"],
            "popularity_score": 0.90,
            "is_trending": True,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Work and Career",
            "description": "Employment, career development, work-life balance",
            "category": "Work",
            "difficulty_level": "intermediate",
            "tags": ["career", "job", "employment", "professional"],
            "keywords": ["interview", "promotion", "remote work", "skills"],
            "popularity_score": 0.78,
            "is_trending": False,
            "is_active": True
        }
    ]
    
    try:
        for topic in topics:
            result = supabase.table("question_topics").insert(topic).execute()
        print(f"✅ Added {len(topics)} question topics")
    except Exception as e:
        print(f"⚠️  Topics might already exist: {str(e)[:50]}")
    
    # 2. Add sample questions
    print("\n❓ Adding sample questions...")
    questions = []
    
    # Part 1 questions (simple, personal)
    part1_questions = [
        "Do you like using technology in your daily life?",
        "How often do you use social media?",
        "What's your favorite type of weather?",
        "Do you enjoy reading books?",
        "How do you usually spend your weekends?",
        "What kind of music do you like?",
        "Do you prefer shopping online or in stores?",
        "How important is exercise to you?",
        "What's your favorite way to relax?",
        "Do you like cooking?"
    ]
    
    # Part 2 questions (cue cards)
    part2_questions = [
        "Describe a piece of technology that you find useful. You should say: what it is, how you use it, how often you use it, and explain why you find it useful.",
        "Describe an environmental problem in your area. You should say: what it is, what causes it, how it affects people, and suggest what could be done about it.",
        "Describe a teacher who influenced you. You should say: who this teacher was, what subject they taught, what made them special, and explain how they influenced you.",
        "Describe a healthy lifestyle change you made. You should say: what the change was, when you made it, why you decided to make it, and explain how it has affected your life.",
        "Describe your ideal job. You should say: what it would be, what skills you would need, what you would do in this job, and explain why this would be your ideal job."
    ]
    
    # Part 3 questions (discussion, abstract)
    part3_questions = [
        "How do you think technology will change education in the future?",
        "What are the main environmental challenges facing your country?",
        "Do you think the education system in your country needs reform? Why?",
        "How can governments encourage people to live healthier lifestyles?",
        "What skills will be most important for workers in the future?",
        "Should social media companies be more regulated?",
        "Is online learning as effective as traditional classroom learning?",
        "What role should governments play in protecting the environment?",
        "How has the concept of work-life balance changed in recent years?",
        "What are the advantages and disadvantages of working from home?"
    ]
    
    topic_ids = [t["id"] for t in topics]
    
    # Create questions for each part
    for i, q_text in enumerate(part1_questions):
        questions.append({
            "id": str(uuid.uuid4()),
            "topic_id": random.choice(topic_ids),
            "part": 1,
            "text": q_text,
            "difficulty": "easy",
            "category": topics[i % len(topics)]["category"],
            "tags": ["part1", "personal", "simple"],
            "keywords": q_text.lower().split()[:3],
            "estimated_time_seconds": 30,
            "is_active": True
        })
    
    for i, q_text in enumerate(part2_questions):
        questions.append({
            "id": str(uuid.uuid4()),
            "topic_id": topic_ids[i % len(topic_ids)],
            "part": 2,
            "text": q_text,
            "difficulty": "medium",
            "category": topics[i % len(topics)]["category"],
            "tags": ["part2", "cue-card", "descriptive"],
            "keywords": q_text.lower().split()[:5],
            "sample_answer": "Sample answer would go here...",
            "tips": "Remember to cover all points on the cue card and speak for 1-2 minutes.",
            "estimated_time_seconds": 120,
            "is_active": True
        })
    
    for i, q_text in enumerate(part3_questions):
        questions.append({
            "id": str(uuid.uuid4()),
            "topic_id": random.choice(topic_ids),
            "part": 3,
            "text": q_text,
            "difficulty": "hard",
            "category": topics[i % len(topics)]["category"],
            "tags": ["part3", "discussion", "abstract"],
            "keywords": q_text.lower().split()[:5],
            "estimated_time_seconds": 90,
            "is_active": True
        })
    
    try:
        for question in questions:
            result = supabase.table("questions").insert(question).execute()
        print(f"✅ Added {len(questions)} questions")
    except Exception as e:
        print(f"⚠️  Questions might already exist: {str(e)[:50]}")
    
    # 3. Create today's daily challenge
    print("\n🎯 Creating daily challenge...")
    
    try:
        # Get some question IDs for the challenge
        part1_ids = [q["id"] for q in questions if q["part"] == 1][:2]
        part2_id = [q["id"] for q in questions if q["part"] == 2][0]
        part3_ids = [q["id"] for q in questions if q["part"] == 3][:2]
        
        daily_challenge = {
            "id": str(uuid.uuid4()),
            "challenge_date": datetime.now().date().isoformat(),
            "title": f"Daily Challenge - {datetime.now().strftime('%B %d')}",
            "description": "Today's IELTS Speaking practice challenge",
            "theme": "Technology and Modern Life",
            "part_1_questions": part1_ids,
            "part_2_question": part2_id,
            "part_3_questions": part3_ids,
            "focus_skills": ["fluency", "vocabulary", "coherence"],
            "estimated_duration_minutes": 15,
            "is_active": True
        }
        
        result = supabase.table("daily_challenges").insert(daily_challenge).execute()
        print("✅ Created today's daily challenge")
    except Exception as e:
        print(f"⚠️  Daily challenge might already exist: {str(e)[:50]}")
    
    # 4. Add sample achievements
    print("\n🏆 Adding achievements...")
    
    achievements = [
        {
            "id": str(uuid.uuid4()),
            "name": "First Steps",
            "description": "Complete your first practice test",
            "icon": "👶",
            "criteria": {"tests_completed": 1},
            "points": 10,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Consistency Key",
            "description": "Practice 3 days in a row",
            "icon": "🔥",
            "criteria": {"streak_days": 3},
            "points": 25,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Week Warrior",
            "description": "Complete 7 tests in a week",
            "icon": "💪",
            "criteria": {"weekly_tests": 7},
            "points": 50,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Perfect Score",
            "description": "Achieve Band 8.0 or higher",
            "icon": "🌟",
            "criteria": {"min_score": 8.0},
            "points": 100,
            "is_active": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Vocabulary Master",
            "description": "Use advanced vocabulary consistently",
            "icon": "📚",
            "criteria": {"vocabulary_score": 8.0},
            "points": 40,
            "is_active": True
        }
    ]
    
    try:
        for achievement in achievements:
            result = supabase.table("achievements").insert(achievement).execute()
        print(f"✅ Added {len(achievements)} achievements")
    except Exception as e:
        print(f"⚠️  Achievements might already exist: {str(e)[:50]}")
    
    print("\n✨ Sample data population complete!")
    print("\n📊 Summary:")
    print(f"  - {len(topics)} Question Topics")
    print(f"  - {len(questions)} Questions (Part 1, 2, 3)")
    print(f"  - 1 Daily Challenge")
    print(f"  - {len(achievements)} Achievements")
    print(f"  - 4 Subscription Plans (already added by schema)")
    
    print("\n🎉 Your Supabase database is now ready for testing!")
    print("You can view this data in your Supabase Dashboard")

if __name__ == "__main__":
    populate_sample_data()
"""
API endpoints for Epic 3: AI-Powered Assessment
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
from app.core.auth import get_current_user, require_auth
from app.models.scoring_models import (
    Transcript, BandScore, FeedbackReport, LanguageAnalysis,
    ScoringRequest, ScoringResponse
)
from app.services.ai_service import (
    TranscriptionService, ScoringService, FeedbackService
)

router = APIRouter(prefix="/api/v1/assessment", tags=["ai-assessment"])

# Initialize services
transcription_service = TranscriptionService()
scoring_service = ScoringService()
feedback_service = FeedbackService()

# In-memory storage for demo
transcripts_db = {}
scores_db = {}
feedback_db = {}
analysis_db = {}
tasks_db = {}


@router.post("/transcribe", response_model=Transcript)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    attempt_id: str = None,
    part: str = None,
    question_index: int = 0,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-3.1: Speech Transcription
    Acceptance Criteria:
    - Transcription appears within 3 seconds after speaking
    - Accuracy rate >90% for clear speech
    - Highlights uncertain words
    - Supports Uzbek-accented English
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Transcribe audio
        transcript = await transcription_service.transcribe_audio(audio_data)
        
        # Update transcript metadata
        transcript.attempt_id = attempt_id or str(uuid.uuid4())
        transcript.part = part or "unknown"
        transcript.question_index = question_index
        
        # Store transcript
        transcript_id = transcript.id
        transcripts_db[transcript_id] = transcript
        
        return transcript
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


from pydantic import BaseModel as PydanticBaseModel

class MockTranscriptRequest(PydanticBaseModel):
    attempt_id: str
    part: str
    question_index: int = 0
    sample_text: Optional[str] = None

@router.post("/transcribe/mock", response_model=Transcript)
async def mock_transcribe(
    request: MockTranscriptRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Mock transcription for testing without audio"""
    # Use provided text or generate sample
    if not request.sample_text:
        samples = {
            "part1": "I work as a software developer at a technology company. I really enjoy my job because it allows me to solve interesting problems and work with talented people. The work is challenging but very rewarding.",
            "part2": "I'd like to talk about my best friend Sarah who has had a significant influence on my life. I met her during my first year at university when we were both studying computer science. She influenced me to be more confident and to pursue my dreams. This was important because I was very shy and unsure about my abilities before meeting her. She always encouraged me to take on new challenges and believed in me even when I didn't believe in myself.",
            "part3": "I think the most important qualities for a role model include integrity, perseverance, and empathy. A good role model should demonstrate these qualities consistently in their actions, not just their words. They should also be willing to admit their mistakes and show how they learn from them."
        }
        sample_text = samples.get(request.part, samples["part1"])
    else:
        sample_text = request.sample_text
    
    # Create mock transcript
    transcript = Transcript(
        attempt_id=request.attempt_id,
        part=request.part,
        question_index=request.question_index,
        text=sample_text,
        confidence=0.92,
        word_count=len(sample_text.split()),
        words_per_minute=150,
        unique_words=len(set(sample_text.lower().split())),
        filler_words=["um", "uh"] if "um" in sample_text or "uh" in sample_text else [],
        transcription_service="mock",
        model_version="demo-1.0"
    )
    
    # Store transcript
    transcripts_db[transcript.id] = transcript
    
    return transcript


@router.post("/score", response_model=ScoringResponse)
async def score_attempt(
    request: ScoringRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-3.2: Band Score Prediction
    Acceptance Criteria:
    - Overall band score (0-9) displayed prominently
    - Individual scores for Fluency, Lexical Resource, Grammar, Pronunciation
    - Score breakdown with explanations
    - Comparison to target band score
    """
    # Create task ID
    task_id = str(uuid.uuid4())
    
    # Store task
    tasks_db[task_id] = {
        "id": task_id,
        "status": "pending",
        "attempt_id": request.attempt_id,
        "created_at": datetime.utcnow()
    }
    
    # Process scoring in background
    background_tasks.add_task(
        process_scoring,
        task_id,
        request.attempt_id,
        request.target_band
    )
    
    return ScoringResponse(
        task_id=task_id,
        status="pending",
        estimated_time_seconds=15 if request.urgent else 30
    )


async def process_scoring(task_id: str, attempt_id: str, target_band: Optional[float]):
    """Background task to process scoring"""
    try:
        # Update task status
        tasks_db[task_id]["status"] = "processing"
        
        # Get transcripts for this attempt
        attempt_transcripts = [
            t for t in transcripts_db.values() 
            if t.attempt_id == attempt_id
        ]
        
        # Calculate band score
        score = await scoring_service.calculate_band_score(
            attempt_transcripts,
            target_band
        )
        
        # Store score
        scores_db[score.id] = score
        
        # Generate feedback
        feedback = await feedback_service.generate_feedback(
            score,
            attempt_transcripts
        )
        feedback_db[feedback.id] = feedback
        
        # Analyze language for each transcript
        for transcript in attempt_transcripts:
            analysis = await feedback_service.analyze_language(transcript)
            analysis_db[analysis.id] = analysis
        
        # Update task status
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["score_id"] = score.id
        tasks_db[task_id]["feedback_id"] = feedback.id
        
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


@router.get("/score/{attempt_id}", response_model=BandScore)
async def get_score(
    attempt_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get band score for an attempt"""
    # Find score for this attempt
    for score in scores_db.values():
        if score.attempt_id == attempt_id:
            return score
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Score not found. It may still be processing."
    )


@router.get("/feedback/{attempt_id}", response_model=FeedbackReport)
async def get_feedback(
    attempt_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-3.3: Detailed Feedback Report
    Acceptance Criteria:
    - Strengths highlighted in green
    - Areas for improvement in amber/red
    - Specific examples from responses
    - Actionable improvement suggestions
    """
    # Find feedback for this attempt
    for feedback in feedback_db.values():
        if feedback.attempt_id == attempt_id:
            return feedback
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Feedback not found. Score may still be processing."
    )


@router.get("/analysis/{transcript_id}", response_model=LanguageAnalysis)
async def get_language_analysis(
    transcript_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-3.4: Grammar & Vocabulary Analysis
    Acceptance Criteria:
    - Grammar errors identified with corrections
    - Vocabulary range assessment
    - Suggestions for better word choices
    - Common Uzbek learner mistakes highlighted
    """
    # Find analysis for this transcript
    for analysis in analysis_db.values():
        if analysis.transcript_id == transcript_id:
            return analysis
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis not found"
    )


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get scoring task status"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = tasks_db[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "attempt_id": task["attempt_id"]
    }
    
    if task["status"] == "completed":
        response["score_id"] = task.get("score_id")
        response["feedback_id"] = task.get("feedback_id")
        response["result_url"] = f"/api/v1/assessment/score/{task['attempt_id']}"
    elif task["status"] == "failed":
        response["error"] = task.get("error")
    
    return response


@router.post("/mock-score/{attempt_id}")
async def create_mock_score(
    attempt_id: str,
    target_band: Optional[float] = 7.0,
    background_tasks: BackgroundTasks = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Create mock score for testing"""
    # Create mock transcripts if none exist
    if not any(t.attempt_id == attempt_id for t in transcripts_db.values()):
        # Create sample transcripts
        for part in ["part1", "part2", "part3"]:
            request = MockTranscriptRequest(
                attempt_id=attempt_id,
                part=part,
                question_index=0
            )
            await mock_transcribe(
                request=request,
                current_user=current_user
            )
    
    # Get transcripts
    attempt_transcripts = [
        t for t in transcripts_db.values() 
        if t.attempt_id == attempt_id
    ]
    
    # Create mock score
    score = await scoring_service.calculate_band_score(
        attempt_transcripts,
        target_band
    )
    scores_db[score.id] = score
    
    # Generate feedback
    feedback = await feedback_service.generate_feedback(
        score,
        attempt_transcripts
    )
    feedback_db[feedback.id] = feedback
    
    # Analyze language
    for transcript in attempt_transcripts:
        analysis = await feedback_service.analyze_language(transcript)
        analysis_db[analysis.id] = analysis
    
    return {
        "message": "Mock score created successfully",
        "attempt_id": attempt_id,
        "score_id": score.id,
        "overall_band": score.overall_band,
        "feedback_available": True,
        "analysis_available": True
    }
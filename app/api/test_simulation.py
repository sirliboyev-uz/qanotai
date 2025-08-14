"""
API endpoints for Epic 2: IELTS Speaking Test Simulation
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import asyncio
import os
import aiofiles
from app.core.auth import get_current_user, require_auth
from app.models.test_models import (
    TestMode, TestPart, TestAttempt, QuestionSet,
    RecordingSession, TimerState, Question
)
from app.data.question_bank import get_question_set

router = APIRouter(prefix="/api/v1/test", tags=["test-simulation"])

# In-memory storage for test attempts
test_attempts = {}
recording_sessions = {}
timers = {}


class StartTestRequest(BaseModel):
    """US-2.1: Start Mock Test request"""
    test_mode: TestMode = TestMode.FULL
    topic: Optional[str] = None
    target_band_score: Optional[int] = Field(None, ge=1, le=9)


class StartTestResponse(BaseModel):
    """US-2.1: Start Mock Test response"""
    attempt_id: str
    test_mode: TestMode
    question_set: QuestionSet
    instructions: str
    estimated_duration_minutes: int


class RecordingRequest(BaseModel):
    """US-2.5: Voice Recording request"""
    action: str = Field(..., description="start, stop, pause, resume")
    part: Optional[TestPart] = None
    question_index: Optional[int] = None


class TimerResponse(BaseModel):
    """Timer state response"""
    part: TestPart
    total_seconds: int
    remaining_seconds: int
    is_running: bool
    message: Optional[str] = None


@router.post("/start", response_model=StartTestResponse)
async def start_mock_test(
    request: StartTestRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-2.1: Start a new IELTS speaking mock test
    Acceptance Criteria:
    - Clear "Start Test" button on dashboard
    - Pre-test instructions displayed
    - Microphone permission requested
    - Audio quality check before starting
    """
    user_id = current_user.get("user_id") if current_user else "anonymous"
    
    # Get question set based on mode and topic
    question_set = get_question_set(request.test_mode.value, request.topic)
    
    # Create test attempt
    attempt = TestAttempt(
        user_id=user_id,
        test_mode=request.test_mode,
        question_set=question_set,
        current_part=TestPart.PART1 if request.test_mode in [TestMode.FULL, TestMode.PART1_ONLY] else None
    )
    
    # Store attempt
    test_attempts[attempt.id] = attempt
    
    # Calculate estimated duration
    duration_map = {
        TestMode.FULL: 15,
        TestMode.PART1_ONLY: 5,
        TestMode.PART2_ONLY: 4,
        TestMode.PART3_ONLY: 5,
        TestMode.QUICK: 8
    }
    
    # Pre-test instructions
    instructions = """
    Welcome to your IELTS Speaking Mock Test!
    
    Instructions:
    1. Ensure you're in a quiet environment
    2. Test your microphone before starting
    3. Speak clearly and at a natural pace
    4. You'll go through Parts 1, 2, and 3 just like the real test
    5. Timer will guide you through each section
    
    Ready? Let's begin!
    """
    
    return StartTestResponse(
        attempt_id=attempt.id,
        test_mode=request.test_mode,
        question_set=question_set,
        instructions=instructions.strip(),
        estimated_duration_minutes=duration_map[request.test_mode]
    )


@router.get("/attempt/{attempt_id}/current")
async def get_current_question(
    attempt_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get current question in the test
    Implements US-2.2, US-2.3, US-2.4 based on current part
    """
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    attempt = test_attempts[attempt_id]
    
    # Determine current question based on part and index
    current_question = None
    timer_info = None
    
    if attempt.current_part == TestPart.PART1:
        # US-2.2: Part 1 Interview
        if attempt.current_question_index < len(attempt.question_set.part1_questions):
            current_question = attempt.question_set.part1_questions[attempt.current_question_index]
            timer_info = TimerState(
                part=TestPart.PART1,
                total_seconds=30,
                remaining_seconds=30,
                is_running=False
            )
    
    elif attempt.current_part == TestPart.PART2:
        # US-2.3: Part 2 Cue Card
        current_question = attempt.question_set.part2_question
        timer_info = TimerState(
            part=TestPart.PART2,
            total_seconds=180,  # 1 min prep + 2 min speaking
            remaining_seconds=180,
            is_running=False,
            preparation_time=60,
            speaking_time=120
        )
    
    elif attempt.current_part == TestPart.PART3:
        # US-2.4: Part 3 Discussion
        if attempt.current_question_index < len(attempt.question_set.part3_questions):
            current_question = attempt.question_set.part3_questions[attempt.current_question_index]
            timer_info = TimerState(
                part=TestPart.PART3,
                total_seconds=45,
                remaining_seconds=45,
                is_running=False
            )
    
    return {
        "attempt_id": attempt_id,
        "current_part": attempt.current_part,
        "current_question_index": attempt.current_question_index,
        "current_question": current_question,
        "timer": timer_info,
        "is_recording": attempt.is_recording
    }


@router.post("/attempt/{attempt_id}/next")
async def move_to_next_question(
    attempt_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Move to next question or part"""
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    attempt = test_attempts[attempt_id]
    
    # Stop any active recording
    attempt.is_recording = False
    
    # Move to next question/part
    if attempt.current_part == TestPart.PART1:
        attempt.current_question_index += 1
        if attempt.current_question_index >= len(attempt.question_set.part1_questions):
            # Move to Part 2
            attempt.current_part = TestPart.PART2
            attempt.current_question_index = 0
            message = "Moving to Part 2: Cue Card"
        else:
            message = f"Part 1 - Question {attempt.current_question_index + 1}"
    
    elif attempt.current_part == TestPart.PART2:
        # Move to Part 3
        attempt.current_part = TestPart.PART3
        attempt.current_question_index = 0
        message = "Moving to Part 3: Discussion"
    
    elif attempt.current_part == TestPart.PART3:
        attempt.current_question_index += 1
        if attempt.current_question_index >= len(attempt.question_set.part3_questions):
            # Test completed
            attempt.completed_at = datetime.utcnow()
            message = "Test completed! Well done!"
        else:
            message = f"Part 3 - Question {attempt.current_question_index + 1}"
    else:
        message = "Test completed"
    
    return {
        "status": "success",
        "message": message,
        "current_part": attempt.current_part,
        "current_question_index": attempt.current_question_index,
        "is_completed": attempt.completed_at is not None
    }


@router.post("/attempt/{attempt_id}/recording")
async def manage_recording(
    attempt_id: str,
    request: RecordingRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    US-2.5: Voice Recording management
    Acceptance Criteria:
    - High-quality audio recording (16kHz minimum)
    - Background noise detection and warning
    - Pause/resume functionality
    - Auto-stop when time limit reached
    """
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    attempt = test_attempts[attempt_id]
    
    if request.action == "start":
        # Start recording
        session = RecordingSession(
            attempt_id=attempt_id,
            part=attempt.current_part,
            question_index=attempt.current_question_index
        )
        
        session_id = f"{attempt_id}_{attempt.current_part}_{attempt.current_question_index}"
        recording_sessions[session_id] = session
        attempt.is_recording = True
        
        return {
            "status": "recording_started",
            "session_id": session_id,
            "part": attempt.current_part,
            "message": "Recording started. Speak clearly into your microphone."
        }
    
    elif request.action == "stop":
        # Stop recording
        attempt.is_recording = False
        session_id = f"{attempt_id}_{attempt.current_part}_{attempt.current_question_index}"
        
        if session_id in recording_sessions:
            session = recording_sessions[session_id]
            session.is_completed = True
            session.duration_seconds = (datetime.utcnow() - session.started_at).seconds
            
            # Simulate audio URL (in production, this would be actual upload)
            session.audio_url = f"/audio/{session_id}.webm"
            attempt.recordings[session_id] = session.dict()
        
        return {
            "status": "recording_stopped",
            "session_id": session_id,
            "duration_seconds": session.duration_seconds if session_id in recording_sessions else 0,
            "message": "Recording saved successfully."
        }
    
    elif request.action == "pause":
        attempt.is_recording = False
        return {"status": "recording_paused", "message": "Recording paused."}
    
    elif request.action == "resume":
        attempt.is_recording = True
        return {"status": "recording_resumed", "message": "Recording resumed."}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


@router.post("/attempt/{attempt_id}/timer/{part}")
async def start_timer(
    attempt_id: str,
    part: TestPart,
    background_tasks: BackgroundTasks,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Timer management for each part
    US-2.2: 30-second timer per Part 1 question
    US-2.3: 1-minute prep + 2-minute speaking for Part 2
    US-2.4: 45-second timer per Part 3 question
    """
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    # Define timer durations
    timer_config = {
        TestPart.PART1: {"total": 30, "message": "30 seconds per question"},
        TestPart.PART2: {"total": 180, "prep": 60, "speak": 120, "message": "1 minute preparation, 2 minutes speaking"},
        TestPart.PART3: {"total": 45, "message": "45 seconds per question"}
    }
    
    config = timer_config[part]
    timer = TimerState(
        part=part,
        total_seconds=config["total"],
        remaining_seconds=config["total"],
        is_running=True,
        started_at=datetime.utcnow()
    )
    
    if part == TestPart.PART2:
        timer.preparation_time = config["prep"]
        timer.speaking_time = config["speak"]
    
    timer_id = f"{attempt_id}_{part}"
    timers[timer_id] = timer
    
    # Simulate timer countdown (in production, use WebSocket)
    async def countdown():
        while timer.remaining_seconds > 0 and timer.is_running:
            await asyncio.sleep(1)
            timer.remaining_seconds -= 1
            
            # Special handling for Part 2 transition
            if part == TestPart.PART2 and timer.remaining_seconds == 120:
                timer.message = "Preparation time ended. Please start speaking now."
    
    background_tasks.add_task(countdown)
    
    return TimerResponse(
        part=timer.part,
        total_seconds=timer.total_seconds,
        remaining_seconds=timer.remaining_seconds,
        is_running=timer.is_running,
        message=config["message"]
    )


@router.get("/attempt/{attempt_id}/timer/{part}", response_model=TimerResponse)
async def get_timer_status(
    attempt_id: str,
    part: TestPart,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get current timer status"""
    timer_id = f"{attempt_id}_{part}"
    
    if timer_id not in timers:
        return TimerResponse(
            part=part,
            total_seconds=0,
            remaining_seconds=0,
            is_running=False,
            message="Timer not started"
        )
    
    timer = timers[timer_id]
    
    # Add contextual messages
    message = None
    if timer.remaining_seconds <= 10 and timer.remaining_seconds > 0:
        message = f"⚠️ {timer.remaining_seconds} seconds remaining!"
    elif timer.remaining_seconds == 0:
        message = "⏰ Time's up!"
    
    return TimerResponse(
        part=timer.part,
        total_seconds=timer.total_seconds,
        remaining_seconds=timer.remaining_seconds,
        is_running=timer.is_running,
        message=message
    )


@router.post("/upload-audio")
async def upload_audio(
    attempt_id: str = Form(...),
    part: str = Form(...),
    question_index: int = Form(...),
    audio_file: UploadFile = File(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Upload audio recording for a test attempt
    """
    # Validate attempt exists
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    # Validate file type
    if not audio_file.filename.endswith(('.m4a', '.mp3', '.wav', '.aac')):
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/audio"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = audio_file.filename.split('.')[-1]
    filename = f"{attempt_id}_{part}_q{question_index}_{timestamp}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save the file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio file: {str(e)}")
    
    # Store file info in attempt recordings
    attempt = test_attempts[attempt_id]
    recording_id = str(uuid.uuid4())
    
    if not hasattr(attempt, 'audio_files'):
        attempt.audio_files = {}
    
    attempt.audio_files[recording_id] = {
        "id": recording_id,
        "part": part,
        "question_index": question_index,
        "file_path": file_path,
        "filename": filename,
        "size_bytes": len(content),
        "uploaded_at": datetime.utcnow().isoformat(),
        "duration_seconds": None  # Will be calculated when processing
    }
    
    return {
        "message": "Audio uploaded successfully",
        "recording_id": recording_id,
        "filename": filename,
        "size_bytes": len(content),
        "file_path": file_path
    }


@router.get("/attempt/{attempt_id}/summary")
async def get_test_summary(
    attempt_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get test attempt summary"""
    if attempt_id not in test_attempts:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    attempt = test_attempts[attempt_id]
    
    # Calculate duration
    duration = None
    if attempt.completed_at:
        duration = (attempt.completed_at - attempt.started_at).seconds
    
    return {
        "attempt_id": attempt_id,
        "test_mode": attempt.test_mode,
        "started_at": attempt.started_at,
        "completed_at": attempt.completed_at,
        "duration_seconds": duration,
        "total_questions": (
            len(attempt.question_set.part1_questions) +
            (1 if attempt.question_set.part2_question else 0) +
            len(attempt.question_set.part3_questions)
        ),
        "recordings_count": len(attempt.recordings),
        "is_completed": attempt.completed_at is not None
    }
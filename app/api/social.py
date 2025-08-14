"""
Epic 7: Social & Community Features API Endpoints
US-7.1: Share Results
US-7.2: Leaderboards
US-7.3: Study Groups
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import random
from ..models.social_models import (
    ScoreCard,
    SocialShare,
    LeaderboardEntry,
    Leaderboard,
    StudyGroup,
    StudyGroupMember,
    GroupChallenge,
    GroupMessage,
    UserSocialSettings,
    SharePlatform,
    PrivacyLevel,
    LeaderboardPeriod,
    StudyGroupRole,
    GroupMessageType,
    CreateScoreCardRequest,
    ShareScoreRequest,
    LeaderboardRequest,
    CreateStudyGroupRequest,
    JoinStudyGroupRequest,
    GroupMessageRequest,
    UpdateSocialSettingsRequest,
    ScoreCardResponse,
    LeaderboardResponse,
    StudyGroupResponse,
    SocialStatsResponse
)
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/social", tags=["Social & Community Features"])

# Mock data stores (replace with actual database in production)
score_cards_db: List[ScoreCard] = []
social_shares_db: List[SocialShare] = []
leaderboards_db: List[Leaderboard] = []
study_groups_db: List[StudyGroup] = []
group_members_db: List[StudyGroupMember] = []
group_challenges_db: List[GroupChallenge] = []
group_messages_db: List[GroupMessage] = []
social_settings_db: Dict[str, UserSocialSettings] = {}

@router.post("/score-card", response_model=ScoreCardResponse)
async def create_score_card(
    request: CreateScoreCardRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-7.1: Share Results
    Create a shareable score card from test results
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Mock test attempt data (in real app, fetch from test attempts)
    mock_test_data = {
        "overall_band": random.uniform(6.0, 8.5),
        "fluency_coherence": random.uniform(6.0, 8.5),
        "lexical_resource": random.uniform(6.0, 8.5),
        "grammatical_range_accuracy": random.uniform(6.0, 8.5),
        "pronunciation": random.uniform(6.0, 8.5),
        "test_date": datetime.utcnow()
    }
    
    # Create score card
    score_card = ScoreCard(
        user_id=user_id,
        test_attempt_id=request.test_attempt_id,
        overall_band=mock_test_data["overall_band"],
        fluency_coherence=mock_test_data["fluency_coherence"],
        lexical_resource=mock_test_data["lexical_resource"],
        grammatical_range_accuracy=mock_test_data["grammatical_range_accuracy"],
        pronunciation=mock_test_data["pronunciation"],
        test_date=mock_test_data["test_date"],
        achievement_title=request.achievement_title,
        card_template=request.card_template,
        privacy_level=request.privacy_level,
        show_detailed_scores=request.show_detailed_scores
    )
    
    # Generate mock image URL
    score_card.image_url = f"https://qanotai.com/api/cards/{score_card.id}/image"
    
    score_cards_db.append(score_card)
    
    # Generate platform-specific share URLs
    share_urls = {
        "whatsapp": f"https://wa.me/?text=Check out my IELTS score! {score_card.image_url}",
        "instagram": f"https://instagram.com/share?url={score_card.image_url}",
        "facebook": f"https://facebook.com/sharer/sharer.php?u={score_card.image_url}",
        "twitter": f"https://twitter.com/intent/tweet?url={score_card.image_url}&text=Just got {score_card.overall_band} on IELTS Speaking! 🎉",
        "telegram": f"https://t.me/share/url?url={score_card.image_url}"
    }
    
    return ScoreCardResponse(
        score_card=score_card,
        image_url=score_card.image_url,
        share_urls=share_urls
    )

@router.post("/share")
async def share_score_card(
    request: ShareScoreRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-7.1: Share Results
    Share a score card to social media platforms
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find the score card
    score_card = None
    for sc in score_cards_db:
        if sc.id == request.score_card_id and sc.user_id == user_id:
            score_card = sc
            break
    
    if not score_card:
        raise HTTPException(status_code=404, detail="Score card not found")
    
    # Create share records for each platform
    shares_created = []
    for platform in request.platforms:
        social_share = SocialShare(
            user_id=user_id,
            score_card_id=score_card.id,
            platform=platform,
            privacy_level=request.privacy_level or score_card.privacy_level,
            share_successful=True  # Mock success
        )
        social_shares_db.append(social_share)
        shares_created.append({
            "platform": platform,
            "share_id": social_share.id,
            "status": "success"
        })
    
    # Update score card share count
    score_card.share_count += len(request.platforms)
    
    return {
        "message": "Score card shared successfully",
        "shares": shares_created,
        "total_shares": score_card.share_count
    }

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: LeaderboardPeriod = Query(LeaderboardPeriod.WEEKLY),
    region: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-7.2: Leaderboards
    Get leaderboard rankings for specified period and region
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find or create leaderboard
    leaderboard = _get_or_create_leaderboard(period, region, country)
    
    # Generate mock leaderboard data if empty
    if not leaderboard or not leaderboard.entries:
        leaderboard = _generate_mock_leaderboard(period, region, country, limit)
        leaderboards_db.append(leaderboard)
    
    # Find user's position
    user_rank = None
    user_entry = None
    for entry in leaderboard.entries:
        if entry.user_id == user_id:
            user_rank = entry.rank
            user_entry = entry
            break
    
    # Calculate rank change (mock)
    rank_change = random.randint(-5, 10) if user_rank else None
    
    # Limit entries for response
    limited_entries = leaderboard.entries[:limit]
    leaderboard.entries = limited_entries
    
    return LeaderboardResponse(
        leaderboard=leaderboard,
        user_rank=user_rank,
        user_entry=user_entry,
        rank_change=rank_change
    )

@router.get("/study-groups")
async def get_study_groups(
    search: Optional[str] = Query(None),
    public_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=50),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-7.3: Study Groups
    Browse available study groups
    """
    # Filter groups
    filtered_groups = study_groups_db.copy()
    
    if public_only:
        filtered_groups = [g for g in filtered_groups if g.is_public and g.is_active]
    
    if search:
        search_lower = search.lower()
        filtered_groups = [
            g for g in filtered_groups 
            if (search_lower in g.name.lower() or 
                search_lower in g.description.lower() or
                any(search_lower in area.lower() for area in g.focus_areas))
        ]
    
    # Sort by member count and activity
    filtered_groups.sort(key=lambda x: (x.member_count, x.total_tests_completed), reverse=True)
    
    return {
        "groups": filtered_groups[:limit],
        "total_count": len(filtered_groups)
    }

@router.post("/study-groups", response_model=StudyGroupResponse)
async def create_study_group(
    request: CreateStudyGroupRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-7.3: Study Groups
    Create a new study group
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Create study group
    study_group = StudyGroup(
        name=request.name,
        description=request.description,
        is_public=request.is_public,
        requires_approval=request.requires_approval,
        target_band_score=request.target_band_score,
        target_test_date=request.target_test_date,
        focus_areas=request.focus_areas,
        member_count=1  # Creator is first member
    )
    
    study_groups_db.append(study_group)
    
    # Add creator as owner
    creator_member = StudyGroupMember(
        group_id=study_group.id,
        user_id=user_id,
        role=StudyGroupRole.OWNER,
        display_name=current_user.get("display_name", "User")
    )
    group_members_db.append(creator_member)
    
    # Create welcome message
    welcome_message = GroupMessage(
        group_id=study_group.id,
        user_id=user_id,
        message_type=GroupMessageType.SYSTEM,
        content=f"Welcome to {study_group.name}! Let's achieve our IELTS goals together! 🎯",
        sender_name="System",
        is_system_message=True
    )
    group_messages_db.append(welcome_message)
    
    return StudyGroupResponse(
        group=study_group,
        members=[creator_member],
        recent_messages=[welcome_message],
        active_challenges=[],
        user_role=StudyGroupRole.OWNER
    )

@router.get("/study-groups/{group_id}", response_model=StudyGroupResponse)
async def get_study_group_details(
    group_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed information about a study group
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find study group
    study_group = None
    for sg in study_groups_db:
        if sg.id == group_id:
            study_group = sg
            break
    
    if not study_group:
        raise HTTPException(status_code=404, detail="Study group not found")
    
    # Get group members
    members = [m for m in group_members_db if m.group_id == group_id and m.is_active]
    
    # Get recent messages
    recent_messages = [
        m for m in group_messages_db 
        if m.group_id == group_id and not m.is_deleted
    ][-20:]  # Last 20 messages
    
    # Get active challenges
    active_challenges = [
        c for c in group_challenges_db 
        if c.group_id == group_id and not c.is_completed and c.end_date >= date.today()
    ]
    
    # Get user's role
    user_role = None
    for member in members:
        if member.user_id == user_id:
            user_role = member.role
            break
    
    return StudyGroupResponse(
        group=study_group,
        members=members,
        recent_messages=recent_messages,
        active_challenges=active_challenges,
        user_role=user_role
    )

@router.post("/study-groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    request: JoinStudyGroupRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Join a study group
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find study group
    study_group = None
    for sg in study_groups_db:
        if sg.id == group_id or (request.group_code and sg.group_code == request.group_code):
            study_group = sg
            break
    
    if not study_group:
        raise HTTPException(status_code=404, detail="Study group not found")
    
    # Check if user is already a member
    existing_member = None
    for member in group_members_db:
        if member.group_id == study_group.id and member.user_id == user_id:
            existing_member = member
            break
    
    if existing_member and existing_member.is_active:
        raise HTTPException(status_code=400, detail="Already a member of this group")
    
    # Check capacity
    if study_group.member_count >= study_group.max_members:
        raise HTTPException(status_code=400, detail="Group is full")
    
    # Create membership
    new_member = StudyGroupMember(
        group_id=study_group.id,
        user_id=user_id,
        display_name=current_user.get("display_name", "User")
    )
    
    group_members_db.append(new_member)
    study_group.member_count += 1
    
    # Create join message
    join_message = GroupMessage(
        group_id=study_group.id,
        user_id=user_id,
        message_type=GroupMessageType.SYSTEM,
        content=f"{new_member.display_name} joined the group! 👋",
        sender_name="System",
        is_system_message=True
    )
    group_messages_db.append(join_message)
    
    return {
        "message": "Successfully joined the study group",
        "group_name": study_group.name,
        "member_count": study_group.member_count,
        "role": new_member.role
    }

@router.post("/study-groups/{group_id}/messages")
async def send_group_message(
    group_id: str,
    request: GroupMessageRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Send a message to the group chat
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Verify user is a member
    member = None
    for m in group_members_db:
        if m.group_id == group_id and m.user_id == user_id and m.is_active:
            member = m
            break
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Create message
    message = GroupMessage(
        group_id=group_id,
        user_id=user_id,
        message_type=request.message_type,
        content=request.content,
        score_card_id=request.score_card_id,
        sender_name=member.display_name
    )
    
    group_messages_db.append(message)
    
    # Update member contribution count
    member.contributions_count += 1
    
    return {
        "message": "Message sent successfully",
        "message_id": message.id,
        "timestamp": message.created_at
    }

@router.get("/study-groups/{group_id}/messages")
async def get_group_messages(
    group_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[datetime] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get group chat messages
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Verify user is a member
    member = None
    for m in group_members_db:
        if m.group_id == group_id and m.user_id == user_id and m.is_active:
            member = m
            break
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Get messages
    messages = [
        m for m in group_messages_db 
        if m.group_id == group_id and not m.is_deleted
    ]
    
    # Filter by timestamp if specified
    if before:
        messages = [m for m in messages if m.created_at < before]
    
    # Sort by timestamp (newest first) and limit
    messages.sort(key=lambda x: x.created_at, reverse=True)
    messages = messages[:limit]
    
    return {
        "messages": messages,
        "total_count": len(messages),
        "has_more": len(messages) == limit
    }

@router.get("/settings")
async def get_social_settings(current_user: Dict = Depends(get_current_user)):
    """
    Get user's social and privacy settings
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create settings
    if user_id not in social_settings_db:
        social_settings_db[user_id] = UserSocialSettings(user_id=user_id)
    
    settings = social_settings_db[user_id]
    return settings

@router.put("/settings")
async def update_social_settings(
    request: UpdateSocialSettingsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Update user's social and privacy settings
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create settings
    if user_id not in social_settings_db:
        social_settings_db[user_id] = UserSocialSettings(user_id=user_id)
    
    settings = social_settings_db[user_id]
    
    # Update fields if provided
    if request.participate_in_leaderboards is not None:
        settings.participate_in_leaderboards = request.participate_in_leaderboards
    
    if request.show_anonymous is not None:
        settings.show_anonymous = request.show_anonymous
    
    if request.auto_share_achievements is not None:
        settings.auto_share_achievements = request.auto_share_achievements
    
    if request.default_privacy_level is not None:
        settings.default_privacy_level = request.default_privacy_level
    
    settings.updated_at = datetime.utcnow()
    
    return {
        "message": "Settings updated successfully",
        "settings": settings
    }

@router.get("/stats", response_model=SocialStatsResponse)
async def get_social_stats(current_user: Dict = Depends(get_current_user)):
    """
    Get user's social engagement statistics
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Calculate stats
    total_shares = len([s for s in social_shares_db if s.user_id == user_id])
    
    # Find leaderboard rank
    leaderboard_rank = None
    for lb in leaderboards_db:
        for entry in lb.entries:
            if entry.user_id == user_id:
                leaderboard_rank = entry.rank
                break
        if leaderboard_rank:
            break
    
    # Count study groups
    study_groups_count = len([m for m in group_members_db if m.user_id == user_id and m.is_active])
    
    # Count achievements shared (mock)
    achievements_shared = len([s for s in social_shares_db if s.user_id == user_id])
    
    # Calculate social score (mock algorithm)
    social_score = min(100.0, (total_shares * 10) + (study_groups_count * 20) + (achievements_shared * 15))
    
    return SocialStatsResponse(
        total_shares=total_shares,
        leaderboard_rank=leaderboard_rank,
        study_groups_count=study_groups_count,
        achievements_shared=achievements_shared,
        social_score=social_score
    )

@router.get("/my-groups")
async def get_my_study_groups(current_user: Dict = Depends(get_current_user)):
    """
    Get user's study groups
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find user's group memberships
    user_memberships = [m for m in group_members_db if m.user_id == user_id and m.is_active]
    
    # Get the corresponding groups
    user_groups = []
    for membership in user_memberships:
        for group in study_groups_db:
            if group.id == membership.group_id:
                group_info = {
                    "group": group,
                    "membership": membership,
                    "unread_messages": _count_unread_messages(group.id, user_id),
                    "active_challenges": len([c for c in group_challenges_db if c.group_id == group.id and not c.is_completed])
                }
                user_groups.append(group_info)
                break
    
    return {
        "groups": user_groups,
        "total_count": len(user_groups)
    }

# Helper functions

def _get_or_create_leaderboard(period: LeaderboardPeriod, region: Optional[str], country: Optional[str]) -> Optional[Leaderboard]:
    """Find existing leaderboard or return None"""
    for lb in leaderboards_db:
        if (lb.period == period and 
            lb.region == region and 
            lb.country == country):
            return lb
    return None

def _generate_mock_leaderboard(period: LeaderboardPeriod, region: Optional[str], country: Optional[str], limit: int) -> Leaderboard:
    """Generate mock leaderboard data"""
    
    # Calculate date range
    today = date.today()
    if period == LeaderboardPeriod.WEEKLY:
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == LeaderboardPeriod.MONTHLY:
        start_date = today - timedelta(days=30)
        end_date = today
    else:  # ALL_TIME
        start_date = date(2023, 1, 1)
        end_date = today
    
    # Generate mock entries
    entries = []
    for i in range(min(limit, 50)):  # Limit to 50 entries
        score = random.uniform(8.5, 6.0)  # Decreasing scores
        entry = LeaderboardEntry(
            user_id=f"user_{i+1}",
            display_name=f"Anonymous {i+1}" if random.choice([True, False]) else f"User{i+1}",
            is_anonymous=random.choice([True, False]),
            rank=i+1,
            score=round(score, 1),
            total_tests=random.randint(5, 50),
            tests_this_period=random.randint(1, 10),
            improvement_trend=random.uniform(-0.5, 1.0),
            country=country or random.choice(["Uzbekistan", "Kazakhstan", "Turkey", "India"]),
            badges_count=random.randint(0, 10),
            streak_days=random.randint(0, 30)
        )
        entries.append(entry)
    
    leaderboard = Leaderboard(
        period=period,
        region=region,
        country=country,
        start_date=start_date,
        end_date=end_date,
        entries=entries,
        total_participants=len(entries),
        average_score=sum(e.score for e in entries) / len(entries) if entries else 0.0,
        highest_score=max(e.score for e in entries) if entries else 0.0,
        next_update=datetime.utcnow() + timedelta(hours=24)
    )
    
    return leaderboard

def _count_unread_messages(group_id: str, user_id: str) -> int:
    """Count unread messages for user in group (mock implementation)"""
    # In real implementation, this would track last read timestamp
    return random.randint(0, 5)

# Initialize some sample data
def _initialize_sample_social_data():
    """Initialize sample social data"""
    global study_groups_db
    
    if not study_groups_db:
        # Create sample study groups
        sample_groups = [
            {
                "name": "IELTS Band 7 Achievers",
                "description": "For serious learners targeting Band 7 and above. Daily practice and mutual support!",
                "target_band_score": 7.0,
                "focus_areas": ["fluency", "pronunciation"],
                "member_count": 15
            },
            {
                "name": "Beginner Friendly Group",
                "description": "Perfect for IELTS beginners. We help each other learn the basics!",
                "target_band_score": 6.0,
                "focus_areas": ["vocabulary", "grammar"],
                "member_count": 8
            },
            {
                "name": "Advanced Speakers Club",
                "description": "For advanced learners pushing towards Band 8+. Challenging practice sessions.",
                "target_band_score": 8.0,
                "focus_areas": ["advanced_vocabulary", "complex_grammar"],
                "member_count": 12
            }
        ]
        
        for group_data in sample_groups:
            group = StudyGroup(**group_data)
            study_groups_db.append(group)

# Initialize sample data
_initialize_sample_social_data()
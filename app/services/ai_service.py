"""
AI Services for Epic 3: Speech Transcription and Scoring
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from app.models.scoring_models import (
    Transcript, TranscriptSegment, BandScore, 
    FeedbackReport, LanguageAnalysis
)
from app.core.config import settings
from app.services.openai_service import openai_service
import logging
import tempfile

logger = logging.getLogger(__name__)


class TranscriptionService:
    """US-3.1: Speech Transcription Service"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.provider = settings.STT_PROVIDER
        
    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Transcript:
        """
        Transcribe audio using Whisper or alternative
        Acceptance Criteria:
        - Transcription appears within 3 seconds after speaking
        - Accuracy rate >90% for clear speech
        - Highlights uncertain words
        - Supports Uzbek-accented English
        """
        start_time = datetime.utcnow()
        
        if self.provider == "openai" and self.openai_key:
            transcript = await self._transcribe_with_whisper(audio_data, language)
        else:
            # Fallback to mock transcription for demo
            transcript = await self._mock_transcription()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        transcript.processing_time_seconds = processing_time
        
        # Analyze transcript
        transcript = self._analyze_transcript(transcript)
        
        return transcript
    
    async def _transcribe_with_whisper(self, audio_data: bytes, language: str) -> Transcript:
        """Transcribe using OpenAI Whisper"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            try:
                # Use the OpenAI service for transcription
                result = await openai_service.transcribe_audio(tmp_file_path)
                
                # Parse Whisper response
                transcript = Transcript(
                    attempt_id="",
                    part="",
                    question_index=0,
                    text=result.get("text", ""),
                    confidence=0.9,  # Whisper doesn't provide overall confidence
                    transcription_service="openai-whisper",
                    model_version="whisper-1"
                )
                
                # Parse segments if available
                if "segments" in result:
                    for seg in result["segments"]:
                        segment = TranscriptSegment(
                            text=seg.get("text", ""),
                            confidence=0.9,  # Default confidence
                            start_time=seg.get("start", 0),
                            end_time=seg.get("end", 0),
                            words=seg.get("words", [])
                        )
                        transcript.segments.append(segment)
                
                return transcript
            finally:
                # Clean up temp file
                import os
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return await self._mock_transcription()
    
    async def _mock_transcription(self) -> Transcript:
        """Mock transcription for demo/testing"""
        sample_text = """
        Well, I really enjoy living in my hometown because it has a perfect balance 
        between modern amenities and traditional culture. Um, the people are very 
        friendly and welcoming, you know, and there are many parks where I can relax. 
        The food is absolutely delicious, especially our local dishes.
        """
        
        transcript = Transcript(
            attempt_id="mock",
            part="part1",
            question_index=0,
            text=sample_text.strip(),
            confidence=0.92,
            word_count=len(sample_text.split()),
            transcription_service="mock",
            model_version="demo-1.0"
        )
        
        # Add mock segments
        words = sample_text.split()
        segment_size = 10
        for i in range(0, len(words), segment_size):
            segment = TranscriptSegment(
                text=" ".join(words[i:i+segment_size]),
                confidence=0.90 + (i % 3) * 0.03,
                start_time=i * 1.5,
                end_time=(i + segment_size) * 1.5
            )
            transcript.segments.append(segment)
        
        return transcript
    
    def _analyze_transcript(self, transcript: Transcript) -> Transcript:
        """Analyze transcript for language features"""
        text = transcript.text.lower()
        words = text.split()
        
        # Count words and calculate WPM
        transcript.word_count = len(words)
        transcript.unique_words = len(set(words))
        
        # Assuming average speaking duration
        duration_seconds = 30  # Default for Part 1 question
        transcript.words_per_minute = (len(words) / duration_seconds) * 60
        
        # Detect filler words
        filler_words = ["um", "uh", "err", "like", "you know", "actually", "basically"]
        transcript.filler_words = [w for w in words if w in filler_words]
        
        # Count hesitations (simplified)
        transcript.hesitations = text.count("...") + text.count("um") + text.count("uh")
        
        return transcript


class ScoringService:
    """US-3.2: Band Score Prediction Service"""
    
    def __init__(self):
        self.ai_provider = settings.AI_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        
    async def calculate_band_score(
        self, 
        transcripts: List[Transcript],
        target_band: Optional[float] = None
    ) -> BandScore:
        """
        Calculate IELTS band score using AI
        Acceptance Criteria:
        - Overall band score (0-9) displayed prominently
        - Individual scores for Fluency, Lexical, Grammar, Pronunciation
        - Score breakdown with explanations
        - Comparison to target band score
        """
        if self.ai_provider == "openai" and self.openai_key:
            score = await self._score_with_gpt(transcripts)
        elif self.ai_provider == "anthropic" and self.anthropic_key:
            score = await self._score_with_claude(transcripts)
        else:
            score = await self._mock_scoring(transcripts)
        
        # Add target comparison
        if target_band:
            score.target_band = target_band
            score.gap_to_target = target_band - score.overall_band
        
        return score
    
    async def _score_with_gpt(self, transcripts: List[Transcript]) -> BandScore:
        """Score using GPT-4"""
        try:
            # Combine all transcripts into a single response
            combined_transcript = "\n\n".join([
                f"Part {t.part} - Question {t.question_index + 1}:\n{t.text}"
                for t in transcripts
            ])
            
            # Use OpenAI service for assessment
            # For simplicity, using a generic question
            question = "IELTS Speaking Test Response"
            part = "full_test" if len(transcripts) > 1 else transcripts[0].part
            
            result = await openai_service.assess_ielts_response(
                transcript=combined_transcript,
                question=question,
                part=part,
                target_band=7.0  # Default target
            )
            
            return BandScore(
                attempt_id=transcripts[0].attempt_id if transcripts else "",
                overall_band=float(result.get("overall_band", 6.0)),
                fluency_coherence=float(result.get("fluency_coherence", 6.0)),
                lexical_resource=float(result.get("lexical_resource", 6.0)),
                grammatical_range_accuracy=float(result.get("grammatical_range", 6.0)),
                pronunciation=float(result.get("pronunciation", 6.0)),
                scoring_model="gpt-4-turbo",
                scoring_version="2024-01",
                confidence_level=0.85
            )
            
        except Exception as e:
            logger.error(f"GPT scoring failed: {e}")
            return await self._mock_scoring(transcripts)
    
    async def _mock_scoring(self, transcripts: List[Transcript]) -> BandScore:
        """Mock scoring for demo/testing"""
        # Simulate scoring based on transcript quality
        base_score = 6.0
        
        if transcripts:
            # Adjust based on word count and variety
            avg_words = sum(t.word_count for t in transcripts) / len(transcripts)
            if avg_words > 50:
                base_score += 0.5
            if avg_words > 80:
                base_score += 0.5
            
            # Adjust based on filler words
            total_fillers = sum(len(t.filler_words) for t in transcripts)
            if total_fillers < 3:
                base_score += 0.5
            elif total_fillers > 10:
                base_score -= 0.5
        
        # Ensure score is within range
        base_score = min(9.0, max(4.0, base_score))
        
        return BandScore(
            attempt_id=transcripts[0].attempt_id if transcripts else "mock",
            overall_band=base_score,
            fluency_coherence=base_score + 0.5,
            lexical_resource=base_score - 0.5,
            grammatical_range_accuracy=base_score,
            pronunciation=base_score + 0.5,
            part1_score=base_score,
            part2_score=base_score - 0.5,
            part3_score=base_score + 0.5,
            scoring_model="mock",
            scoring_version="demo-1.0",
            confidence_level=0.75
        )
    
    def _get_system_prompt(self) -> str:
        """System prompt for IELTS scoring"""
        return """
        You are an experienced IELTS Speaking examiner. Score the candidate's response 
        according to official IELTS band descriptors. Provide scores for:
        1. Fluency and Coherence (0-9)
        2. Lexical Resource (0-9)
        3. Grammatical Range and Accuracy (0-9)
        4. Pronunciation (0-9)
        5. Overall Band Score (0-9)
        
        Return scores in JSON format with keys:
        overall_band, fluency_coherence, lexical_resource, 
        grammatical_range_accuracy, pronunciation
        """
    
    def _create_scoring_prompt(self, transcripts: List[Transcript]) -> str:
        """Create prompt for AI scoring"""
        parts = []
        for i, transcript in enumerate(transcripts):
            parts.append(f"Part {transcript.part} Response {i+1}:\n{transcript.text}\n")
        
        return f"""
        Score this IELTS Speaking test response:
        
        {' '.join(parts)}
        
        Provide band scores (0-9 with 0.5 increments) in JSON format.
        """


class FeedbackService:
    """US-3.3 & US-3.4: Feedback and Analysis Service"""
    
    async def generate_feedback(
        self,
        score: BandScore,
        transcripts: List[Transcript]
    ) -> FeedbackReport:
        """
        Generate detailed feedback report
        Acceptance Criteria:
        - Strengths highlighted in green
        - Areas for improvement in amber/red
        - Specific examples from responses
        - Actionable improvement suggestions
        """
        report = FeedbackReport(
            attempt_id=score.attempt_id,
            score_id=score.id,
            summary=self._generate_summary(score),
            overall_impression=self._generate_impression(score)
        )
        
        # Generate strengths and improvements
        report.strengths = self._identify_strengths(score, transcripts)
        report.improvements = self._identify_improvements(score, transcripts)
        
        # Generate criterion-specific feedback
        report.fluency_feedback = self._fluency_feedback(score.fluency_coherence)
        report.lexical_feedback = self._lexical_feedback(score.lexical_resource)
        report.grammar_feedback = self._grammar_feedback(score.grammatical_range_accuracy)
        report.pronunciation_feedback = self._pronunciation_feedback(score.pronunciation)
        
        # Action items
        report.action_items = self._generate_action_items(score)
        report.recommended_practice = self._recommend_practice(score)
        report.estimated_improvement_time = self._estimate_improvement_time(score)
        
        return report
    
    async def analyze_language(
        self,
        transcript: Transcript
    ) -> LanguageAnalysis:
        """
        Analyze grammar and vocabulary
        Acceptance Criteria:
        - Grammar errors identified with corrections
        - Vocabulary range assessment
        - Suggestions for better word choices
        - Common Uzbek learner mistakes highlighted
        """
        analysis = LanguageAnalysis(
            attempt_id=transcript.attempt_id,
            transcript_id=transcript.id
        )
        
        # Mock analysis for demo
        text = transcript.text
        words = text.split()
        
        # Vocabulary analysis
        analysis.vocabulary_range = self._assess_vocabulary_range(words)
        analysis.lexical_diversity = len(set(words)) / len(words) if words else 0
        
        # Grammar analysis (simplified)
        analysis.grammar_errors = self._detect_grammar_errors(text)
        analysis.grammar_accuracy_percentage = 85.0  # Mock value
        
        # Uzbek learner specific
        analysis.common_l1_interference = [
            "Article usage (a/an/the)",
            "Present perfect vs past simple",
            "Preposition choice"
        ]
        
        analysis.recommended_focus_areas = [
            "Practice using articles correctly",
            "Study phrasal verbs",
            "Improve pronunciation of 'th' sounds"
        ]
        
        return analysis
    
    def _generate_summary(self, score: BandScore) -> str:
        """Generate summary based on score"""
        if score.overall_band >= 7.0:
            return "Excellent performance! You demonstrate strong English speaking skills."
        elif score.overall_band >= 6.0:
            return "Good performance with room for improvement in specific areas."
        elif score.overall_band >= 5.0:
            return "Adequate performance. Focus on expanding vocabulary and improving fluency."
        else:
            return "Basic communication achieved. Significant practice needed in all areas."
    
    def _generate_impression(self, score: BandScore) -> str:
        """Generate overall impression"""
        return f"""
        Your current speaking level is Band {score.overall_band}. 
        You show particular strength in {self._get_strongest_area(score)} 
        while {self._get_weakest_area(score)} needs the most attention.
        """
    
    def _get_strongest_area(self, score: BandScore) -> str:
        """Identify strongest criterion"""
        scores = {
            "fluency": score.fluency_coherence,
            "vocabulary": score.lexical_resource,
            "grammar": score.grammatical_range_accuracy,
            "pronunciation": score.pronunciation
        }
        return max(scores, key=scores.get)
    
    def _get_weakest_area(self, score: BandScore) -> str:
        """Identify weakest criterion"""
        scores = {
            "fluency": score.fluency_coherence,
            "vocabulary": score.lexical_resource,
            "grammar": score.grammatical_range_accuracy,
            "pronunciation": score.pronunciation
        }
        return min(scores, key=scores.get)
    
    def _identify_strengths(self, score: BandScore, transcripts: List[Transcript]) -> List[str]:
        """Identify strengths from performance"""
        strengths = []
        
        if score.fluency_coherence >= 6.5:
            strengths.append("Good fluency with natural speech flow")
        if score.lexical_resource >= 6.5:
            strengths.append("Wide vocabulary range with appropriate word choice")
        if score.grammatical_range_accuracy >= 6.5:
            strengths.append("Complex sentence structures used effectively")
        if score.pronunciation >= 6.5:
            strengths.append("Clear pronunciation with good intonation")
        
        return strengths if strengths else ["Consistent effort throughout the test"]
    
    def _identify_improvements(self, score: BandScore, transcripts: List[Transcript]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        if score.fluency_coherence < 6.0:
            improvements.append("Reduce hesitations and improve speech flow")
        if score.lexical_resource < 6.0:
            improvements.append("Expand vocabulary and use more varied expressions")
        if score.grammatical_range_accuracy < 6.0:
            improvements.append("Work on grammar accuracy and sentence variety")
        if score.pronunciation < 6.0:
            improvements.append("Practice pronunciation of difficult sounds")
        
        return improvements if improvements else ["Maintain consistency across all criteria"]
    
    def _fluency_feedback(self, score: float) -> str:
        """Generate fluency-specific feedback"""
        if score >= 7.0:
            return "Excellent fluency with rare hesitation. Ideas flow naturally."
        elif score >= 6.0:
            return "Generally fluent with occasional self-correction. Work on reducing pauses."
        else:
            return "Noticeable pauses affect fluency. Practice speaking continuously for longer periods."
    
    def _lexical_feedback(self, score: float) -> str:
        """Generate vocabulary-specific feedback"""
        if score >= 7.0:
            return "Good vocabulary range with precise word choices."
        elif score >= 6.0:
            return "Adequate vocabulary for most topics. Try using more idiomatic expressions."
        else:
            return "Limited vocabulary range. Focus on learning topic-specific vocabulary."
    
    def _grammar_feedback(self, score: float) -> str:
        """Generate grammar-specific feedback"""
        if score >= 7.0:
            return "Complex structures used accurately with rare errors."
        elif score >= 6.0:
            return "Mix of simple and complex structures. Some errors don't impede communication."
        else:
            return "Basic structures with frequent errors. Review fundamental grammar rules."
    
    def _pronunciation_feedback(self, score: float) -> str:
        """Generate pronunciation-specific feedback"""
        if score >= 7.0:
            return "Clear pronunciation with natural intonation patterns."
        elif score >= 6.0:
            return "Generally clear with occasional mispronunciation."
        else:
            return "Pronunciation issues affect clarity. Practice individual sounds and word stress."
    
    def _generate_action_items(self, score: BandScore) -> List[str]:
        """Generate specific action items"""
        items = []
        
        if score.fluency_coherence < score.overall_band:
            items.append("Practice speaking for 2 minutes without stopping")
        if score.lexical_resource < score.overall_band:
            items.append("Learn 10 new words daily with example sentences")
        if score.grammatical_range_accuracy < score.overall_band:
            items.append("Complete grammar exercises focusing on complex structures")
        if score.pronunciation < score.overall_band:
            items.append("Record yourself and compare with native speakers")
        
        return items if items else ["Maintain current practice routine"]
    
    def _recommend_practice(self, score: BandScore) -> List[str]:
        """Recommend practice activities"""
        return [
            "Daily 5-minute impromptu speaking on random topics",
            "Watch English news and repeat key phrases",
            "Join online speaking clubs for regular practice",
            "Use QanotAI's daily challenges feature"
        ]
    
    def _estimate_improvement_time(self, score: BandScore) -> str:
        """Estimate time to improve"""
        if score.gap_to_target:
            if score.gap_to_target <= 0.5:
                return "2-4 weeks with intensive practice"
            elif score.gap_to_target <= 1.0:
                return "4-8 weeks with regular practice"
            else:
                return "2-3 months with structured learning"
        return "Continuous practice recommended"
    
    def _assess_vocabulary_range(self, words: List[str]) -> str:
        """Assess vocabulary range"""
        unique_words = len(set(words))
        if unique_words > 100:
            return "excellent"
        elif unique_words > 70:
            return "good"
        elif unique_words > 40:
            return "adequate"
        else:
            return "limited"
    
    def _detect_grammar_errors(self, text: str) -> List[Dict[str, Any]]:
        """Detect common grammar errors (simplified)"""
        errors = []
        
        # Check for article errors (simplified)
        if " a " in text and " a vowel" in text:
            errors.append({
                "error": "a vowel",
                "correction": "an vowel",
                "type": "article"
            })
        
        # Check for subject-verb agreement (simplified)
        if "he have" in text.lower():
            errors.append({
                "error": "he have",
                "correction": "he has",
                "type": "subject-verb agreement"
            })
        
        return errors
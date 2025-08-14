"""
OpenAI Integration Service for QanotAI
Handles Whisper transcription and GPT-4 IELTS assessment
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from pathlib import Path

# Load environment variables
load_dotenv()

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper
        """
        try:
            # Read the audio file
            with open(audio_file_path, "rb") as audio_file:
                # Use Whisper API for transcription
                transcript = await asyncio.to_thread(
                    self.client.audio.transcriptions.create,
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language="en"  # Force English for IELTS
                )
            
            return {
                "text": transcript.text,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                "language": transcript.language if hasattr(transcript, 'language') else "en",
                "segments": transcript.segments if hasattr(transcript, 'segments') else [],
                "words": transcript.words if hasattr(transcript, 'words') else []
            }
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            raise
    
    async def assess_ielts_response(
        self,
        transcript: str,
        question: str,
        part: str,
        target_band: float = 7.0
    ) -> Dict[str, Any]:
        """
        Assess IELTS speaking response using GPT-4
        """
        try:
            # Prepare the assessment prompt
            system_prompt = """You are an expert IELTS Speaking examiner with 20+ years of experience. 
            Assess the following speaking response according to official IELTS criteria:
            1. Fluency and Coherence (FC)
            2. Lexical Resource (LR)
            3. Grammatical Range and Accuracy (GRA)
            4. Pronunciation (P)
            
            Provide scores from 0-9 for each criterion and detailed feedback.
            Return your assessment in JSON format."""
            
            user_prompt = f"""
            IELTS Part: {part}
            Question: {question}
            Target Band Score: {target_band}
            
            Candidate's Response:
            {transcript}
            
            Please provide:
            1. Individual band scores for each criterion (0-9)
            2. Overall band score
            3. Specific strengths (with examples from the response)
            4. Areas for improvement (with specific suggestions)
            5. Detailed feedback for each criterion
            
            Format your response as JSON with this structure:
            {{
                "fluency_coherence": <score>,
                "lexical_resource": <score>,
                "grammatical_range": <score>,
                "pronunciation": <score>,
                "overall_band": <score>,
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"],
                "detailed_feedback": {{
                    "fluency_coherence": "detailed feedback",
                    "lexical_resource": "detailed feedback",
                    "grammatical_range": "detailed feedback",
                    "pronunciation": "detailed feedback"
                }},
                "recommendations": ["recommendation1", "recommendation2"]
            }}
            """
            
            # Call GPT-4 for assessment
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4-turbo-preview",  # Use GPT-4 Turbo for better performance
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent scoring
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            assessment = json.loads(response.choices[0].message.content)
            
            return assessment
            
        except Exception as e:
            print(f"Error assessing IELTS response: {e}")
            # Return a fallback assessment
            return {
                "fluency_coherence": 5.0,
                "lexical_resource": 5.0,
                "grammatical_range": 5.0,
                "pronunciation": 5.0,
                "overall_band": 5.0,
                "strengths": ["Attempted to answer the question"],
                "improvements": ["Could not assess due to technical error"],
                "detailed_feedback": {
                    "fluency_coherence": "Assessment unavailable",
                    "lexical_resource": "Assessment unavailable",
                    "grammatical_range": "Assessment unavailable",
                    "pronunciation": "Assessment unavailable"
                },
                "recommendations": ["Please try again"]
            }
    
    async def generate_ielts_feedback(
        self,
        assessments: List[Dict[str, Any]],
        target_band: float
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feedback for the entire test
        """
        try:
            # Prepare feedback prompt
            prompt = f"""
            Based on the following IELTS Speaking test assessments, provide comprehensive feedback:
            
            Target Band Score: {target_band}
            Assessments: {json.dumps(assessments, indent=2)}
            
            Generate:
            1. Overall test performance summary
            2. Strongest areas across all parts
            3. Consistent weaknesses to address
            4. Specific improvement strategies
            5. Study plan recommendations
            6. Estimated time to reach target band
            
            Return as JSON with clear, actionable advice.
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an IELTS coach providing detailed, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            feedback = json.loads(response.choices[0].message.content)
            return feedback
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return {
                "summary": "Feedback generation failed",
                "strengths": [],
                "weaknesses": [],
                "recommendations": ["Please retry the assessment"]
            }
    
    async def analyze_pronunciation(self, audio_file_path: str, transcript: str) -> Dict[str, Any]:
        """
        Analyze pronunciation issues (simplified version)
        Note: For production, consider using Azure Speech or Google Cloud Speech for detailed pronunciation analysis
        """
        try:
            # This is a simplified version
            # In production, you'd want to use specialized pronunciation APIs
            
            prompt = f"""
            Analyze potential pronunciation issues in this transcript:
            "{transcript}"
            
            Identify:
            1. Likely mispronounced words (based on common IELTS mistakes)
            2. Suggested pronunciation improvements
            3. Intonation and stress pattern advice
            
            Return as JSON.
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a pronunciation expert for IELTS."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing pronunciation: {e}")
            return {
                "issues": [],
                "suggestions": ["Focus on clear articulation and natural rhythm"]
            }
    
    def estimate_api_cost(self, audio_duration_seconds: int, num_assessments: int) -> Dict[str, float]:
        """
        Estimate API costs for a test session
        """
        # Pricing as of 2024 (check OpenAI pricing page for updates)
        whisper_cost_per_minute = 0.006
        gpt4_cost_per_1k_tokens = 0.03  # Approximate for GPT-4 Turbo
        
        # Estimates
        audio_minutes = audio_duration_seconds / 60
        whisper_cost = audio_minutes * whisper_cost_per_minute
        
        # Assume ~500 tokens per assessment (input + output)
        total_tokens = num_assessments * 500
        gpt4_cost = (total_tokens / 1000) * gpt4_cost_per_1k_tokens
        
        return {
            "whisper_cost": round(whisper_cost, 4),
            "gpt4_cost": round(gpt4_cost, 4),
            "total_cost": round(whisper_cost + gpt4_cost, 4),
            "cost_breakdown": {
                "audio_minutes": round(audio_minutes, 2),
                "assessments": num_assessments
            }
        }

# Singleton instance
openai_service = OpenAIService()
"""
Test OpenAI integration
"""
import asyncio
import os
from app.services.openai_service import OpenAIService

async def test_assessment():
    """Test the IELTS assessment functionality"""
    service = OpenAIService()
    
    # Test transcript
    test_transcript = """
    Well, I really enjoy living in my hometown because it has a perfect balance 
    between modern amenities and traditional culture. The people are very 
    friendly and welcoming, and there are many parks where I can relax. 
    The food is absolutely delicious, especially our local dishes.
    """
    
    print("Testing IELTS Assessment with OpenAI GPT-4...")
    print("-" * 50)
    
    try:
        # Test assessment
        result = await service.assess_ielts_response(
            transcript=test_transcript,
            question="Tell me about your hometown",
            part="Part 1",
            target_band=7.0
        )
        
        print(f"Overall Band: {result.get('overall_band')}")
        print(f"Fluency & Coherence: {result.get('fluency_coherence')}")
        print(f"Lexical Resource: {result.get('lexical_resource')}")
        print(f"Grammatical Range: {result.get('grammatical_range')}")
        print(f"Pronunciation: {result.get('pronunciation')}")
        print("\nStrengths:")
        for strength in result.get('strengths', []):
            print(f"  - {strength}")
        print("\nAreas for Improvement:")
        for improvement in result.get('improvements', []):
            print(f"  - {improvement}")
        print("\nDetailed Feedback:")
        for criterion, feedback in result.get('detailed_feedback', {}).items():
            print(f"  {criterion}: {feedback}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_assessment())
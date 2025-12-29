import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test_gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key: {api_key[:10]}...")
    
    # Test with simple query
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        request_timeout=5
    )
    
    try:
        print("Testing Gemini API...")
        result = await asyncio.wait_for(
            llm.ainvoke("Say hello in one word"),
            timeout=10.0
        )
        print(f"Success! Response: {result.content}")
        return True
    except asyncio.TimeoutError:
        print("ERROR: Gemini API timed out after 10 seconds")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini())
    if not success:
        print("\nGemini API is not working. Possible causes:")
        print("1. Invalid or expired API key")
        print("2. Quota exceeded")
        print("3. Regional restrictions")
        print("4. Model not available")

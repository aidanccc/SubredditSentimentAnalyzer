from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import RedditDB as rb # Your logic file

# This is a relative import. The "." means "from the current folder"
import RedditDB as rb;

app = FastAPI(debug=True)

class AnalyzeRequest(BaseModel): # this helps simplify json requests
    subredditStr: str


origins = [
    "http://127.0.0.1:5500"
]

#This is for security functions
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Error because im not using async praw
'''
@app.post("/analyze" )
def create_data(request: AnalyzeRequest):
    score = await getMentalScore("UMD")
    new_score = float(score)
    return {"score": "Hello"}
'''

@app.post("/analyze")
async def create_data(request: AnalyzeRequest):
    try:
        target_subreddit = request.subredditStr 

        # Using wait_for creates a 'Task', which satisfies the 
        # timeout context manager requirement.
        score = await asyncio.wait_for(
            rb.getMentalScore(target_subreddit), 
            timeout=45.0  # Reddit scraping can be slow
        )
        
        return {"subreddit": target_subreddit, "score": float(score)}

    except asyncio.TimeoutError:
        return {"error": "The request to Reddit timed out. Try a smaller limit."}
    except Exception as e:
        # Log the full error for debugging
        print(f"Detailed Error: {e}") 
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager
from browser_use import Agent, Browser
from browser_use.llm import ChatDeepSeek

# Global browser instance
browser = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser
    # Initialize the browser once on startup
    browser = Browser(headless=True, args=['--no-sandbox'])
    yield
    # Cleanup on shutdown (if browser supported close)
    # if browser: await browser.close() 

app = FastAPI(lifespan=lifespan)

class TaskRequest(BaseModel):
    url: str
    task: str
    deepseek_api_key: str

@app.post("/browse")
async def run_agent(request: TaskRequest):
    global browser
    try:
        # Initialize DeepSeek LLM
        llm = ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-chat',
            api_key=request.deepseek_api_key,
        )

        # Prepare task description
        full_task = f"Navigate to {request.url}. {request.task}"

        # Initialize Agent using the persistent browser instance
        # use_vision=False because DeepSeek-V3 (chat) is text-only/DOM-based
        agent = Agent(
            task=full_task,
            llm=llm,
            use_vision=False,
            browser=browser
        )

        # Run agent
        result = await agent.run()
        
        # Return result
        return {"result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

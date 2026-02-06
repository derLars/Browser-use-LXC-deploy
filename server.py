from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from browser_use import Agent, Browser
from browser_use.llm import ChatDeepSeek

app = FastAPI()

class TaskRequest(BaseModel):
    url: str
    task: str
    deepseek_api_key: str

@app.post("/browse")
async def run_agent(request: TaskRequest):
    try:
        # Initialize DeepSeek LLM
        llm = ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-chat',
            api_key=request.deepseek_api_key,
        )

        # Configure browser for headless execution in LXC
        # 'args' passes arguments to the browser instance
        browser = Browser(headless=True, args=['--no-sandbox'])

        # Prepare task description
        # If url is provided, we can instruct the agent to start there
        # However, typically the agent decides navigation. 
        # But to be explicit:
        full_task = f"Navigate to {request.url}. {request.task}"

        # Initialize Agent
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
        # run() returns history, we'll convert to string for now
        return {"result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

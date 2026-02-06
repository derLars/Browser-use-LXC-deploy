import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from browser_use import Agent, Browser
from browser_use.llm import ChatDeepSeek, ChatOpenAI
from loguru import logger

# --- Logger Setup ---
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/server.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

app = FastAPI()

class TaskRequest(BaseModel):
    url: str
    task: str
    api_key: str
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/v1" 
    use_vision: bool = False
    timeout: int = 900  # Default 15 minutes (in seconds)
    max_steps: int = 100  # Maximum agent steps to prevent infinite loops

def extract_final_result(history):
    """Extracts the final meaningful result from the agent history."""
    # Check for errors first
    if history.all_results:
        last_result = history.all_results[-1]
        if last_result.error:
            return {"error": last_result.error, "details": str(history)}

    # Look for 'done' action output
    for output in reversed(history.all_model_outputs):
        if 'done' in output:
            return {"result": output['done'].get('text')}
    
    # Fallback to extracted content
    if history.all_results:
        last_result = history.all_results[-1]
        if last_result.extracted_content:
            return {"result": last_result.extracted_content}
            
    return {"result": "Task completed (no explicit text output found).", "history_summary": str(history)}

@app.post("/browse")
async def run_agent(request: TaskRequest):
    logger.info(f"Incoming request: {request.task} on {request.url}")
    logger.info(f"Configuration: model={request.model}, vision={request.use_vision}, timeout={request.timeout}s, max_steps={request.max_steps}")
    
    try:
        # Initialize LLM
        if "deepseek" in request.model.lower():
            llm = ChatDeepSeek(
                base_url=request.base_url or 'https://api.deepseek.com/v1',
                model=request.model,
                api_key=request.api_key,
            )
        else:
            llm = ChatOpenAI(
                base_url=request.base_url,
                model=request.model,
                api_key=request.api_key,
            )

        # Configure browser
        # 'args' passes arguments to the browser instance
        browser = Browser(headless=True, args=['--no-sandbox'])

        # Prepare task description
        full_task = f"Navigate to {request.url}. {request.task}"

        # Initialize Agent
        agent = Agent(
            task=full_task,
            llm=llm,
            use_vision=request.use_vision,
            browser=browser,
            max_steps=request.max_steps
        )

        logger.info(f"Starting agent execution with {request.timeout}s timeout...")
        
        try:
            # Run agent with timeout
            history = await asyncio.wait_for(
                agent.run(),
                timeout=request.timeout
            )
            logger.info("Agent execution finished successfully.")
            
        except asyncio.TimeoutError:
            logger.error(f"Agent execution timed out after {request.timeout} seconds")
            return JSONResponse(
                status_code=408,  # Request Timeout
                content={
                    "error": "timeout",
                    "message": f"Task execution exceeded the timeout limit of {request.timeout} seconds",
                    "suggestion": "Try increasing the 'timeout' parameter or simplifying the task"
                }
            )
        
        response_data = extract_final_result(history)
        
        if "error" in response_data:
            logger.error(f"Agent failed: {response_data['error']}")
            return JSONResponse(status_code=500, content=response_data)
            
        logger.success("Task completed successfully.")
        return response_data

    except Exception as e:
        logger.exception("Internal Server Error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=1200,  # 20 minutes keep-alive
        timeout_graceful_shutdown=30
    )

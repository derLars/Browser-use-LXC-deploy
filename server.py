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
    base_url: str | None = None
    use_vision: bool = False
    use_judge: bool = False  # Whether to use LLM to critique results
    use_thinking: bool = False  # Whether to use internal thinking process
    timeout: int = 900  # Default 15 minutes (in seconds)
    max_steps: int = 100  # Maximum agent steps to prevent infinite loops

def extract_final_result(history):
    """Extracts the final meaningful result from the agent history."""
    try:
        # Convert Pydantic model to dict for safe access
        if hasattr(history, 'model_dump'):
            history_dict = history.model_dump()
        elif hasattr(history, 'dict'):
            history_dict = history.dict()
        else:
            # Fallback if it's not a Pydantic model
            logger.warning("History object doesn't have model_dump or dict method")
            return {"result": "Task completed successfully", "history": str(history)}
        
        logger.debug(f"History structure: {list(history_dict.keys())}")
        
        # Return the structured history data
        return {
            "result": "Task completed successfully",
            "history": history_dict
        }
        
    except Exception as e:
        logger.error(f"Error extracting result: {e}")
        return {
            "result": "Task completed successfully", 
            "note": "History data could not be serialized",
            "error_details": str(e)
        }

@app.post("/browse")
async def run_agent(request: TaskRequest):
    logger.info(f"Incoming request: {request.task} on {request.url}")
    logger.info(f"Configuration: model={request.model}, vision={request.use_vision}, timeout={request.timeout}s, max_steps={request.max_steps}")
    
    try:
        # Determine base_url based on model if not provided
        base_url = request.base_url
        if not base_url:
            if "deepseek" in request.model.lower():
                base_url = "https://api.deepseek.com/v1"
            # For OpenAI and others, let the library handle the default or use what's provided

        # Initialize LLM
        if "deepseek" in request.model.lower():
            llm = ChatDeepSeek(
                base_url=base_url,
                model=request.model,
                api_key=request.api_key,
            )
        else:
            llm = ChatOpenAI(
                base_url=base_url,
                model=request.model,
                api_key=request.api_key,
            )

        # Configure browser
        # 'args' passes arguments to the browser instance
        browser = Browser(headless=True, args=['--no-sandbox'])

        # Prepare task description
        full_task = f"Navigate to {request.url}. {request.task}"

        try:
            # Initialize Agent
            agent = Agent(
                task=full_task,
                llm=llm,
                use_vision=request.use_vision,
                browser=browser,
                max_steps=request.max_steps,
                use_judge=request.use_judge,
                use_thinking=request.use_thinking
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

        finally:
            if browser:
                try:
                    await browser.close()
                    logger.debug("Browser instance closed.")
                except Exception as e:
                    logger.warning(f"Failed to close browser: {e}")

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

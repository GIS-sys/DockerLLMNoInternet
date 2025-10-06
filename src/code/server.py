import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid

from ai import Models
from basemodels import PromptRequest, PromptResponse


app = FastAPI(title="Local LLM")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


class RequestManager:
    def __init__(self):
        self.current_request: Optional[str] = None
        self.lock = asyncio.Lock()

    async def try_acquire(self) -> bool:
        async with self.lock:
            if self.current_request is None:
                self.current_request = str(uuid.uuid4())
                return True
            return False

    async def release(self):
        async with self.lock:
            self.current_request = None

request_manager = RequestManager()


@app.post("/process-prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    if not await request_manager.try_acquire():
        raise HTTPException(status_code=429, detail="Server is busy processing another request. Try again in a few seconds")
    try:
        # Call the foo function with provided parameters
        result = Models.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        await request_manager.release()


@app.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="interface.html",
        context={"models_list": Models.get_models_list(), "model_current": Models.get_current_model()}
    )


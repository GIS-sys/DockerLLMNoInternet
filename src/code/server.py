from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import portalocker

from ai import Models
from basemodels import PromptRequest, PromptResponse
import json


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


class CustomLock:
    def __init__(self, lock_name: str = "custom_lock"):
        self.lock_file_path = f"/tmp/{lock_name}.lock"
        self._file = None

    def acquire(self) -> bool:
        try:
            self._file = open(self.lock_file_path, 'a+')
            portalocker.lock(self._file, portalocker.LOCK_EX | portalocker.LOCK_NB)
            return True
        except (portalocker.LockException, IOError):
            if self._file:
                self._file.close()
                self._file = None
            return False

    def release(self):
        if self._file:
            try:
                portalocker.unlock(self._file)
            finally:
                self._file.close()
                self._file = None


CustomLock().release()


@app.post("/process-prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    lock = CustomLock()
    if not lock.acquire():
        raise HTTPException(status_code=429, detail="Server is busy processing another request. Try again in a few seconds")
    try:
        result = Models.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        lock.release()


@app.post("/process-prompt-stream")
async def process_prompt_stream(request: PromptRequest):
    lock = CustomLock()
    if not lock.acquire():
        raise HTTPException(status_code=429, detail="Server is busy processing another request. Try again in a few seconds")
    
    async def generate():
        try:
            generator = Models.process_generator(
                model_name=request.model_name,
                max_new_tokens=request.max_new_tokens,
                prompt=request.prompt
            )
            
            for chunk in generator:
                if isinstance(chunk, dict):
                    break
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            # Get the final result
            yield f"data: {json.dumps({'text': str(chunk)})}\n\n"
            yield f"data: {json.dumps({'thinking': chunk['thinking'], 'final': chunk['final']})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            lock.release()
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="interface.html",
        context={"models_list": Models.get_models_list(), "model_current": Models.get_current_model()}
    )


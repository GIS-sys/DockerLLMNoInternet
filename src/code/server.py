from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


@app.post("/process-prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    try:
        # Call the foo function with provided parameters
        result = Models.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="interface.html",
        context={"models_list": Models.get_models_list(), "model_current": Models.get_current_model()}
    )


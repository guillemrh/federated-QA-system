from fastapi import APIRouter
from .models import AskRequest, AskResponse
from .service import answer_question

router = APIRouter(
    prefix="/ask",
    tags=["questions"],
    responses={200: {"description": "Has your question been answered?"}},
)

@router.post("/", response_model=AskResponse, summary="Given a question, get a response")
async def answer_legal_question(req: AskRequest):
    return answer_question(req.question)


from fastapi import APIRouter
from shared.models import AskRequest, AskResponse
from .service import answer_question

router = APIRouter(
    prefix="/ask",
    tags=["questions"],
    responses={200: {"description": "Has your question been answered?"}},
)

@router.post("/", response_model=AskResponse, summary="Given a question, get a response")
async def answer_financial_question(req: AskRequest):
    return answer_question(req.question)

@router.get("/healthcheck")
def healthcheck():
    return {"status": "Finance node is healthy"}


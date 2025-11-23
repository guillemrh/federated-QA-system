from fastapi import APIRouter
from shared.models import AskRequest, AskResponse
from .service import answer_question

router = APIRouter(
    prefix="/ask",
    tags=["questions"],
    responses={200: {"description": "Has your question been answered?"}},
)

@router.post("/", response_model=AskResponse)
async def answer_financial_question(req: AskRequest):
    node_result = answer_question(req.question)
    return node_result.response  # only expose AskResponse

@router.get("/healthcheck")
def healthcheck():
    return {"status": "Finance node is healthy"}


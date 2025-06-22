from shared.models import Source, AskResponse

def answer_question(question: str) -> AskResponse:
    source = Source(
        name="Savings and Investment",
        url="https://finance.ec.europa.eu/index_en",
        snippet="The savings and investments union (SIU) aims to create better financial opportunities for EU citizens, while enhancing our financial system’s capability to connect savings..."
    )

    response = AskResponse(
        answer="This is financial law",
        confidence=1.0,
        sources=[source],
        node_id="financial_node",
        status="success"
    )

    return response
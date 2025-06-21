from .models import Source, AskResponse

def answer_question(question: str) -> AskResponse:
    source = Source(
        name="Art. 6 GDPR - Lawfulness of processing",
        url="https://gdpr-info.eu/art-6-gdpr/",
        snippet="Processing shall be lawful only if and to the extent that at least one of the following applies..."
    )

    response = AskResponse(
        answer="This is the law.",
        confidence=1.0,
        sources=[source],
        node_id="legal_node",
        status="success"
    )

    return response
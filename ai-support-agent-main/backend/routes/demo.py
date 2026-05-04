from fastapi import APIRouter

router = APIRouter(prefix="/demo", tags=["demo"])

MOCK_PERSONAS = [
    {
        "id": "persona_riley",
        "name": "Riley Chen",
        "channels": ["chat", "email"],
        "archetype": "SaaS admin fighting SSO / SAML issues",
        "sample_problem": "SAML assertion fails intermittently for ~5% of logins after IdP cert rotation.",
    },
    {
        "id": "persona_marcus",
        "name": "Marcus Ortiz",
        "channels": ["phone", "chat"],
        "archetype": "Field ops with flaky mobile sync",
        "sample_problem": "Offline queue on Android duplicates tickets when signal comes back.",
    },
    {
        "id": "persona_ava",
        "name": "Ava Thompson",
        "channels": ["email", "whatsapp"],
        "archetype": "VIP retail customer — high sentiment volatility",
        "sample_problem": "Order marked delivered but nothing arrived — third time contacting support.",
    },
    {
        "id": "persona_lin",
        "name": "Lin Okonkwo",
        "channels": ["chat"],
        "archetype": "Engineer integrating webhooks",
        "sample_problem": "Webhook retries hit 429s — need backoff guidance and signature verification checklist.",
    },
]


@router.get("/personas")
def personas():
    """Evaluator-friendly mock customers — use copy/paste prompts in the UI."""
    return {"personas": MOCK_PERSONAS}

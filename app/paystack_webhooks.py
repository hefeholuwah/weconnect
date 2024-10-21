from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/webhook")
async def handle_paystack_webhook(payload: dict):
    """Handle Paystack webhook events."""
    # Process the webhook payload here
    return {"message": "Webhook received", "data": payload}

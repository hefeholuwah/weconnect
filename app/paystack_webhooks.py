import hashlib
import hmac
import json
import os
from fastapi import APIRouter, Request, HTTPException, status
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    """Validate the Paystack webhook signature using HMAC."""
    secret = PAYSTACK_SECRET_KEY.encode('utf-8')
    computed_signature = hmac.new(secret, payload, digestmod=hashlib.sha512).hexdigest()
    print("Computed HMAC Signature:", computed_signature)
    print("Received HMAC Signature:", signature)
    return hmac.compare_digest(computed_signature, signature)


@router.post("/webhook/")
async def paystack_webhook(request: Request):
    """Handle Paystack webhook events."""
    # Get the signature from the headers
    signature = request.headers.get("x-paystack-signature")
    
    # Read the raw body of the request
    payload = await request.body()

    # Verify the webhook signature
    if not signature or not verify_paystack_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Paystack signature"
        )

    # Process the payload
    event = json.loads(payload)
    
    # Handle the event types (e.g., subscription events)
    if event["event"] == "subscription.create":
        # Handle subscription creation
        return {"message": "Subscription created"}

    elif event["event"] == "subscription.disable":
        # Handle subscription disable
        return {"message": "Subscription disabled"}
    
    # Add more event handlers as needed
    return {"message": "Event received"}


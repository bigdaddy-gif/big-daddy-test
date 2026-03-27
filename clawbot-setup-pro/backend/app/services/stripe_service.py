import stripe

from app.core.config import settings


class StripeService:
    def __init__(self) -> None:
        if not settings.stripe_secret_key:
            raise RuntimeError("STRIPE_SECRET_KEY not set")
        stripe.api_key = settings.stripe_secret_key

    def create_checkout_session(self, *, user_id: str, user_email: str, success_url: str, cancel_url: str) -> str:
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=user_email,
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "ClawBot Setup Pro — $1,000 Setup"},
                        "unit_amount": 100000,
                    },
                }
            ],
            metadata={
                "user_id": user_id,
                "sku": "setup_1000",
            },
        )
        return session.url

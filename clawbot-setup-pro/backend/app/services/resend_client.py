import httpx

from app.core.config import settings


class ResendClient:
    def __init__(self) -> None:
        self._api_key = settings.resend_api_key

    async def send_magic_link(self, to_email: str, link_url: str) -> None:
        if not self._api_key:
            # Dev mode: no-op (still allows API contract testing)
            return

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "from": settings.resend_from_email,
                    "to": [to_email],
                    "subject": "Your ClawBot Setup Pro sign-in link",
                    "html": f"<p>Click to sign in:</p><p><a href=\"{link_url}\">Sign in</a></p>",
                },
            )
            r.raise_for_status()

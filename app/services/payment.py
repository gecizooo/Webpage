import httpx
from app.config import settings

async def create_invoice(amount: float, order_id: str, description: str):
    """NOWPayments invoice létrehozása"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.nowpayments.io/v1/invoice",
            headers={
                "x-api-key": settings.NOWPAYMENTS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "price_amount": amount,
                "price_currency": "usd",
                "order_id": str(order_id),
                "order_description": description,
                "ipn_callback_url": f"{settings.BASE_URL}/webhook/nowpayments",
                "success_url": f"{settings.BASE_URL}/success?order={order_id}",
                "cancel_url": f"{settings.BASE_URL}/cancel"
            }
        )
        response.raise_for_status()
        return response.json()

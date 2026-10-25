from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, Product
from app.services.payment import create_invoice
from app.services.license import generate_license

router = APIRouter(tags=["payments"])

@router.post("/create-payment/{product_id}")
async def create_payment(product_id: int, email: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Termék nem található")
    
    order = Order(
        product_id=product.id,
        email=email,
        amount=product.price,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    invoice = await create_invoice(
        amount=product.price,
        order_id=order.id,
        description=product.name
    )
    
    order.payment_id = invoice.get("id")
    db.commit()
    
    return {
        "order_id": order.id,
        "payment_url": invoice.get("invoice_url"),
        "message": "Irányítsd a vásárlót a payment_url-re"
    }

@router.post("/webhook/nowpayments")
async def nowpayments_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    
    # TODO: signature ellenőrzés (NOWPAYMENTS_IPN_SECRET)
    
    status = payload.get("payment_status")
    order_id = payload.get("order_id")
    
    if status in ["finished", "confirmed"] and order_id:
        order = db.query(Order).filter(Order.id == int(order_id)).first()
        if order and order.status != "paid":
            order.status = "paid"
            order.license_key = generate_license(order.product_id, order.email)
            db.commit()
            
            # Itt küldhetsz emailt a license_key-jel
            print(f"[DELIVERY] Email: {order.email} | License: {order.license_key}")
    
    return {"status": "ok"}

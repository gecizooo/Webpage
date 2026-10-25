from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView

from app.database import engine, Base, get_db
from app.models import Product, Order
from app.routers import payments
from app.config import settings

# Táblák létrehozása
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto License Shop", version="1.0.0")

# Routerek
app.include_router(payments.router)

# ========== Admin ==========
admin = Admin(app, engine, title="Shop Admin")

class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.name, Product.price, Product.is_active]
    column_searchable_list = [Product.name]
    form_columns = [Product.name, Product.description, Product.price, Product.file_path, Product.is_active]

class OrderAdmin(ModelView, model=Order):
    column_list = [Order.id, Order.email, Order.amount, Order.status, Order.license_key, Order.created_at]
    column_searchable_list = [Order.email, Order.license_key]
    can_create = False
    can_edit = False

admin.add_view(ProductAdmin)
admin.add_view(OrderAdmin)

# ========== Főoldal ==========
@app.get("/", response_class=HTMLResponse)
async def home(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto License Shop</title>
        <style>
            body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; background: #0f172a; color: #e2e8f0; }
            .product { border: 1px solid #334155; padding: 20px; margin: 15px 0; border-radius: 12px; background: #1e293b; }
            button { background: #10b981; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; }
            input { padding: 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; width: 250px; margin-right: 10px; }
            a { color: #38bdf8; }
        </style>
    </head>
    <body>
        <h1>Crypto License Shop</h1>
        <p>Fizetés kriptóval → automatikus licensz</p>
    """
    
    if not products:
        html += "<p>Még nincsenek termékek. Menj az <a href='/admin'>Adminba</a> és hozz létre egyet.</p>"
    
    for p in products:
        html += f"""
        <div class="product">
            <h2>{p.name}</h2>
            <p>{p.description or ''}</p>
            <p><strong>{p.price} USD</strong></p>
            <form action="/buy/{p.id}" method="post">
                <input type="email" name="email" placeholder="Email címed" required>
                <button type="submit">Vásárlás kriptóval</button>
            </form>
        </div>
        """
    
    html += """
        <hr style="border-color:#334155; margin: 40px 0;">
        <p><a href="/admin">Admin panel</a></p>
    </body></html>
    """
    return html


@app.post("/buy/{product_id}")
async def buy_product(product_id: int, email: str = Form(...), db: Session = Depends(get_db)):
    """Egyszerű átirányítás a fizetésre"""
    from app.services.payment import create_invoice
    from app.models import Order
    
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        return HTMLResponse("<h1>Termék nem található</h1>", status_code=404)
    
    order = Order(
        product_id=product.id,
        email=email,
        amount=product.price,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    try:
        invoice = await create_invoice(
            amount=product.price,
            order_id=order.id,
            description=product.name
        )
        order.payment_id = str(invoice.get("id"))
        db.commit()
        
        payment_url = invoice.get("invoice_url")
        if payment_url:
            return RedirectResponse(url=payment_url, status_code=303)
        else:
            return HTMLResponse("<h1>Hiba a fizetés létrehozásakor</h1>")
    except Exception as e:
        return HTMLResponse(f"<h1>Hiba:</h1><pre>{str(e)}</pre>")


@app.get("/success")
async def success(order: int = None):
    return {"message": "Sikeres fizetés! A licenszt emailben kapod meg.", "order_id": order}


@app.get("/cancel")
async def cancel():
    return {"message": "Fizetés megszakítva"}
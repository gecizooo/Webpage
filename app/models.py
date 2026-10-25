from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)          # USD-ben
    file_path = Column(String)                     # pl. files/mycode.zip
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    email = Column(String, nullable=False)
    amount = Column(Float)
    status = Column(String, default="pending")     # pending, paid, expired
    license_key = Column(String, unique=True, nullable=True)
    payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

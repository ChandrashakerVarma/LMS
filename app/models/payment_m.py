from sqlalchemy import Column, Integer, String,DateTime,func,Boolean,Numeric,ForeignKey,Date
from sqlalchemy.orm import relationship
from app.database import Base

class Payment(Base):
    __tablename__="payments"
    
    id=Column(Integer,primary_key=True,index=True)
    organization_id=Column(Integer,ForeignKey("organizations.id",ondelete="CASCADE"))
    
    amount=Column(Numeric(10,2),nullable=False)
    payment_type=Column(String(50),nullable=False) #subscription,addon etc
    payment_method=Column(String(50),nullable=True) #credit card, paypal etc
    transaction_id=Column(String(100),nullable=True,unique=True)
    
    payment_status=Column(String(20),default="pending") #completed,failed,pending
    payment_date=Column(Date,nullable=True)
    
    description=Column(String(255),nullable=True)
    
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),server_onupdate=func.now())
    
    created_by=Column(String(100),nullable=True)
    modified_by=Column(String(100),nullable=True)
    
    #Relationships
    organization=relationship("Organization",back_populates="payments")
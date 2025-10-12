from app import models, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(txn: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_txn = models.Transaction(**txn.dict())
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return schemas.TransactionOut(
        id=db_txn.id,
        farmer_id=db_txn.farmer_id,
        vendor_id=db_txn.vendor_id,
        crop_id=db_txn.crop_id,
        quantity=txn.quantity,
        total_price=txn.total_price
    )

@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    transaction_list = []
    for txn in transactions:
        transaction_list.append(schemas.TransactionOut(
            id=txn.id,
            farmer_id=txn.farmer_id,
            vendor_id=txn.vendor_id,
            crop_id=txn.crop_id,
            quantity=txn.quantity or 0.0,
            total_price=txn.amount or 0.0
        ))
    return transaction_list

@router.delete("/{txn_id}")
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
    return {"message": "Transaction deleted successfully"}
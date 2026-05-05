from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import SessionLocal, engine, Base
import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/sync")
def sync_data(payload: List[Dict[str, Any]], db: Session = Depends(get_db)):

    for item in payload:

        table = item.get("table_name")
        operation = item.get("operation")
        data = item.get("payload")

        if not table or not operation or not data:
            continue

        model = {
            "tareas": models.Tarea,
            "agenda": models.Agenda,
            "compras": models.Compra,
            "medicamentos": models.Medicamento
        }.get(table)

        if not model:
            continue

        if operation in ["INSERT", "UPDATE"]:
            obj = db.query(model).filter(model.id == data["id"]).first()

            if obj:
                for key, value in data.items():
                    setattr(obj, key, value)
            else:
                obj = model(**data)
                db.add(obj)

        elif operation == "DELETE":
            obj = db.query(model).filter(model.id == data["id"]).first()
            if obj:
                db.delete(obj)

    db.commit()

    return {"status": "ok"}
# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session
# from typing import List, Dict, Any

# from database import SessionLocal, engine, Base
# import models

# app = FastAPI()

# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.post("/sync")
# def sync_data(payload: List[Dict[str, Any]], db: Session = Depends(get_db)):

#     for item in payload:

#         table = item.get("table_name")
#         operation = item.get("operation")
#         data = item.get("payload")

#         if not table or not operation or not data:
#             continue

#         model = {
#             "tareas": models.Tarea,
#             "agenda": models.Agenda,
#             "compras": models.Compra,
#             "medicamentos": models.Medicamento
#         }.get(table)

#         if not model:
#             continue

#         if operation in ["INSERT", "UPDATE"]:
#             obj = db.query(model).filter(model.id == data["id"]).first()

#             if obj:
#                 for key, value in data.items():
#                     setattr(obj, key, value)
#             else:
#                 obj = model(**data)
#                 db.add(obj)

#         elif operation == "DELETE":
#             obj = db.query(model).filter(model.id == data["id"]).first()
#             if obj:
#                 db.delete(obj)

#     db.commit()

#     return {"status": "ok"}


# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session

# from database import SessionLocal, engine, Base
# import models

# app = FastAPI()

# Base.metadata.create_all(bind=engine)

# # ======================
# # DB
# # ======================
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ======================
# # MAPA TABLAS
# # ======================
# MODEL_MAP = {
#     "tareas": models.Tarea,
#     "agenda": models.Agenda,
#     "compras": models.Compra,
#     "medicamentos": models.Medicamento
# }

# # ======================
# # SYNC PRINCIPAL
# # ======================
# @app.post("/sync")
# def sync_data(payload: list, db: Session = Depends(get_db)):

#     for item in payload:

#         table = item.get("table_name")
#         operation = item.get("operation")
#         data = item.get("payload")

#         model = MODEL_MAP.get(table)

#         if not model or not data:
#             continue

#         # ================= INSERT / UPDATE =================
#         if operation in ["INSERT", "UPDATE"]:

#             obj = db.query(model).filter(model.id == data["id"]).first()

#             if obj:
#                 for key, value in data.items():
#                     setattr(obj, key, value)
#             else:
#                 obj = model(**data)
#                 db.add(obj)

#             obj.sync_status = "synced"

#         # ================= DELETE =================
#         elif operation == "DELETE":

#             obj = db.query(model).filter(model.id == data["id"]).first()

#             if obj:
#                 db.delete(obj)

#     db.commit()

#     return {"status": "ok"}

# # ======================
# # DESCARGAR CAMBIOS (FASE 4)
# # ======================
# @app.get("/sync-updates")
# def sync_updates(db: Session = Depends(get_db)):

#     updates = {}

#     for name, model in MODEL_MAP.items():
#         rows = db.query(model).filter(model.sync_status == "updated").all()

#         updates[name] = [
#             {c.name: getattr(r, c.name) for c in model.__table__.columns}
#             for r in rows
#         ]

#     return updates

# from fastapi import FastAPI, Depends, Body
# from sqlalchemy.orm import Session

# from database import SessionLocal, engine, Base
# import models

# app = FastAPI()

# # ⚠️ SOLO DEV (en prod ideal Alembic)
# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# MODEL_MAP = {
#     "tareas": models.Tarea,
#     "agenda": models.Agenda,
#     "compras": models.Compra,
#     "medicamentos": models.Medicamento
# }

# # =========================
# # 🔥 SYNC FIX
# # =========================
# @app.post("/sync")
# def sync_data(
#     payload: list = Body(...),   # 🔥 FIX IMPORTANTE
#     db: Session = Depends(get_db)
# ):

#     for item in payload:

#         table = item.get("table_name")
#         operation = item.get("operation")
#         data = item.get("payload")

#         model = MODEL_MAP.get(table)

#         if not model or not data:
#             continue

#         if operation in ["INSERT", "UPDATE"]:

#             obj = db.query(model).filter(model.id == data["id"]).first()

#             if obj:
#                 for key, value in data.items():
#                     setattr(obj, key, value)
#             else:
#                 obj = model(**data)
#                 db.add(obj)

#             obj.sync_status = "synced"

#         elif operation == "DELETE":

#             obj = db.query(model).filter(model.id == data["id"]).first()
#             if obj:
#                 db.delete(obj)

#     db.commit()
#     return {"status": "ok"}


# main.py
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Any, Dict, List
# import psycopg2
# import os
# import json

# app = FastAPI()

# DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

# def get_conn():
#     return psycopg2.connect(DATABASE_URL)

# class SyncPayload(BaseModel):
#     table_name: str
#     operation: str
#     payload: Dict[str, Any]

# # Tablas permitidas — seguridad
# ALLOWED_TABLES = {"tareas", "agenda", "compras", "medicamentos"}

# @app.get("/")
# def root():
#     return {"status": "ok", "message": "TaskLife API corriendo"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/sync")
# def sync(data: SyncPayload):
#     if data.table_name not in ALLOWED_TABLES:
#         raise HTTPException(status_code=400, detail="Tabla no permitida")

#     conn = get_conn()
#     cur = conn.cursor()

#     try:
#         p = dict(data.payload)  # copia mutable

#         if data.operation in ("INSERT", "UPDATE"):
#             if data.table_name == "tareas":
#                 cur.execute("""
#                     INSERT INTO tareas (id, user_id, titulo, descripcion, completada,
#                         "fechaLimite", prioridad, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(completada)s,
#                         %(fechaLimite)s, %(prioridad)s, %(sync_status)s, %(deleted)s,
#                         %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         titulo = EXCLUDED.titulo,
#                         descripcion = EXCLUDED.descripcion,
#                         completada = EXCLUDED.completada,
#                         "fechaLimite" = EXCLUDED."fechaLimite",
#                         prioridad = EXCLUDED.prioridad,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "agenda":
#                 # asistencia puede venir vacía — la normalizamos
#                 p["asistencia"] = p.get("asistencia") or None
#                 cur.execute("""
#                     INSERT INTO agenda (id, user_id, titulo, descripcion, asistencia,
#                         fecha, hora, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(asistencia)s,
#                         %(fecha)s, %(hora)s, %(sync_status)s, %(deleted)s,
#                         %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         titulo = EXCLUDED.titulo,
#                         fecha = EXCLUDED.fecha,
#                         hora = EXCLUDED.hora,
#                         asistencia = EXCLUDED.asistencia,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "compras":
#                 # productos puede venir como string JSON o como lista
#                 if isinstance(p.get("productos"), (dict, list)):
#                     p["productos"] = json.dumps(p["productos"])
#                 cur.execute("""
#                     INSERT INTO compras (id, user_id, categoria, productos, total,
#                         fecha, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(categoria)s, %(productos)s, %(total)s,
#                         %(fecha)s, %(sync_status)s, %(deleted)s, %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         categoria = EXCLUDED.categoria,
#                         productos = EXCLUDED.productos,
#                         total = EXCLUDED.total,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "medicamentos":
#                 # lastTaken puede venir null
#                 p["lastTaken"] = p.get("lastTaken") or None
#                 cur.execute("""
#                     INSERT INTO medicamentos (id, user_id, nombre, "dosisMg", "cadaHoras",
#                         cantidad, umbral, "photoUri", "lastTaken", sync_status, deleted,
#                         created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(nombre)s, %(dosisMg)s, %(cadaHoras)s,
#                         %(cantidad)s, %(umbral)s, %(photoUri)s, %(lastTaken)s, %(sync_status)s,
#                         %(deleted)s, %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         nombre = EXCLUDED.nombre,
#                         cantidad = EXCLUDED.cantidad,
#                         "lastTaken" = EXCLUDED."lastTaken",
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#         elif data.operation == "DELETE":
#             cur.execute(
#                 f"UPDATE {data.table_name} SET deleted = 1 WHERE id = %s",
#                 (p["id"],)
#             )

#         conn.commit()
#         return {"status": "ok"}

#     except Exception as e:
#         conn.rollback()
#         print("❌ DB error:", e)
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         cur.close()
#         conn.close()



# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Any, Dict
# import psycopg2
# import json

# app = FastAPI()

# DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

# def get_conn():
#     return psycopg2.connect(DATABASE_URL)

# class SyncPayload(BaseModel):
#     table_name: str
#     operation: str
#     payload: Dict[str, Any]

# ALLOWED_TABLES = {"tareas", "agenda", "compras", "medicamentos"}

# @app.get("/")
# def root():
#     return {"status": "ok", "message": "TaskLife API v2"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/sync")
# def sync(data: SyncPayload):
#     if data.table_name not in ALLOWED_TABLES:
#         raise HTTPException(status_code=400, detail="Tabla no permitida")

#     conn = get_conn()
#     cur = conn.cursor()

#     try:
#         p = dict(data.payload)

#         if data.operation in ("INSERT", "UPDATE"):

#             if data.table_name == "tareas":
#                 cur.execute("""
#                     INSERT INTO tareas (id, user_id, titulo, descripcion, completada,
#                         "fechaLimite", prioridad, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(completada)s,
#                         %(fechaLimite)s, %(prioridad)s, %(sync_status)s, %(deleted)s,
#                         %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         titulo = EXCLUDED.titulo,
#                         descripcion = EXCLUDED.descripcion,
#                         completada = EXCLUDED.completada,
#                         "fechaLimite" = EXCLUDED."fechaLimite",
#                         prioridad = EXCLUDED.prioridad,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "agenda":
#                 p["asistencia"] = p.get("asistencia") or None
#                 p["descripcion"] = p.get("descripcion") or None
#                 cur.execute("""
#                     INSERT INTO agenda (id, user_id, titulo, descripcion, asistencia,
#                         fecha, hora, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(asistencia)s,
#                         %(fecha)s, %(hora)s, %(sync_status)s, %(deleted)s,
#                         %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         titulo = EXCLUDED.titulo,
#                         descripcion = EXCLUDED.descripcion,
#                         fecha = EXCLUDED.fecha,
#                         hora = EXCLUDED.hora,
#                         asistencia = EXCLUDED.asistencia,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "compras":
#                 if isinstance(p.get("productos"), (dict, list)):
#                     p["productos"] = json.dumps(p["productos"])
#                 cur.execute("""
#                     INSERT INTO compras (id, user_id, categoria, productos, total,
#                         fecha, sync_status, deleted, created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(categoria)s, %(productos)s, %(total)s,
#                         %(fecha)s, %(sync_status)s, %(deleted)s, %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         categoria = EXCLUDED.categoria,
#                         productos = EXCLUDED.productos,
#                         total = EXCLUDED.total,
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#             elif data.table_name == "medicamentos":
#                 p["lastTaken"] = p.get("lastTaken") or None
#                 p["photoUri"] = p.get("photoUri") or None
#                 cur.execute("""
#                     INSERT INTO medicamentos (id, user_id, nombre, "dosisMg", "cadaHoras",
#                         cantidad, umbral, "photoUri", "lastTaken", sync_status, deleted,
#                         created_at, updated_at)
#                     VALUES (%(id)s, %(user_id)s, %(nombre)s, %(dosisMg)s, %(cadaHoras)s,
#                         %(cantidad)s, %(umbral)s, %(photoUri)s, %(lastTaken)s, %(sync_status)s,
#                         %(deleted)s, %(created_at)s, %(updated_at)s)
#                     ON CONFLICT (id) DO UPDATE SET
#                         nombre = EXCLUDED.nombre,
#                         cantidad = EXCLUDED.cantidad,
#                         "lastTaken" = EXCLUDED."lastTaken",
#                         "photoUri" = EXCLUDED."photoUri",
#                         deleted = EXCLUDED.deleted,
#                         updated_at = EXCLUDED.updated_at
#                 """, p)

#         elif data.operation == "DELETE":
#             cur.execute(
#                 f"UPDATE {data.table_name} SET deleted = 1 WHERE id = %s",
#                 (p["id"],)
#             )

#         conn.commit()
#         return {"status": "ok"}

#     except Exception as e:
#         conn.rollback()
#         print("❌ DB error:", e)
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         cur.close()
#         conn.close()




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import psycopg2
import json

app = FastAPI()

DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

class SyncPayload(BaseModel):
    table_name: str
    operation: str
    payload: Dict[str, Any]

ALLOWED_TABLES = {"tareas", "agenda", "compras", "medicamentos"}

@app.get("/")
def root():
    return {"status": "ok", "message": "TaskLife API v3"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/sync")
def sync(data: SyncPayload):
    if data.table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="Tabla no permitida")

    conn = get_conn()
    cur = conn.cursor()

    try:
        p = dict(data.payload)

        if data.operation in ("INSERT", "UPDATE"):

            if data.table_name == "tareas":
                cur.execute("""
                    INSERT INTO tareas (id, user_id, titulo, descripcion, completada,
                        "fechaLimite", prioridad, sync_status, deleted, created_at, updated_at)
                    VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(completada)s,
                        %(fechaLimite)s, %(prioridad)s, %(sync_status)s, %(deleted)s,
                        %(created_at)s, %(updated_at)s)
                    ON CONFLICT (id) DO UPDATE SET
                        titulo = EXCLUDED.titulo,
                        descripcion = EXCLUDED.descripcion,
                        completada = EXCLUDED.completada,
                        "fechaLimite" = EXCLUDED."fechaLimite",
                        prioridad = EXCLUDED.prioridad,
                        deleted = EXCLUDED.deleted,
                        updated_at = EXCLUDED.updated_at
                """, p)

            elif data.table_name == "agenda":
                p["asistencia"] = p.get("asistencia") or None
                p["descripcion"] = p.get("descripcion") or None
                cur.execute("""
                    INSERT INTO agenda (id, user_id, titulo, descripcion, asistencia,
                        fecha, hora, sync_status, deleted, created_at, updated_at)
                    VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(asistencia)s,
                        %(fecha)s, %(hora)s, %(sync_status)s, %(deleted)s,
                        %(created_at)s, %(updated_at)s)
                    ON CONFLICT (id) DO UPDATE SET
                        titulo = EXCLUDED.titulo,
                        descripcion = EXCLUDED.descripcion,
                        fecha = EXCLUDED.fecha,
                        hora = EXCLUDED.hora,
                        asistencia = EXCLUDED.asistencia,
                        deleted = EXCLUDED.deleted,
                        updated_at = EXCLUDED.updated_at
                """, p)

            elif data.table_name == "compras":
                if isinstance(p.get("productos"), (dict, list)):
                    p["productos"] = json.dumps(p["productos"])
                cur.execute("""
                    INSERT INTO compras (id, user_id, categoria, productos, total,
                        fecha, sync_status, deleted, created_at, updated_at)
                    VALUES (%(id)s, %(user_id)s, %(categoria)s, %(productos)s, %(total)s,
                        %(fecha)s, %(sync_status)s, %(deleted)s, %(created_at)s, %(updated_at)s)
                    ON CONFLICT (id) DO UPDATE SET
                        categoria = EXCLUDED.categoria,
                        productos = EXCLUDED.productos,
                        total = EXCLUDED.total,
                        deleted = EXCLUDED.deleted,
                        updated_at = EXCLUDED.updated_at
                """, p)

            elif data.table_name == "medicamentos":
                p["lastTaken"] = p.get("lastTaken") or None
                p["photoUri"] = p.get("photoUri") or None
                cur.execute("""
                    INSERT INTO medicamentos (id, user_id, nombre, "dosisMg", "cadaHoras",
                        cantidad, umbral, "photoUri", "lastTaken", sync_status, deleted,
                        created_at, updated_at)
                    VALUES (%(id)s, %(user_id)s, %(nombre)s, %(dosisMg)s, %(cadaHoras)s,
                        %(cantidad)s, %(umbral)s, %(photoUri)s, %(lastTaken)s, %(sync_status)s,
                        %(deleted)s, %(created_at)s, %(updated_at)s)
                    ON CONFLICT (id) DO UPDATE SET
                        nombre = EXCLUDED.nombre,
                        cantidad = EXCLUDED.cantidad,
                        "lastTaken" = EXCLUDED."lastTaken",
                        "photoUri" = EXCLUDED."photoUri",
                        deleted = EXCLUDED.deleted,
                        updated_at = EXCLUDED.updated_at
                """, p)

        elif data.operation == "DELETE":
            cur.execute(
                f"UPDATE {data.table_name} SET deleted = 1 WHERE id = %s",
                (p["id"],)
            )

        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        conn.rollback()
        print("❌ DB error:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import psycopg2
import json

app = FastAPI()

DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

ALLOWED_TABLES = {"tareas", "agenda", "compras", "medicamentos"}

class SyncPayload(BaseModel):
    table_name: str
    operation: str
    payload: Dict[str, Any]

# ==========================================
# HEALTH
# ==========================================
@app.get("/")
def root():
    return {"status": "ok", "message": "TaskLife API v4"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ==========================================
# SYNC (subir cambios — ya funciona)
# ==========================================
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
            # ✅ Ahora SÍ borra físicamente de PostgreSQL
            cur.execute(
                f"DELETE FROM {data.table_name} WHERE id = %s",
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

# ==========================================
# GET — descargar datos por user_id
# ==========================================
@app.get("/tareas/{user_id}")
def get_tareas(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user_id, titulo, descripcion, completada,
                "fechaLimite", prioridad, sync_status, deleted, created_at, updated_at
            FROM tareas
            WHERE user_id = %s AND deleted = 0
            ORDER BY created_at DESC
        """, (user_id,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/agenda/{user_id}")
def get_agenda(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user_id, titulo, descripcion, asistencia,
                fecha, hora, sync_status, deleted, created_at, updated_at
            FROM agenda
            WHERE user_id = %s AND deleted = 0
            ORDER BY fecha ASC
        """, (user_id,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/compras/{user_id}")
def get_compras(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user_id, categoria, productos, total,
                fecha, sync_status, deleted, created_at, updated_at
            FROM compras
            WHERE user_id = %s AND deleted = 0
            ORDER BY created_at DESC
        """, (user_id,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/medicamentos/{user_id}")
def get_medicamentos(user_id: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user_id, nombre, "dosisMg", "cadaHoras",
                cantidad, umbral, "photoUri", "lastTaken",
                sync_status, deleted, created_at, updated_at
            FROM medicamentos
            WHERE user_id = %s AND deleted = 0
            ORDER BY created_at DESC
        """, (user_id,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
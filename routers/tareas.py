from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter(prefix="/tareas", tags=["Tareas"])

class TareaIn(BaseModel):
    id: str
    user_id: str
    titulo: str
    descripcion: Optional[str] = None
    completada: int = 0
    fechaLimite: Optional[str] = None
    prioridad: str = "Media"
    sync_status: str = "synced"
    deleted: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@router.get("/{user_id}")
def listar(user_id: str):
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
        cur.close(); conn.close()

@router.post("")
def crear(tarea: TareaIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO tareas (id, user_id, titulo, descripcion, completada,
                "fechaLimite", prioridad, sync_status, deleted, created_at, updated_at)
            VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(completada)s,
                %(fechaLimite)s, %(prioridad)s, %(sync_status)s, %(deleted)s,
                %(created_at)s, %(updated_at)s)
            ON CONFLICT (id) DO NOTHING
        """, tarea.model_dump())
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.put("/{id}")
def actualizar(id: str, tarea: TareaIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE tareas SET
                titulo = %(titulo)s,
                descripcion = %(descripcion)s,
                completada = %(completada)s,
                "fechaLimite" = %(fechaLimite)s,
                prioridad = %(prioridad)s,
                deleted = %(deleted)s,
                updated_at = %(updated_at)s
            WHERE id = %(id)s
        """, {**tarea.model_dump(), "id": id})
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.delete("/{id}")
def eliminar(id: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tareas WHERE id = %s", (id,))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()
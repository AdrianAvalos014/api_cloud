from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter(prefix="/agenda", tags=["Agenda"])

class EventoIn(BaseModel):
    id: str
    user_id: str
    titulo: str
    descripcion: Optional[str] = None
    asistencia: Optional[str] = None
    fecha: str
    hora: str
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
        cur.close(); conn.close()

@router.post("")
def crear(evento: EventoIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = evento.model_dump()
        p["asistencia"] = p.get("asistencia") or None
        p["descripcion"] = p.get("descripcion") or None
        cur.execute("""
            INSERT INTO agenda (id, user_id, titulo, descripcion, asistencia,
                fecha, hora, sync_status, deleted, created_at, updated_at)
            VALUES (%(id)s, %(user_id)s, %(titulo)s, %(descripcion)s, %(asistencia)s,
                %(fecha)s, %(hora)s, %(sync_status)s, %(deleted)s,
                %(created_at)s, %(updated_at)s)
            ON CONFLICT (id) DO NOTHING
        """, p)
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.put("/{id}")
def actualizar(id: str, evento: EventoIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = evento.model_dump()
        p["asistencia"] = p.get("asistencia") or None
        cur.execute("""
            UPDATE agenda SET
                titulo = %(titulo)s,
                descripcion = %(descripcion)s,
                fecha = %(fecha)s,
                hora = %(hora)s,
                asistencia = %(asistencia)s,
                deleted = %(deleted)s,
                updated_at = %(updated_at)s
            WHERE id = %(id)s
        """, {**p, "id": id})
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
        cur.execute("DELETE FROM agenda WHERE id = %s", (id,))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()
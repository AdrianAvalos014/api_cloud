from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])

class MedicamentoIn(BaseModel):
    id: str
    user_id: str
    nombre: str
    dosisMg: Optional[str] = None
    cadaHoras: Optional[str] = None
    cantidad: Optional[str] = None
    umbral: Optional[str] = None
    photoUri: Optional[str] = None
    lastTaken: Optional[int] = None
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
        cur.close(); conn.close()

@router.post("")
def crear(med: MedicamentoIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = med.model_dump()
        p["lastTaken"] = p.get("lastTaken") or None
        p["photoUri"] = p.get("photoUri") or None
        cur.execute("""
            INSERT INTO medicamentos (id, user_id, nombre, "dosisMg", "cadaHoras",
                cantidad, umbral, "photoUri", "lastTaken", sync_status, deleted,
                created_at, updated_at)
            VALUES (%(id)s, %(user_id)s, %(nombre)s, %(dosisMg)s, %(cadaHoras)s,
                %(cantidad)s, %(umbral)s, %(photoUri)s, %(lastTaken)s, %(sync_status)s,
                %(deleted)s, %(created_at)s, %(updated_at)s)
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
def actualizar(id: str, med: MedicamentoIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = med.model_dump()
        p["lastTaken"] = p.get("lastTaken") or None
        p["photoUri"] = p.get("photoUri") or None
        cur.execute("""
            UPDATE medicamentos SET
                nombre = %(nombre)s,
                "dosisMg" = %(dosisMg)s,
                "cadaHoras" = %(cadaHoras)s,
                cantidad = %(cantidad)s,
                umbral = %(umbral)s,
                "photoUri" = %(photoUri)s,
                "lastTaken" = %(lastTaken)s,
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
        cur.execute("DELETE FROM medicamentos WHERE id = %s", (id,))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()
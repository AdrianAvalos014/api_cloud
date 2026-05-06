from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn
import json

router = APIRouter(prefix="/compras", tags=["Compras"])

class CompraIn(BaseModel):
    id: str
    user_id: str
    categoria: str
    productos: str  # JSON string
    total: float
    fecha: str
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
        cur.close(); conn.close()

@router.post("")
def crear(compra: CompraIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = compra.model_dump()
        if isinstance(p.get("productos"), (dict, list)):
            p["productos"] = json.dumps(p["productos"])
        cur.execute("""
            INSERT INTO compras (id, user_id, categoria, productos, total,
                fecha, sync_status, deleted, created_at, updated_at)
            VALUES (%(id)s, %(user_id)s, %(categoria)s, %(productos)s, %(total)s,
                %(fecha)s, %(sync_status)s, %(deleted)s, %(created_at)s, %(updated_at)s)
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
def actualizar(id: str, compra: CompraIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        p = compra.model_dump()
        if isinstance(p.get("productos"), (dict, list)):
            p["productos"] = json.dumps(p["productos"])
        cur.execute("""
            UPDATE compras SET
                categoria = %(categoria)s,
                productos = %(productos)s,
                total = %(total)s,
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
        cur.execute("DELETE FROM compras WHERE id = %s", (id,))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()
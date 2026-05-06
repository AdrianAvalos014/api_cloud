from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from database import get_conn
import json

router = APIRouter(tags=["Sync"])

class SyncPayload(BaseModel):
    table_name: str
    operation: str
    payload: Dict[str, Any]

ALLOWED_TABLES = {"tareas", "agenda", "compras", "medicamentos"}

@router.post("/sync")
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
                f"DELETE FROM {data.table_name} WHERE id = %s",
                (p["id"],)
            )

        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
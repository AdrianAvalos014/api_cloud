from sqlalchemy import Column, String, Integer, Float, Text
from database import Base

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    titulo = Column(String)
    descripcion = Column(Text)
    sync_status = Column(String)
    deleted = Column(Integer, default=0)


class Agenda(Base):
    __tablename__ = "agenda"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    titulo = Column(String)
    descripcion = Column(Text)
    fecha = Column(String)
    hora = Column(String)
    sync_status = Column(String)
    deleted = Column(Integer, default=0)


class Compra(Base):
    __tablename__ = "compras"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    categoria = Column(String)
    productos = Column(Text)
    total = Column(Float)
    fecha = Column(String)
    sync_status = Column(String)
    deleted = Column(Integer, default=0)


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    nombre = Column(String)
    dosisMg = Column(String)
    cadaHoras = Column(String)
    cantidad = Column(String)
    umbral = Column(String)
    photoUri = Column(Text)
    lastTaken = Column(String)
    sync_status = Column(String)
    deleted = Column(Integer, default=0)
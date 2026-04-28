"""Seed datos de desarrollo: 1 usuario admin + 10 rubros estándar de construcción."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import select

from common.config.settings import get_settings
from modules.auth.models.usuario import Usuario
from modules.rubros.models.rubro import Rubro


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

RUBROS_INICIALES = [
    ("Movimiento de suelos", "Excavaciones, rellenos y compactación", 4500.0),
    ("Estructura", "Fundaciones, columnas, vigas y losa", 18000.0),
    ("Mampostería", "Paredes de ladrillos o bloques", 8500.0),
    ("Instalación eléctrica", "Tablero, cableado y bocas", 6000.0),
    ("Instalación sanitaria", "Cañerías, desagüe y artefactos", 5500.0),
    ("Cubierta", "Techo, aislación y membrana", 7000.0),
    ("Revoques", "Revoque grueso y fino interior/exterior", 4000.0),
    ("Carpintería", "Puertas, ventanas y marcos", 5000.0),
    ("Pintura", "Pintura interior y exterior", 2500.0),
    ("Terminaciones", "Pisos, cerámicos, sanitarios y griferías", 9000.0),
]


async def seed() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url_async, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        result = await session.execute(select(Usuario).where(Usuario.email == "admin@obrascost.ar"))
        if not result.scalars().first():
            admin = Usuario(
                email="admin@obrascost.ar",
                password_hash=_hash_password("Admin1234!"),
                nombre="Administrador",
                role="admin",
            )
            session.add(admin)
            print("✓ Usuario admin creado: admin@obrascost.ar / Admin1234!")
        else:
            print("· Usuario admin ya existe")

        for nombre, descripcion, costo in RUBROS_INICIALES:
            r = await session.execute(select(Rubro).where(Rubro.nombre == nombre))
            if not r.scalars().first():
                session.add(Rubro(nombre=nombre, descripcion=descripcion, costo_referencia_m2=costo))
                print(f"✓ Rubro: {nombre}")
            else:
                print(f"· Rubro ya existe: {nombre}")

        await session.commit()

    await engine.dispose()
    print("\nSeed completado.")


if __name__ == "__main__":
    asyncio.run(seed())

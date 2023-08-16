# Python imports
import time
from typing import Any

# Starlette imports
from starlette.status import HTTP_409_CONFLICT

# Pydantic imports
from pydantic_settings import BaseSettings

# FastAPI imports
from fastapi.exceptions import HTTPException

# SQLAlchemy imports
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Settings(BaseSettings):
    """
    Clase que representa la configuración de la aplicación.

    Atributos:
        DATABASE_URL (str): Cadena que representa la URL para conectarse a la base de datos PostgreSQL. (por ejemplo, 'postgresql+asyncpg://postgres:micontraseña@localhost:5432/test')
        ORIGINS (str): Cadena que representa los orígenes permitidos para CORS (por ejemplo, 'http://localhost:8080,http://127.0.0.1:8080' para localhost).
    """

    DATABASE_URL: str
    ORIGINS: str

    class Config:
        """
        Clase que representa la configuración de las opciones.

        Atributos:
            env_file (str): Una cadena que representa la ruta al archivo de entorno.
        """

        env_file = "./.env"


def get_settings():
    """
    Obtiene la configuración de la aplicación.

    Returns:
        Settings: Una instancia de la configuración de la aplicación.
    """
    return Settings()


Base = declarative_base()


class AsyncDBSession:
    """
    Administrador de sesión de base de datos asincrónica.

    Esta clase administra la creación y configuración de una sesión de base de datos asincrónica.

    Atributos:
        session: La sesión de base de datos asincrónica.
        engine: El motor de base de datos asincrónico.

    Métodos:
        init(): Inicializa la sesión de base de datos y el motor.
        create_all(): Crea todas las tablas de la base de datos.
    """

    def __init__(self) -> None:
        """
        Inicializa un nuevo AsyncDBSession.

        Returns:
            None
        """
        self.session = None
        self.engine = None

    def __getattr__(self, __name: str) -> Any:
        """
        Obtiene un atributo de la sesión.

        Args:
            __name (str): El nombre del atributo.

        Returns:
            Any: El valor del atributo.
        """
        return getattr(self.session, __name)

    def init(self):
        """
        Inicializa la sesión de base de datos y el motor.

        Returns:
            None
        """
        self.engine = create_async_engine(
            url=get_settings().DATABASE_URL, future=True, echo=True
        )
        self.session = sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def create_all(self):
        """
        Crea todas las tablas de la base de datos.

        Raises:
            SQLAlchemyError: Si ocurre un error al crear las tablas.
        """
        try:
            async with self.engine.begin() as conn:
                try:
                    await conn.run_sync(Base.metadata.create_all)
                except SQLAlchemyError as e:
                    print(f"Error al crear las tablas: {e}")
                    raise
        except Exception as e:
            print(f"Error de conexión: {e}")
            time.sleep(5)
            await self.create_all()


db = AsyncDBSession()


async def commit_rollback(session=None):
    """
    Confirma los cambios o hace un rollback de la sesión.

    Raises:
        Exception: Si ocurre un error durante la confirmación, se intenta un rollback.
    """
    try:
        if session is None:
            await db.session.commit()
        else:
            await session.commit()
    except Exception as e:
        if session is None:
            await db.session.rollback()
        else:
            await session.commit()
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=[
                {
                    "field": "rollback",
                    "msg": f"{e}",
                }
            ],
        )

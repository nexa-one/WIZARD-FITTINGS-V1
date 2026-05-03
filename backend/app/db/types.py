"""
Dialect-aware types: use PostgreSQL native types in production,
fall back to SQLite-compatible equivalents for testing.
"""
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy import types, Enum as SAEnum


class UUIDType(types.TypeDecorator):
    """UUID stored as PostgreSQL UUID in prod, TEXT in SQLite."""
    impl = types.String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(types.String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class JSONBType(types.TypeDecorator):
    """JSONB in PostgreSQL, JSON in SQLite."""
    impl = types.JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(types.JSON())


def PortableEnum(enum_class):
    """SQLAlchemy Enum that works on both PostgreSQL and SQLite."""
    return SAEnum(enum_class, native_enum=False, length=50)

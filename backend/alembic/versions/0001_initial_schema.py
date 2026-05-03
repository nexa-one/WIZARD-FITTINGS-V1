"""Initial schema – CFM Fittings Pro Baseline V1

Revision ID: 0001
Revises:
Create Date: 2026-05-03
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # tenants
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("contact_phone", sa.String(50)),
        sa.Column("address", sa.Text()),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("phone", sa.String(50)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    # plans
    op.create_table(
        "plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("tier", sa.String(50), nullable=False),
        sa.Column("price_monthly", sa.Numeric(10, 2), server_default="0"),
        sa.Column("price_yearly", sa.Numeric(10, 2), server_default="0"),
        sa.Column("max_users", sa.Integer(), server_default="5"),
        sa.Column("max_orders_per_month", sa.Integer(), server_default="100"),
        sa.Column("max_storage_gb", sa.Integer(), server_default="5"),
        sa.Column("features", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("status", sa.String(50), server_default="trial"),
        sa.Column("starts_at", sa.String(50)),
        sa.Column("ends_at", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # jobs
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("job_number", sa.String(100)),
        sa.Column("client_name", sa.String(255)),
        sa.Column("location", sa.Text()),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_jobs_tenant_id", "jobs", ["tenant_id"])

    # job_areas
    op.create_table(
        "job_areas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("floor_level", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # fittings
    op.create_table(
        "fittings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("fitting_type", sa.String(50), nullable=False),
        sa.Column("material", sa.String(50), server_default="galvanized"),
        sa.Column("connection_type", sa.String(50), server_default="slip"),
        sa.Column("dimensions", JSONB(), server_default="{}"),
        sa.Column("geometry_data", JSONB(), server_default="{}"),
        sa.Column("engineering_data", JSONB(), server_default="{}"),
        sa.Column("gauge", sa.String(20)),
        sa.Column("description", sa.Text()),
        sa.Column("is_validated", sa.Boolean(), server_default="false"),
        sa.Column("is_template", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_fittings_tenant_id", "fittings", ["tenant_id"])

    # orders
    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=True),
        sa.Column("job_area_id", UUID(as_uuid=True), sa.ForeignKey("job_areas.id"), nullable=True),
        sa.Column("request_number", sa.String(100), nullable=False),
        sa.Column("requester_name", sa.String(255), nullable=False),
        sa.Column("order_date", sa.String(50), nullable=False),
        sa.Column("urgency", sa.String(50), server_default="normal"),
        sa.Column("piece_quantity", sa.Integer(), server_default="1"),
        sa.Column("status", sa.String(50), server_default="draft", nullable=False),
        sa.Column("order_type", sa.String(50), server_default="standard", nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", JSONB(), server_default="[]"),
        sa.Column("audit_history", JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_orders_tenant_id", "orders", ["tenant_id"])
    op.create_index("ix_orders_request_number", "orders", ["request_number"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # order_items
    op.create_table(
        "order_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fitting_id", UUID(as_uuid=True), sa.ForeignKey("fittings.id"), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("unit", sa.String(50)),
        sa.Column("notes", sa.Text()),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("specifications", JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    # fitting_requests
    op.create_table(
        "fitting_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("fitting_id", UUID(as_uuid=True), sa.ForeignKey("fittings.id"), nullable=True),
        sa.Column("requested_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("parsed_data", JSONB(), server_default="{}"),
        sa.Column("suggested_data", JSONB(), server_default="{}"),
        sa.Column("missing_fields", JSONB(), server_default="[]"),
        sa.Column("validation_result", JSONB(), server_default="{}"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("old_values", JSONB(), server_default="{}"),
        sa.Column("new_values", JSONB(), server_default="{}"),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(100), server_default="info"),
        sa.Column("is_read", sa.Boolean(), server_default="false"),
        sa.Column("payload", JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # exports
    op.create_table(
        "exports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100)),
        sa.Column("export_format", sa.String(20), nullable=False),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_size_bytes", sa.Integer()),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("error_message", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed default plans
    op.execute("""
        INSERT INTO plans (id, name, tier, price_monthly, price_yearly, max_users, max_orders_per_month, max_storage_gb, features, is_active)
        VALUES
          (gen_random_uuid(), 'Free', 'free', 0, 0, 2, 20, 1, 'Basic fitting creation, 20 orders/month', true),
          (gen_random_uuid(), 'Starter', 'starter', 49, 490, 5, 200, 10, 'All Free features + exports, 200 orders/month', true),
          (gen_random_uuid(), 'Professional', 'professional', 149, 1490, 20, 1000, 50, 'All Starter + AI requests, 3D preview, 1000 orders/month', true),
          (gen_random_uuid(), 'Enterprise', 'enterprise', 499, 4990, 999, 999999, 500, 'Unlimited everything + dedicated support', true)
    """)


def downgrade() -> None:
    op.drop_table("exports")
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("fitting_requests")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("fittings")
    op.drop_table("job_areas")
    op.drop_table("jobs")
    op.drop_table("subscriptions")
    op.drop_table("plans")
    op.drop_table("users")
    op.drop_table("tenants")

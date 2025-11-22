"""Add skill and education tables with reconciliation

Revision ID: ab047a75cdbf
Revises: 001
Create Date: 2025-11-18 13:36:36.761548

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'ab047a75cdbf'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    # --- SKILLS TABLE ---
    if 'skills' not in tables:
        op.create_table('skills',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('normalized_name', sa.String(length=255), nullable=True),
            sa.Column('category', sa.String(length=100), nullable=True),
            sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_skills_name'), 'skills', ['name'], unique=True)
        op.create_index(op.f('ix_skills_normalized_name'), 'skills', ['normalized_name'], unique=False)
    else:
        # Check for missing columns
        columns = [c['name'] for c in inspector.get_columns('skills')]
        if 'normalized_name' not in columns:
            op.add_column('skills', sa.Column('normalized_name', sa.String(length=255), nullable=True))
            op.create_index(op.f('ix_skills_normalized_name'), 'skills', ['normalized_name'], unique=False)
            # Populate normalized_name
            op.execute("UPDATE skills SET normalized_name = LOWER(name)")

    # --- USER_SKILLS TABLE ---
    if 'user_skills' not in tables:
        op.create_table('user_skills',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('skill_id', sa.UUID(), nullable=False),
            sa.Column('proficiency_level', sa.Integer(), server_default='1', nullable=True),
            sa.Column('confidence_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('source_tags', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True),
            sa.Column('evidence_snippets', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True),
            sa.Column('confirmed_by_user', sa.Boolean(), server_default='false', nullable=True),
            sa.Column('hidden', sa.Boolean(), server_default='false', nullable=True),
            sa.Column('evidence_source', sa.String(length=50), nullable=True),
            sa.Column('last_used_year', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('last_updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_user_skills_skill_id'), 'user_skills', ['skill_id'], unique=False)
        op.create_index(op.f('ix_user_skills_user_id'), 'user_skills', ['user_id'], unique=False)
    else:
        columns = [c['name'] for c in inspector.get_columns('user_skills')]
        if 'evidence_source' not in columns:
            op.add_column('user_skills', sa.Column('evidence_source', sa.String(length=50), nullable=True))
        if 'last_used_year' not in columns:
            op.add_column('user_skills', sa.Column('last_used_year', sa.Float(), nullable=True))

    # --- EDUCATION TABLE ---
    if 'education' not in tables:
        op.create_table('education',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('degree', sa.String(length=255), nullable=False),
            sa.Column('institution', sa.String(length=255), nullable=False),
            sa.Column('field_of_study', sa.String(length=255), nullable=True),
            sa.Column('start_year', sa.Float(), nullable=True),
            sa.Column('end_year', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_education_user_id'), 'education', ['user_id'], unique=False)

    # --- CONVERSATIONS TABLE (Check if missing from 001) ---
    if 'conversations' not in tables:
        op.create_table('conversations',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('career_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('last_message_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)
        op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # --- COACH_MESSAGES TABLE ---
    if 'coach_messages' not in tables:
        op.create_table('coach_messages',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('conversation_id', sa.UUID(), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('suggestions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_coach_messages_conversation_id'), 'coach_messages', ['conversation_id'], unique=False)
        op.create_index(op.f('ix_coach_messages_created_at'), 'coach_messages', ['created_at'], unique=False)


def downgrade() -> None:
    # We won't implement complex conditional downgrade logic here for simplicity
    # But ideally we would check if we created the table before dropping
    pass

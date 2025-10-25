"""Create job marketplace tables

Revision ID: 001
Revises: 
Create Date: 2025-10-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('remote_type', sa.String(50), nullable=True),  # 'remote', 'hybrid', 'on_site'
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True, server_default='USD'),
        sa.Column('required_skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('experience_level', sa.String(50), nullable=True),  # 'entry', 'mid', 'senior'
        sa.Column('job_type', sa.String(50), nullable=True),  # 'full_time', 'part_time', 'contract'
        sa.Column('company_logo_url', sa.String(500), nullable=True),
        sa.Column('job_url', sa.String(500), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),  # 'github', 'onet', 'manual', etc
        sa.Column('external_id', sa.String(255), nullable=True),  # ID from external source
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id', 'source', name='uq_external_job_id'),
    )
    op.create_index('ix_jobs_company', 'jobs', ['company'])
    op.create_index('ix_jobs_title', 'jobs', ['title'])
    op.create_index('ix_jobs_source', 'jobs', ['source'])

    # Create job_applications table
    op.create_table(
        'job_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),  # Firebase UID
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='applied'),  # applied, rejected, interview, offered
        sa.Column('match_score', sa.Float(), nullable=True),  # 0-100
        sa.Column('skill_gaps', postgresql.ARRAY(sa.String()), nullable=True),  # Skills user needs
        sa.Column('recommended_prep', sa.Text(), nullable=True),  # Interview prep tips
        sa.Column('interview_date', sa.DateTime(), nullable=True),
        sa.Column('interview_notes', sa.Text(), nullable=True),
        sa.Column('offer_salary', sa.Integer(), nullable=True),
        sa.Column('offer_status', sa.String(50), nullable=True),  # 'pending', 'accepted', 'declined'
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_application'),
    )
    op.create_index('ix_job_applications_user_id', 'job_applications', ['user_id'])
    op.create_index('ix_job_applications_job_id', 'job_applications', ['job_id'])
    op.create_index('ix_job_applications_status', 'job_applications', ['status'])

    # Create saved_jobs table
    op.create_table(
        'saved_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),  # Firebase UID
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('saved_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),  # User's personal notes
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_saved_job'),
    )
    op.create_index('ix_saved_jobs_user_id', 'saved_jobs', ['user_id'])
    op.create_index('ix_saved_jobs_job_id', 'saved_jobs', ['job_id'])

    # Create job_alert_preferences table
    op.create_table(
        'job_alert_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),  # Firebase UID
        sa.Column('job_title_keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('locations', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('remote_types', postgresql.ARRAY(sa.String()), nullable=True),  # 'remote', 'hybrid', 'on_site'
        sa.Column('min_salary', sa.Integer(), nullable=True),
        sa.Column('max_salary', sa.Integer(), nullable=True),
        sa.Column('experience_levels', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('required_skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('excluded_keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('min_match_score', sa.Float(), nullable=True, server_default='0.5'),  # Minimum match % to alert
        sa.Column('email_alerts_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('alert_frequency', sa.String(50), nullable=False, server_default='daily'),  # 'instant', 'daily', 'weekly'
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_job_alert_preferences'),
    )
    op.create_index('ix_job_alert_preferences_user_id', 'job_alert_preferences', ['user_id'])


def downgrade() -> None:
    # Drop indices
    op.drop_index('ix_job_alert_preferences_user_id')
    op.drop_index('ix_saved_jobs_job_id')
    op.drop_index('ix_saved_jobs_user_id')
    op.drop_index('ix_job_applications_status')
    op.drop_index('ix_job_applications_job_id')
    op.drop_index('ix_job_applications_user_id')
    op.drop_index('ix_jobs_source')
    op.drop_index('ix_jobs_title')
    op.drop_index('ix_jobs_company')
    
    # Drop tables
    op.drop_table('job_alert_preferences')
    op.drop_table('saved_jobs')
    op.drop_table('job_applications')
    op.drop_table('jobs')

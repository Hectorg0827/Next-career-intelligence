"""
User-related endpoints (profile, history, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.models.schemas import UserCreate, UserResponse, AnalysisHistoryItem
from app.models.database import User, Analysis
from app.db.database import get_db

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (called after Firebase authentication)
    """
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.firebase_uid == user_data.firebase_uid
        ).first()
        
        if existing_user:
            return existing_user
        
        # Create new user
        user = User(
            email=user_data.email,
            firebase_uid=user_data.firebase_uid,
            name=user_data.name
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created: {user.email}")
        
        return user
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/users/{user_id}/history", response_model=List[AnalysisHistoryItem])
async def get_user_history(
    user_id: str,
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Get user's analysis history
    """
    
    try:
        analyses = db.query(Analysis).filter(
            Analysis.user_id == user_id
        ).order_by(
            Analysis.created_at.desc()
        ).limit(limit).all()
        
        history = []
        for analysis in analyses:
            history.append(AnalysisHistoryItem(
                analysis_id=analysis.id,
                job_title=analysis.job_title,
                risk_score=analysis.risk_score,
                compatibility_score=analysis.compatibility_score,
                created_at=analysis.created_at
            ))
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to fetch user history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis history"
        )


@router.get("/users/{user_id}/analysis/{analysis_id}")
async def get_analysis(
    user_id: str,
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific analysis by ID
    """
    
    try:
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return analysis.analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis"
        )

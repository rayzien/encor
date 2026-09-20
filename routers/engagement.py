"""
API Router for Engine 2 Engagement Rules & Spintax Testing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
import json

from database import get_db, EngagementRule
from engine.engagement.spintax import SpintaxParser

router = APIRouter(prefix="/api/engagement", tags=["Engagement Rules"])

class SpintaxTestRequest(BaseModel):
    spintax: str
    sample_count: int = 5

class EngagementRulesPayload(BaseModel):
    do_like_enabled: bool = True
    do_like_percentage: int = 100
    delimit_liking_min: int = 5
    delimit_liking_max: int = 10000

    do_comment_enabled: bool = False
    do_comment_percentage: int = 100
    delimit_commenting_min: int = 0
    delimit_commenting_max: int = 500
    comments_spintax: List[str] = ["{Awesome|Great|Love this} {pic|shot|photo}!"]
    
    do_comment_likes_enabled: bool = False
    do_comment_likes_percentage: int = 50
    comment_likes_max: int = 3

    do_follow_enabled: bool = True
    do_follow_percentage: int = 100

    user_interact_amount: int = 3
    user_interact_percentage: int = 100
    user_interact_randomize: bool = True
    user_interact_media: str = "Photo"

    do_story_enabled: bool = True
    do_story_percentage: int = 100

@router.get("/rules")
def get_engagement_rules(db: Session = Depends(get_db)):
    rule = db.query(EngagementRule).first()
    if not rule:
        # Create default rule record
        rule = EngagementRule()
        db.add(rule)
        db.commit()
        db.refresh(rule)

    spintax_list = json.loads(rule.comments_spintax_json or "[]")
    
    return {
        "id": rule.id,
        "do_like_enabled": rule.do_like_enabled,
        "do_like_percentage": rule.do_like_percentage,
        "delimit_liking_min": rule.delimit_liking_min,
        "delimit_liking_max": rule.delimit_liking_max,
        
        "do_comment_enabled": rule.do_comment_enabled,
        "do_comment_percentage": rule.do_comment_percentage,
        "delimit_commenting_min": rule.delimit_commenting_min,
        "delimit_commenting_max": rule.delimit_commenting_max,
        "comments_spintax": spintax_list,

        "do_comment_likes_enabled": rule.do_comment_likes_enabled,
        "do_comment_likes_percentage": rule.do_comment_likes_percentage,
        "comment_likes_max": rule.comment_likes_max,

        "do_follow_enabled": rule.do_follow_enabled,
        "do_follow_percentage": rule.do_follow_percentage,

        "user_interact_amount": rule.user_interact_amount,
        "user_interact_percentage": rule.user_interact_percentage,
        "user_interact_randomize": rule.user_interact_randomize,
        "user_interact_media": rule.user_interact_media,

        "do_story_enabled": rule.do_story_enabled,
        "do_story_percentage": rule.do_story_percentage
    }

@router.post("/rules")
def save_engagement_rules(payload: EngagementRulesPayload, db: Session = Depends(get_db)):
    rule = db.query(EngagementRule).first()
    if not rule:
        rule = EngagementRule()
        db.add(rule)

    rule.do_like_enabled = payload.do_like_enabled
    rule.do_like_percentage = payload.do_like_percentage
    rule.delimit_liking_min = payload.delimit_liking_min
    rule.delimit_liking_max = payload.delimit_liking_max

    rule.do_comment_enabled = payload.do_comment_enabled
    rule.do_comment_percentage = payload.do_comment_percentage
    rule.delimit_commenting_min = payload.delimit_commenting_min
    rule.delimit_commenting_max = payload.delimit_commenting_max
    rule.comments_spintax_json = json.dumps(payload.comments_spintax)

    rule.do_comment_likes_enabled = payload.do_comment_likes_enabled
    rule.do_comment_likes_percentage = payload.do_comment_likes_percentage
    rule.comment_likes_max = payload.comment_likes_max

    rule.do_follow_enabled = payload.do_follow_enabled
    rule.do_follow_percentage = payload.do_follow_percentage

    rule.user_interact_amount = payload.user_interact_amount
    rule.user_interact_percentage = payload.user_interact_percentage
    rule.user_interact_randomize = payload.user_interact_randomize
    rule.user_interact_media = payload.user_interact_media

    rule.do_story_enabled = payload.do_story_enabled
    rule.do_story_percentage = payload.do_story_percentage

    db.commit()
    return {"message": "Engagement rules saved successfully."}

@router.post("/spintax/test")
def test_spintax(req: SpintaxTestRequest):
    samples = [SpintaxParser.spin(req.spintax) for _ in range(req.sample_count)]
    total_variations = SpintaxParser.get_variations_count(req.spintax)
    return {
        "spintax": req.spintax,
        "total_variations": total_variations,
        "samples": samples
    }

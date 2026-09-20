"""
API Router for Engine 3 Safety Guardrails & Profile Verification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json

from database import get_db, SafetyRule
from engine.safety.rules import SafetyRulesContainer
from engine.safety.guardrail import SafetyGuardrail

router = APIRouter(prefix="/api/safety", tags=["Safety Rules"])

class SafetyRulesPayload(BaseModel):
    relationship_bounds_enabled: bool = True
    min_followers: int = 30
    max_followers: int = 50000
    min_following: int = 20
    max_following: int = 7500
    min_posts: int = 5
    max_posts: int = 10000
    potency_ratio: float = 0.0

    skip_private: bool = True
    private_percentage: int = 100
    skip_no_profile_pic: bool = True
    no_profile_pic_percentage: int = 100
    skip_business: bool = False
    skip_non_business: bool = False
    skip_business_categories: List[str] = []
    dont_skip_business_categories: List[str] = []
    skip_verified: bool = True

    mandatory_words: List[str] = []
    ignore_words: List[str] = ["nsfw", "giveaway", "fake", "scam"]

    ignore_users: List[str] = []
    mandatory_language: List[str] = ["LATIN"]

class VerifyUserRequest(BaseModel):
    username: str
    followers: int = 100
    following: int = 100
    posts: int = 10
    bio: Optional[str] = ""
    is_private: bool = False
    has_profile_pic: bool = True
    is_business: bool = False
    business_category: Optional[str] = None
    is_verified: bool = False

@router.get("/rules")
def get_safety_rules(db: Session = Depends(get_db)):
    rule = db.query(SafetyRule).first()
    if not rule:
        rule = SafetyRule()
        db.add(rule)
        db.commit()
        db.refresh(rule)

    return {
        "id": rule.id,
        "relationship_bounds_enabled": rule.relationship_bounds_enabled,
        "min_followers": rule.min_followers,
        "max_followers": rule.max_followers,
        "min_following": rule.min_following,
        "max_following": rule.max_following,
        "min_posts": rule.min_posts,
        "max_posts": rule.max_posts,
        "potency_ratio": float(rule.potency_ratio or 0.0),

        "skip_private": rule.skip_private,
        "private_percentage": rule.private_percentage,
        "skip_no_profile_pic": rule.skip_no_profile_pic,
        "no_profile_pic_percentage": rule.no_profile_pic_percentage,
        "skip_business": rule.skip_business,
        "skip_non_business": rule.skip_non_business,
        "skip_business_categories": json.loads(rule.skip_business_categories_json or "[]"),
        "dont_skip_business_categories": json.loads(rule.dont_skip_business_categories_json or "[]"),
        "skip_verified": rule.skip_verified,

        "mandatory_words": json.loads(rule.mandatory_words_json or "[]"),
        "ignore_words": json.loads(rule.ignore_words_json or "[]"),

        "ignore_users": json.loads(rule.ignore_users_json or "[]"),
        "mandatory_language": json.loads(rule.mandatory_language_json or "[]")
    }

@router.post("/rules")
def save_safety_rules(payload: SafetyRulesPayload, db: Session = Depends(get_db)):
    rule = db.query(SafetyRule).first()
    if not rule:
        rule = SafetyRule()
        db.add(rule)

    rule.relationship_bounds_enabled = payload.relationship_bounds_enabled
    rule.min_followers = payload.min_followers
    rule.max_followers = payload.max_followers
    rule.min_following = payload.min_following
    rule.max_following = payload.max_following
    rule.min_posts = payload.min_posts
    rule.max_posts = payload.max_posts
    rule.potency_ratio = str(payload.potency_ratio)

    rule.skip_private = payload.skip_private
    rule.private_percentage = payload.private_percentage
    rule.skip_no_profile_pic = payload.skip_no_profile_pic
    rule.no_profile_pic_percentage = payload.no_profile_pic_percentage
    rule.skip_business = payload.skip_business
    rule.skip_non_business = payload.skip_non_business
    rule.skip_business_categories_json = json.dumps(payload.skip_business_categories)
    rule.dont_skip_business_categories_json = json.dumps(payload.dont_skip_business_categories)
    rule.skip_verified = payload.skip_verified

    rule.mandatory_words_json = json.dumps(payload.mandatory_words)
    rule.ignore_words_json = json.dumps(payload.ignore_words)

    rule.ignore_users_json = json.dumps(payload.ignore_users)
    rule.mandatory_language_json = json.dumps(payload.mandatory_language)

    db.commit()
    return {"message": "Safety rules updated successfully."}

@router.post("/verify-user")
def verify_user_safety(req: VerifyUserRequest, db: Session = Depends(get_db)):
    rules_data = get_safety_rules(db)
    container = SafetyRulesContainer(
        relationship_bounds_enabled=rules_data["relationship_bounds_enabled"],
        min_followers=rules_data["min_followers"],
        max_followers=rules_data["max_followers"],
        min_following=rules_data["min_following"],
        max_following=rules_data["max_following"],
        min_posts=rules_data["min_posts"],
        max_posts=rules_data["max_posts"],
        potency_ratio=rules_data["potency_ratio"],
        skip_private=rules_data["skip_private"],
        private_percentage=rules_data["private_percentage"],
        skip_no_profile_pic=rules_data["skip_no_profile_pic"],
        no_profile_pic_percentage=rules_data["no_profile_pic_percentage"],
        skip_business=rules_data["skip_business"],
        skip_non_business=rules_data["skip_non_business"],
        skip_business_categories=rules_data["skip_business_categories"],
        dont_skip_business_categories=rules_data["dont_skip_business_categories"],
        skip_verified=rules_data["skip_verified"],
        mandatory_words=rules_data["mandatory_words"],
        ignore_words=rules_data["ignore_words"],
        ignore_users=rules_data["ignore_users"],
        mandatory_language=rules_data["mandatory_language"]
    )

    passed, reason, audit = SafetyGuardrail.evaluate_profile(
        rules=container,
        username=req.username,
        followers=req.followers,
        following=req.following,
        posts=req.posts,
        bio=req.bio or "",
        is_private=req.is_private,
        has_profile_pic=req.has_profile_pic,
        is_business=req.is_business,
        business_category=req.business_category,
        is_verified=req.is_verified
    )

    return {
        "username": req.username,
        "passed": passed,
        "reason": reason,
        "audit": audit
    }

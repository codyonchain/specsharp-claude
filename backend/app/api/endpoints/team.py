from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import secrets
import string
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import User, Project
from app.db.team_models import Team, TeamInvitation, team_members
from app.api.endpoints.auth import get_current_user
from app.core.config import settings
from app.services.email_service import send_team_invitation_email
import stripe
import os

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
ADDITIONAL_SEAT_PRICE_ID = os.getenv("STRIPE_ADDITIONAL_SEAT_PRICE_ID", "price_additional_seat")


@router.post("/create")
async def create_team(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new team"""
    # Generate a unique slug
    base_slug = name.lower().replace(" ", "-")
    slug = base_slug
    counter = 1
    while db.query(Team).filter(Team.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create the team
    team = Team(
        name=name,
        slug=slug,
        owner_id=current_user.id,
        seats_included=3  # Base plan includes 3 seats
    )
    db.add(team)
    db.flush()
    
    # Add the owner as the first team member (admin)
    db.execute(
        team_members.insert().values(
            user_id=current_user.id,
            team_id=team.id,
            role='admin'
        )
    )
    
    # Update user's current team
    current_user.current_team_id = team.id
    
    # Migrate user's existing projects to the team
    user_projects = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.team_id == None
    ).all()
    
    for project in user_projects:
        project.team_id = team.id
        project.created_by_id = current_user.id
    
    db.commit()
    
    return {
        "id": team.id,
        "name": team.name,
        "slug": team.slug,
        "seats_included": team.seats_included,
        "seats_used": team.seats_used,
        "seats_available": team.seats_available
    }


@router.get("/current")
async def get_current_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current team details"""
    if not current_user.current_team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team selected"
        )
    
    team = db.query(Team).filter(Team.id == current_user.current_team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is admin
    is_admin = db.query(team_members.c.role).filter(
        team_members.c.user_id == current_user.id,
        team_members.c.team_id == team.id
    ).scalar() == 'admin'
    
    return {
        "id": team.id,
        "name": team.name,
        "slug": team.slug,
        "owner_id": team.owner_id,
        "is_admin": is_admin,
        "seats_included": team.seats_included,
        "additional_seats": team.additional_seats,
        "seats_used": team.seats_used,
        "seats_available": team.seats_available,
        "subscription_status": team.subscription_status
    }


@router.get("/members")
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all team members"""
    if not current_user.current_team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team selected"
        )
    
    # Get team members with their roles
    members = db.query(
        User.id,
        User.email,
        User.full_name,
        team_members.c.role,
        team_members.c.joined_at
    ).join(
        team_members,
        team_members.c.user_id == User.id
    ).filter(
        team_members.c.team_id == current_user.current_team_id
    ).all()
    
    return [
        {
            "id": member.id,
            "email": member.email,
            "full_name": member.full_name,
            "role": member.role,
            "joined_at": member.joined_at.isoformat() if member.joined_at else None
        }
        for member in members
    ]


@router.post("/invite")
async def invite_team_member(
    email: str,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Invite a new team member"""
    if not current_user.current_team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team selected"
        )
    
    # Check if user is admin
    is_admin = db.query(team_members.c.role).filter(
        team_members.c.user_id == current_user.id,
        team_members.c.team_id == current_user.current_team_id
    ).scalar() == 'admin'
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team admins can invite members"
        )
    
    team = db.query(Team).filter(Team.id == current_user.current_team_id).first()
    
    # Check if seats are available
    if team.seats_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No seats available. Please purchase additional seats."
        )
    
    # Check if user is already a member
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        existing_member = db.query(team_members).filter(
            team_members.c.user_id == existing_user.id,
            team_members.c.team_id == team.id
        ).first()
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a team member"
            )
    
    # Check for pending invitation
    pending_invite = db.query(TeamInvitation).filter(
        TeamInvitation.team_id == team.id,
        TeamInvitation.email == email,
        TeamInvitation.status == 'pending'
    ).first()
    
    if pending_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An invitation is already pending for this email"
        )
    
    # Generate invitation token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    # Create invitation
    invitation = TeamInvitation(
        team_id=team.id,
        email=email,
        role=role,
        token=token,
        invited_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()
    
    # Send invitation email (implement this service)
    # await send_team_invitation_email(email, team.name, current_user.full_name, token)
    
    return {
        "message": "Invitation sent successfully",
        "invitation_id": invitation.id,
        "email": email
    }


@router.post("/add-seats")
async def add_seats(
    seats_to_add: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Add additional seats to the team subscription"""
    if seats_to_add < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must add at least 1 seat"
        )
    
    if not current_user.current_team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team selected"
        )
    
    # Check if user is admin
    is_admin = db.query(team_members.c.role).filter(
        team_members.c.user_id == current_user.id,
        team_members.c.team_id == current_user.current_team_id
    ).scalar() == 'admin'
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team admins can purchase seats"
        )
    
    team = db.query(Team).filter(Team.id == current_user.current_team_id).first()
    
    if not team.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team must have an active subscription to add seats"
        )
    
    try:
        # Get current subscription
        subscription = stripe.Subscription.retrieve(team.stripe_subscription_id)
        
        # Find the additional seats item or add it
        seat_item = None
        for item in subscription['items']['data']:
            if item['price']['id'] == ADDITIONAL_SEAT_PRICE_ID:
                seat_item = item
                break
        
        if seat_item:
            # Update quantity
            stripe.SubscriptionItem.modify(
                seat_item['id'],
                quantity=team.additional_seats + seats_to_add
            )
        else:
            # Add new subscription item for additional seats
            stripe.SubscriptionItem.create(
                subscription=team.stripe_subscription_id,
                price=ADDITIONAL_SEAT_PRICE_ID,
                quantity=seats_to_add
            )
        
        # Update team record
        team.additional_seats += seats_to_add
        db.commit()
        
        return {
            "message": f"Successfully added {seats_to_add} seats",
            "total_seats": team.total_seats,
            "additional_cost": seats_to_add * 99  # $99 per seat
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/accept-invitation/{token}")
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Accept a team invitation"""
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.token == token,
        TeamInvitation.status == 'pending'
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invitation"
        )
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is for a different email address"
        )
    
    team = db.query(Team).filter(Team.id == invitation.team_id).first()
    
    # Check if seats are still available
    if team.seats_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No seats available in this team"
        )
    
    # Add user to team
    db.execute(
        team_members.insert().values(
            user_id=current_user.id,
            team_id=team.id,
            role=invitation.role
        )
    )
    
    # Update user's current team
    current_user.current_team_id = team.id
    
    # Mark invitation as accepted
    invitation.status = 'accepted'
    invitation.accepted_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Successfully joined team",
        "team_name": team.name,
        "team_id": team.id
    }


@router.put("/members/{member_id}/role")
async def update_member_role(
    member_id: int,
    new_role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update a team member's role"""
    if new_role not in ['admin', 'member']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'member'"
        )
    
    if not current_user.current_team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team selected"
        )
    
    # Check if user is admin
    is_admin = db.query(team_members.c.role).filter(
        team_members.c.user_id == current_user.id,
        team_members.c.team_id == current_user.current_team_id
    ).scalar() == 'admin'
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team admins can change roles"
        )
    
    # Can't change own role
    if member_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # Update the role
    result = db.execute(
        team_members.update()
        .where(
            team_members.c.user_id == member_id,
            team_members.c.team_id == current_user.current_team_id
        )
        .values(role=new_role)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    db.commit()
    
    return {"message": "Role updated successfully"}
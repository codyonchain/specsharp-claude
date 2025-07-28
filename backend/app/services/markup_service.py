from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import User, Project
from app.db.markup_models import UserMarkupSettings, ProjectMarkupOverrides


class MarkupService:
    """Service for handling markup calculations and settings"""
    
    # Default trade categories
    TRADE_CATEGORIES = {
        'structural': ['Structural'],
        'mechanical': ['Mechanical', 'HVAC'],
        'electrical': ['Electrical'],
        'plumbing': ['Plumbing'],
        'finishes': ['Finishes', 'Interior Finishes', 'Exterior Finishes'],
        'general_conditions': ['General Conditions', 'General Requirements'],
        'site_work': ['Site Work', 'Sitework'],
        'roofing': ['Roofing'],
        'hvac': ['HVAC', 'Mechanical']
    }
    
    def get_user_markup_settings(self, db: Session, user_id: int) -> UserMarkupSettings:
        """Get or create user markup settings"""
        settings = db.query(UserMarkupSettings).filter_by(user_id=user_id).first()
        
        if not settings:
            # Create default settings for user
            settings = UserMarkupSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings
    
    def get_project_markup_overrides(self, db: Session, project_id: int) -> Optional[ProjectMarkupOverrides]:
        """Get project-specific markup overrides if they exist"""
        return db.query(ProjectMarkupOverrides).filter_by(project_id=project_id).first()
    
    def calculate_markup_for_trade(
        self, 
        base_cost: float, 
        trade_name: str,
        user_settings: UserMarkupSettings,
        project_overrides: Optional[ProjectMarkupOverrides] = None
    ) -> Dict[str, float]:
        """Calculate markup for a specific trade"""
        
        # Determine if trade is self-performed or subcontracted
        is_self_perform = False
        if project_overrides and project_overrides.trade_performance_type:
            performance_type = project_overrides.trade_performance_type.get(trade_name.lower())
            is_self_perform = performance_type == 'self_perform'
        
        # Get base markup percentage
        if is_self_perform:
            base_markup = user_settings.self_perform_markup_percent
            if project_overrides and project_overrides.override_self_perform is not None:
                base_markup = project_overrides.override_self_perform
        else:
            base_markup = user_settings.subcontractor_markup_percent
            if project_overrides and project_overrides.override_subcontractor is not None:
                base_markup = project_overrides.override_subcontractor
        
        # Check for trade-specific overrides
        overhead_percent = user_settings.global_overhead_percent
        profit_percent = user_settings.global_profit_percent
        
        # User trade-specific settings
        if user_settings.trade_specific_markups:
            trade_settings = user_settings.trade_specific_markups.get(trade_name.lower(), {})
            if 'overhead' in trade_settings:
                overhead_percent = trade_settings['overhead']
            if 'profit' in trade_settings:
                profit_percent = trade_settings['profit']
        
        # Project trade-specific overrides
        if project_overrides and project_overrides.trade_overrides:
            trade_overrides = project_overrides.trade_overrides.get(trade_name.lower(), {})
            if 'overhead' in trade_overrides:
                overhead_percent = trade_overrides['overhead']
            if 'profit' in trade_overrides:
                profit_percent = trade_overrides['profit']
        
        # Calculate amounts
        overhead_amount = base_cost * (overhead_percent / 100)
        profit_amount = base_cost * (profit_percent / 100)
        total_markup = overhead_amount + profit_amount
        total_with_markup = base_cost + total_markup
        
        return {
            'base_cost': base_cost,
            'overhead_percent': overhead_percent,
            'overhead_amount': overhead_amount,
            'profit_percent': profit_percent,
            'profit_amount': profit_amount,
            'total_markup': total_markup,
            'total_with_markup': total_with_markup,
            'effective_markup_percent': (total_markup / base_cost * 100) if base_cost > 0 else 0,
            'is_self_perform': is_self_perform
        }
    
    def apply_markup_to_scope(
        self, 
        scope_data: Dict, 
        db: Session,
        user_id: int,
        project_id: Optional[int] = None
    ) -> Dict:
        """Apply markups to an entire scope response"""
        user_settings = self.get_user_markup_settings(db, user_id)
        project_overrides = None
        if project_id:
            project_overrides = self.get_project_markup_overrides(db, project_id)
        
        # Deep copy the scope data
        import copy
        marked_up_scope = copy.deepcopy(scope_data)
        
        # Track totals
        total_base_cost = 0
        total_markup = 0
        markup_details = []
        
        # Apply markup to each category
        if 'categories' in marked_up_scope:
            for category in marked_up_scope['categories']:
                category_base = category.get('subtotal', 0)
                category_markup = self.calculate_markup_for_trade(
                    category_base,
                    category['name'],
                    user_settings,
                    project_overrides
                )
                
                # Update category with markup
                category['base_subtotal'] = category_base
                category['markup_details'] = category_markup
                category['subtotal_with_markup'] = category_markup['total_with_markup']
                
                total_base_cost += category_base
                total_markup += category_markup['total_markup']
                
                markup_details.append({
                    'category': category['name'],
                    'base_cost': category_base,
                    'markup': category_markup['total_markup'],
                    'total': category_markup['total_with_markup'],
                    'overhead_percent': category_markup['overhead_percent'],
                    'profit_percent': category_markup['profit_percent'],
                    'is_self_perform': category_markup['is_self_perform']
                })
        
        # Update totals
        marked_up_scope['base_subtotal'] = total_base_cost
        marked_up_scope['total_markup'] = total_markup
        marked_up_scope['subtotal'] = total_base_cost + total_markup
        
        # Recalculate contingency on marked up amount
        contingency_percent = marked_up_scope.get('contingency_percentage', 10)
        marked_up_scope['contingency_amount'] = marked_up_scope['subtotal'] * (contingency_percent / 100)
        marked_up_scope['total_cost'] = marked_up_scope['subtotal'] + marked_up_scope['contingency_amount']
        
        # Update cost per sqft
        if 'request_data' in marked_up_scope:
            sqft = marked_up_scope['request_data'].get('square_footage', 1)
            marked_up_scope['cost_per_sqft'] = marked_up_scope['total_cost'] / sqft if sqft > 0 else 0
        
        # Add markup summary
        marked_up_scope['markup_summary'] = {
            'total_base_cost': total_base_cost,
            'total_markup': total_markup,
            'average_markup_percent': (total_markup / total_base_cost * 100) if total_base_cost > 0 else 0,
            'details': markup_details,
            'show_in_pdf': user_settings.show_markups_in_pdf,
            'show_breakdown': user_settings.show_markup_breakdown
        }
        
        return marked_up_scope
    
    def update_user_markup_settings(
        self,
        db: Session,
        user_id: int,
        settings_update: Dict
    ) -> UserMarkupSettings:
        """Update user markup settings"""
        settings = self.get_user_markup_settings(db, user_id)
        
        # Update fields
        for key, value in settings_update.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        db.commit()
        db.refresh(settings)
        return settings
    
    def update_project_markup_overrides(
        self,
        db: Session,
        project_id: int,
        overrides_update: Dict
    ) -> ProjectMarkupOverrides:
        """Update or create project markup overrides"""
        overrides = self.get_project_markup_overrides(db, project_id)
        
        if not overrides:
            overrides = ProjectMarkupOverrides(project_id=project_id)
            db.add(overrides)
        
        # Update fields
        for key, value in overrides_update.items():
            if hasattr(overrides, key):
                setattr(overrides, key, value)
        
        db.commit()
        db.refresh(overrides)
        return overrides


markup_service = MarkupService()
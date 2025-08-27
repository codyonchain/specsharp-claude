"""Financial analyzer that provides investment analysis for all building types"""

from typing import Dict, List, Any
import math

class FinancialAnalyzer:
    def calculate_revenue_requirements(self, building_type: str, subtype: str, total_cost: float, square_footage: float) -> dict:
        """Calculate what revenue/rates are needed for project success"""
        
        target_roi = 0.08  # 8% return target
        required_noi = total_cost * target_roi
        
        if building_type == 'multifamily':
            unit_count = int(square_footage / 1100) if square_footage > 0 else 1
            occupancy = 0.93
            noi_margin = 0.60
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_monthly_rent = required_revenue / (unit_count * 12 * occupancy) if unit_count > 0 else 0
            
            market_rent = {
                'luxury_apartments': 3500,
                'affordable_housing': 1200,
                'standard_apartments': 2200,
                'student_housing': 1500,
                'senior_living': 2800
            }.get(subtype, 2200)
            
            return {
                'metric_name': 'Monthly Rent',
                'required_value': required_monthly_rent,
                'market_value': market_rent,
                'feasibility': 'Feasible' if required_monthly_rent <= market_rent else 'Challenging',
                'gap': market_rent - required_monthly_rent,
                'gap_percentage': ((market_rent - required_monthly_rent) / market_rent) * 100 if market_rent > 0 else 0
            }
            
        elif building_type == 'hotel' or building_type == 'hospitality':
            room_count = int(square_footage / 400) if square_footage > 0 else 1  # 400 SF per room
            occupancy = 0.70
            noi_margin = 0.40
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_revpar = required_revenue / (room_count * 365) if room_count > 0 else 0
            
            market_revpar = {
                'luxury': 250,
                'business': 150,
                'budget': 80
            }.get(subtype, 120)
            
            return {
                'metric_name': 'RevPAR',
                'required_value': required_revpar,
                'market_value': market_revpar,
                'feasibility': 'Feasible' if required_revpar <= market_revpar else 'Challenging',
                'gap': market_revpar - required_revpar,
                'gap_percentage': ((market_revpar - required_revpar) / market_revpar) * 100 if market_revpar > 0 else 0
            }
            
        elif building_type == 'restaurant':
            # Restaurant metrics
            if subtype == 'bar_tavern':
                seats = int(square_footage / 20) if square_footage > 0 else 1  # 20 SF per seat for bar
                avg_check = 25  # Lower average check
                turns_per_day = 3  # More turns for bar
            elif subtype == 'cafe':
                seats = int(square_footage / 25) if square_footage > 0 else 1
                avg_check = 15
                turns_per_day = 6  # High turnover for cafe
            elif subtype == 'quick_service':
                seats = int(square_footage / 18) if square_footage > 0 else 1
                avg_check = 12
                turns_per_day = 8
            else:  # full_service
                seats = int(square_footage / 25) if square_footage > 0 else 1  # 25 SF per seat
                avg_check = 35
                turns_per_day = 2.5
            
            occupancy = 0.70  # Average seat occupancy
            operating_days = 350  # Closed some holidays
            noi_margin = 0.15  # Restaurant margins are lower
            
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_daily_revenue = required_revenue / operating_days if operating_days > 0 else required_revenue
            
            # Market comparison
            market_revenue = seats * avg_check * turns_per_day * occupancy * operating_days
            
            return {
                'metric_name': 'Annual Revenue',
                'required_value': required_revenue,
                'market_value': market_revenue,
                'unit_measure': 'per year',
                'feasibility': 'Feasible' if market_revenue >= required_revenue else 'Needs Review',
                'gap': market_revenue - required_revenue,
                'gap_percentage': ((market_revenue - required_revenue) / market_revenue) * 100 if market_revenue > 0 else 0,
                'details': {
                    'seats': seats,
                    'avg_check': avg_check,
                    'turns_per_day': turns_per_day,
                    'occupancy': occupancy,
                    'operating_days': operating_days
                }
            }
            
        elif building_type == 'healthcare':
            bed_count = int(square_footage / 1333) if square_footage > 0 else 1
            noi_margin = 0.35
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_per_bed = required_revenue / bed_count if bed_count > 0 else 0
            
            market_reimbursement = {
                'hospital': 550000,
                'surgery_center': 450000,
                'medical_office': 180000,
                'urgent_care': 320000
            }.get(subtype, 350000)
            
            return {
                'metric_name': 'Revenue per Bed',
                'required_value': required_per_bed,
                'market_value': market_reimbursement,
                'feasibility': 'Feasible' if required_per_bed <= market_reimbursement else 'Challenging',
                'gap': market_reimbursement - required_per_bed,
                'gap_percentage': ((market_reimbursement - required_per_bed) / market_reimbursement) * 100 if market_reimbursement > 0 else 0
            }
            
        elif building_type == 'retail':
            leasable_sf = square_footage * 0.85 if square_footage > 0 else 1
            occupancy = 0.92
            noi_margin = 0.65
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_rent_psf = required_revenue / (leasable_sf * occupancy) if leasable_sf > 0 else 0
            
            market_rent = {
                'shopping_center': 28,
                'big_box': 15,
                'strip_mall': 25
            }.get(subtype, 25)
            
            return {
                'metric_name': 'Annual Rent/SF',
                'required_value': required_rent_psf,
                'market_value': market_rent,
                'feasibility': 'Feasible' if required_rent_psf <= market_rent else 'Challenging',
                'gap': market_rent - required_rent_psf,
                'gap_percentage': ((market_rent - required_rent_psf) / market_rent) * 100 if market_rent > 0 else 0
            }
            
        elif building_type == 'industrial':
            leasable_sf = square_footage * 0.95 if square_footage > 0 else 1
            occupancy = 0.95
            noi_margin = 0.75
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_rent_psf = required_revenue / (leasable_sf * occupancy) if leasable_sf > 0 else 0
            
            market_rent = {
                'warehouse': 7,
                'distribution_center': 8,
                'flex_space': 12,
                'manufacturing': 9,
                'cold_storage': 15
            }.get(subtype, 8)
            
            return {
                'metric_name': 'NNN Rent/SF',
                'required_value': required_rent_psf,
                'market_value': market_rent,
                'feasibility': 'Feasible' if required_rent_psf <= market_rent else 'Feasible',
                'gap': market_rent - required_rent_psf,
                'gap_percentage': ((market_rent - required_rent_psf) / market_rent) * 100 if market_rent > 0 else 0
            }
            
        elif building_type == 'mixed_use':
            # Simplified mixed-use calculation based on blended revenue
            rentable_sf = square_footage * 0.85 if square_footage > 0 else 1
            occupancy = 0.90
            noi_margin = 0.55
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_revenue_psf = required_revenue / (rentable_sf * occupancy) if rentable_sf > 0 else 0
            
            # Blended market rate
            market_revenue_psf = 40  # Blended rate for mixed-use
            
            return {
                'metric_name': 'Blended Revenue/SF',
                'required_value': required_revenue_psf,
                'market_value': market_revenue_psf,
                'feasibility': 'Feasible' if required_revenue_psf <= market_revenue_psf else 'Challenging',
                'gap': market_revenue_psf - required_revenue_psf,
                'gap_percentage': ((market_revenue_psf - required_revenue_psf) / market_revenue_psf) * 100 if market_revenue_psf > 0 else 0
            }
            
        else:  # office/commercial and all other types
            rentable_sf = square_footage * 0.85 if square_footage > 0 else 1
            occupancy = 0.90
            noi_margin = 0.65
            required_revenue = required_noi / noi_margin if noi_margin > 0 else required_noi
            required_rent_psf = required_revenue / (rentable_sf * occupancy) if rentable_sf > 0 else 0
            
            market_rent = {
                'class_a': 42,
                'class_b': 28,
                'class_c': 18,
                'creative_office': 38
            }.get(subtype, 30)
            
            return {
                'metric_name': 'Annual Rent/SF',
                'required_value': required_rent_psf,
                'market_value': market_rent,
                'feasibility': 'Feasible' if required_rent_psf <= market_rent else 'Challenging',
                'gap': market_rent - required_rent_psf,
                'gap_percentage': ((market_rent - required_rent_psf) / market_rent) * 100 if market_rent > 0 else 0
            }
    
    def analyze_investment(self, project_data: dict) -> dict:
        """Analyze investment and provide comprehensive financial metrics"""
        
        building_type = project_data.get('building_type', 'office')
        total_cost = project_data.get('total_project_cost', 0)
        square_footage = project_data.get('square_footage', 0)
        subtype = project_data.get('subtype', '')
        
        # Calculate base metrics based on building type
        if building_type == 'multifamily':
            analysis = self._analyze_multifamily(project_data)
        elif building_type == 'healthcare':
            analysis = self._analyze_healthcare(project_data)
        elif building_type == 'educational':
            analysis = self._analyze_educational(project_data)
        elif building_type == 'restaurant':
            analysis = self._analyze_restaurant(project_data)
        elif building_type == 'hotel' or building_type == 'hospitality':
            analysis = self._analyze_hotel(project_data)
        elif building_type == 'retail':
            analysis = self._analyze_retail(project_data)
        elif building_type == 'industrial':
            analysis = self._analyze_industrial(project_data)
        elif building_type == 'mixed_use':
            analysis = self._analyze_mixed_use(project_data)
        else:
            # Fallback for civic, parking, recreation, specialty
            analysis = self._analyze_commercial(project_data)
        
        # Add ownership analysis structure with revenue and NOI
        ownership_analysis = {
            'return_metrics': {
                'estimated_roi': analysis['roi'],
                'cash_on_cash_return': analysis['roi'],
                'ten_year_npv': analysis['npv'],
                'irr': analysis['irr'],
                'payback_period': analysis['payback_period'],
                # Add revenue and NOI fields
                'annual_revenue': analysis.get('annual_revenue', 0),
                'noi': analysis.get('noi', 0),
                'estimated_annual_noi': analysis.get('noi', 0),  # Duplicate for compatibility
                'noi_margin': analysis.get('noi_margin', 0.60)
            },
            # Also add at top level for easier access
            'annual_revenue': analysis.get('annual_revenue', 0),
            'noi': analysis.get('noi', 0),
            'debt_metrics': {
                'calculated_dscr': analysis.get('dscr', 1.25),
                'loan_to_value': 0.65,
                'interest_rate': 0.068,
                'amortization_years': 25
            },
            'investment_analysis': self._calculate_investment_decision(project_data, analysis)
        }
        
        # Add project info with dynamic labels
        project_info = self._get_project_info(building_type, square_footage, subtype)
        
        # Add department allocation
        department_allocation = self._get_department_allocation(building_type, total_cost, square_footage)
        
        # Add operational metrics
        operational_metrics = self._get_operational_metrics(building_type, subtype, analysis)
        
        # Add revenue_analysis section for easy access
        revenue_analysis = {
            'annual_revenue': analysis.get('annual_revenue', 0),
            'monthly_revenue': analysis.get('annual_revenue', 0) / 12 if analysis.get('annual_revenue', 0) > 0 else 0,
            'noi': analysis.get('noi', 0),
            'noi_margin': analysis.get('noi_margin', 0.60),
            'operating_expenses': analysis.get('annual_revenue', 0) - analysis.get('noi', 0) if analysis.get('annual_revenue', 0) > 0 else 0
        }
        
        # Calculate revenue requirements for feasibility
        revenue_requirements = self.calculate_revenue_requirements(
            building_type=building_type,
            subtype=subtype,
            total_cost=total_cost,
            square_footage=square_footage
        )
        
        return {
            'ownership_analysis': ownership_analysis,
            'project_info': project_info,
            'department_allocation': department_allocation,
            'operational_metrics': operational_metrics,
            'revenue_analysis': revenue_analysis,
            'revenue_requirements': revenue_requirements
        }
    
    def _analyze_multifamily(self, data: dict) -> dict:
        """Multifamily-specific financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'standard_apartments')
        
        # Calculate units based on subtype
        avg_unit_size = {
            'luxury_apartments': 1100,
            'affordable_housing': 750,
            'senior_living': 900,
            'student_housing': 650,
            'standard_apartments': 950
        }.get(subtype, 950)
        
        units = square_footage / avg_unit_size if avg_unit_size > 0 else 0
        
        # Monthly rent varies by subtype
        monthly_rent = {
            'luxury_apartments': 3500,
            'affordable_housing': 1200,
            'senior_living': 2800,
            'student_housing': 1500,
            'standard_apartments': 2200
        }.get(subtype, 2200)
        
        # Calculate revenue and NOI
        occupancy_rate = 0.93  # 93% stabilized occupancy
        annual_revenue = units * monthly_rent * 12 * occupancy_rate
        operating_expenses = annual_revenue * 0.40  # 40% operating expense ratio
        noi = annual_revenue - operating_expenses
        
        # Debt service calculation
        loan_amount = total_cost * 0.65  # 65% LTV
        interest_rate = 0.068  # 6.8% interest
        annual_debt_service = loan_amount * (interest_rate + 0.02)  # Simplified P&I
        
        # Calculate NPV
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.35,  # 35% equity
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.03,
            discount_rate=0.08,
            years=10,
            terminal_value=noi * 12  # 12x exit multiple
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.35, noi - annual_debt_service),
            'payback_period': (total_cost * 0.35) / (noi - annual_debt_service) if (noi - annual_debt_service) > 0 else 999,
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': 0.60,  # 60% NOI margin for multifamily
            'units': units,
            'monthly_rent': monthly_rent
        }
    
    def _analyze_healthcare(self, data: dict) -> dict:
        """Healthcare-specific financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        
        # Healthcare metrics
        beds = square_footage / 1333  # Average SF per bed
        revenue_per_bed = 553000  # Annual revenue per bed
        annual_revenue = beds * revenue_per_bed
        
        # Operating metrics
        operating_margin = 0.15  # 15% EBITDA margin (typical for hospitals)
        noi = annual_revenue * operating_margin
        
        # Debt metrics
        loan_amount = total_cost * 0.60  # 60% LTV (more conservative for healthcare)
        annual_debt_service = loan_amount * 0.085
        
        # NPV calculation
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.40,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.025,
            discount_rate=0.09,
            years=10,
            terminal_value=noi * 10
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.40, noi - annual_debt_service),
            'payback_period': (total_cost * 0.40) / (noi - annual_debt_service) if (noi - annual_debt_service) > 0 else 999,
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': operating_margin,  # 15% for healthcare
            'beds': beds
        }
    
    def _analyze_educational(self, data: dict) -> dict:
        """Educational facility financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        
        # Educational metrics (public schools typically don't generate revenue)
        classrooms = square_footage / 900
        students = classrooms * 25  # 25 students per classroom
        
        # For private schools or universities
        tuition_per_student = 15000  # Annual tuition
        annual_revenue = students * tuition_per_student * 0.9  # 90% collection rate
        
        operating_expenses = annual_revenue * 0.85  # High operating expense ratio
        noi = annual_revenue - operating_expenses
        
        # Often funded through bonds or public funding
        annual_debt_service = total_cost * 0.05  # Lower debt service for public projects
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.20,  # Lower equity requirement
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.02,
            discount_rate=0.06,
            years=20,  # Longer horizon for educational facilities
            terminal_value=0  # No terminal value for public facilities
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.20, noi - annual_debt_service),
            'payback_period': (total_cost * 0.20) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': 0.15,  # 15% NOI margin for educational
            'classrooms': classrooms,
            'students': students
        }
    
    def _analyze_restaurant(self, data: dict) -> dict:
        """Restaurant financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'full_service')
        
        # Restaurant-specific metrics based on subtype
        if subtype == 'bar_tavern':
            seats = int(square_footage / 20)  # 20 SF per seat
            avg_check = 25
            turns_per_day = 3
            food_cost_ratio = 0.25  # Lower food cost for bars
            labor_cost_ratio = 0.30
        elif subtype == 'cafe':
            seats = int(square_footage / 25)
            avg_check = 15
            turns_per_day = 6
            food_cost_ratio = 0.30
            labor_cost_ratio = 0.35
        elif subtype == 'quick_service':
            seats = int(square_footage / 18)
            avg_check = 12
            turns_per_day = 8
            food_cost_ratio = 0.28
            labor_cost_ratio = 0.25
        else:  # full_service
            seats = int(square_footage / 25)
            avg_check = 35
            turns_per_day = 2.5
            food_cost_ratio = 0.32
            labor_cost_ratio = 0.33
        
        occupancy = 0.70
        operating_days = 350
        
        # Revenue calculation
        daily_revenue = seats * avg_check * turns_per_day * occupancy
        annual_revenue = daily_revenue * operating_days
        
        # Operating expenses
        food_costs = annual_revenue * food_cost_ratio
        labor_costs = annual_revenue * labor_cost_ratio
        rent_and_overhead = annual_revenue * 0.20  # 20% for rent/utilities/etc
        other_costs = annual_revenue * 0.10  # 10% for other expenses
        
        operating_expenses = food_costs + labor_costs + rent_and_overhead + other_costs
        noi = annual_revenue - operating_expenses
        
        # Debt metrics
        loan_amount = total_cost * 0.65  # 65% LTV for restaurants
        annual_debt_service = loan_amount * 0.068
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.35,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.02,
            discount_rate=0.10,  # Higher discount rate for restaurants
            years=10,  # Shorter horizon for restaurants
            terminal_value=total_cost * 0.50  # Lower terminal value
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.35, noi - annual_debt_service),
            'payback_period': (total_cost * 0.35) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': noi / annual_revenue if annual_revenue > 0 else 0,
            'seats': seats,
            'avg_check': avg_check,
            'daily_revenue': daily_revenue
        }
    
    def _analyze_hotel(self, data: dict) -> dict:
        """Hotel/Hospitality financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'business_hotel')
        
        # Hotel-specific metrics
        rooms = int(square_footage / 400) if square_footage > 0 else 1  # 400 SF per room average
        
        # ADR (Average Daily Rate) by subtype
        adr_by_type = {
            'luxury': 350,
            'full_service_hotel': 350,
            'business': 180,
            'business_hotel': 180,
            'limited_service_hotel': 120,
            'budget': 90,
            'extended_stay': 110
        }
        adr = adr_by_type.get(subtype, 150)
        
        # Occupancy rates
        occupancy = 0.75 if subtype in ['luxury', 'full_service_hotel'] else 0.70
        
        # Calculate revenue
        annual_revenue = rooms * adr * occupancy * 365
        
        # Operating expenses (hotels have high operating costs)
        operating_expenses = annual_revenue * 0.62  # 62% operating expense ratio
        noi = annual_revenue - operating_expenses
        noi_margin = noi / annual_revenue if annual_revenue > 0 else 0
        
        # Debt metrics
        loan_amount = total_cost * 0.65  # 65% LTV for hotels
        annual_debt_service = loan_amount * 0.07
        
        # RevPAR (Revenue per Available Room)
        revpar = adr * occupancy
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.35,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.03,
            discount_rate=0.09,
            years=10,
            terminal_value=noi / 0.085  # 8.5% cap rate for hotels
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.35, noi - annual_debt_service),
            'payback_period': (total_cost * 0.35) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': noi_margin,
            'rooms': rooms,
            'adr': adr,
            'occupancy': occupancy,
            'revpar': revpar
        }
    
    def _analyze_retail(self, data: dict) -> dict:
        """Retail projects financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'shopping_center')
        
        # Leasable area
        leasable_sf = square_footage * 0.85 if square_footage > 0 else 1  # 85% efficiency
        
        # Rent by subtype
        annual_rent_psf = {
            'shopping_center': 28,
            'big_box': 15,
            'strip_mall': 25,
            'lifestyle_center': 35,
            'outlet_center': 22,
            'neighborhood_center': 20,
            'power_center': 18,
            'regional_mall': 45
        }
        rent_psf = annual_rent_psf.get(subtype, 25)
        
        occupancy = 0.92  # Retail typically 90-95%
        annual_revenue = leasable_sf * rent_psf * occupancy
        
        # Operating expenses (CAM, taxes, insurance, management)
        operating_expenses = annual_revenue * 0.35  # 35% expense ratio
        noi = annual_revenue - operating_expenses
        noi_margin = noi / annual_revenue if annual_revenue > 0 else 0
        
        # Debt metrics
        loan_amount = total_cost * 0.70  # 70% LTV for retail
        annual_debt_service = loan_amount * 0.065
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.30,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.025,
            discount_rate=0.08,
            years=10,
            terminal_value=noi / 0.075  # 7.5% cap rate for retail
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.30, noi - annual_debt_service),
            'payback_period': (total_cost * 0.30) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': noi_margin,
            'leasable_sf': leasable_sf,
            'rent_psf': rent_psf,
            'occupancy': occupancy
        }
    
    def _analyze_industrial(self, data: dict) -> dict:
        """Industrial projects financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'warehouse')
        
        # Industrial metrics - very high efficiency
        leasable_sf = square_footage * 0.95 if square_footage > 0 else 1  # 95% efficiency
        
        # NNN lease rates by subtype (annual per SF)
        annual_rent_psf = {
            'warehouse': 7,
            'distribution_center': 8,
            'flex_space': 12,
            'manufacturing': 9,
            'cold_storage': 15,
            'data_center': 150  # Much higher for data centers
        }
        rent_psf = annual_rent_psf.get(subtype, 8)
        
        occupancy = 0.95  # Industrial typically has high occupancy
        annual_revenue = leasable_sf * rent_psf * occupancy
        
        # Low operating expenses due to NNN leases (tenants pay most expenses)
        operating_expenses = annual_revenue * 0.25 if subtype != 'data_center' else annual_revenue * 0.45
        noi = annual_revenue - operating_expenses
        noi_margin = noi / annual_revenue if annual_revenue > 0 else 0
        
        # Debt metrics
        loan_amount = total_cost * 0.75  # 75% LTV for industrial
        annual_debt_service = loan_amount * 0.06  # Lower rate for stable industrial
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.25,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.02,
            discount_rate=0.07,
            years=15,  # Longer term for industrial
            terminal_value=noi / 0.065  # 6.5% cap rate for industrial
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.25, noi - annual_debt_service),
            'payback_period': (total_cost * 0.25) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': noi_margin,
            'leasable_sf': leasable_sf,
            'rent_psf': rent_psf,
            'occupancy': occupancy,
            'lease_type': 'NNN' if subtype != 'data_center' else 'Gross'
        }
    
    def _analyze_mixed_use(self, data: dict) -> dict:
        """Mixed-use projects financial analysis with multiple components"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        subtype = data.get('subtype', 'retail_residential')
        
        # Component breakdown by subtype
        if subtype == 'retail_residential':
            residential_sf = square_footage * 0.70
            retail_sf = square_footage * 0.30
            office_sf = 0
        elif subtype == 'office_residential':
            residential_sf = square_footage * 0.60
            retail_sf = 0
            office_sf = square_footage * 0.40
        elif subtype == 'hotel_retail':
            residential_sf = 0
            retail_sf = square_footage * 0.25
            office_sf = 0
            hotel_sf = square_footage * 0.75
        elif subtype == 'urban_mixed':
            residential_sf = square_footage * 0.50
            retail_sf = square_footage * 0.20
            office_sf = square_footage * 0.30
        else:  # transit_oriented
            residential_sf = square_footage * 0.60
            retail_sf = square_footage * 0.25
            office_sf = square_footage * 0.15
        
        # Calculate revenue for each component
        residential_revenue = 0
        if residential_sf > 0:
            units = int(residential_sf / 1100)  # 1100 SF per unit
            monthly_rent = 2200  # Average rent
            residential_revenue = units * monthly_rent * 12 * 0.93  # 93% occupancy
        
        retail_revenue = 0
        if retail_sf > 0:
            leasable_retail = retail_sf * 0.85  # 85% efficiency
            retail_revenue = leasable_retail * 25 * 0.92  # $25/SF at 92% occupancy
        
        office_revenue = 0
        if office_sf > 0:
            leasable_office = office_sf * 0.85
            office_revenue = leasable_office * 30 * 0.88  # $30/SF at 88% occupancy
        
        hotel_revenue = 0
        if 'hotel_sf' in locals() and hotel_sf > 0:
            rooms = int(hotel_sf / 400)
            hotel_revenue = rooms * 150 * 0.70 * 365  # $150 ADR at 70% occupancy
        
        # Total revenue and NOI
        annual_revenue = residential_revenue + retail_revenue + office_revenue + hotel_revenue
        
        # Blended operating expenses
        blended_expense_ratio = 0.45  # Mixed-use typically 40-50% expenses
        operating_expenses = annual_revenue * blended_expense_ratio
        noi = annual_revenue - operating_expenses
        noi_margin = noi / annual_revenue if annual_revenue > 0 else 0
        
        # Debt metrics
        loan_amount = total_cost * 0.68  # 68% LTV for mixed-use
        annual_debt_service = loan_amount * 0.065
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.32,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.03,
            discount_rate=0.08,
            years=10,
            terminal_value=noi / 0.07  # 7% cap rate for mixed-use
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.32, noi - annual_debt_service),
            'payback_period': (total_cost * 0.32) / max(noi - annual_debt_service, 1),
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': noi_margin,
            'residential_revenue': residential_revenue,
            'retail_revenue': retail_revenue,
            'office_revenue': office_revenue,
            'component_breakdown': {
                'residential_sf': residential_sf,
                'retail_sf': retail_sf,
                'office_sf': office_sf
            }
        }
    
    def _analyze_commercial(self, data: dict) -> dict:
        """Commercial/Office building financial analysis"""
        square_footage = data.get('square_footage', 0)
        total_cost = data.get('total_project_cost', 0)
        
        # Office metrics
        rentable_sf = square_footage * 0.85  # 85% efficiency ratio
        annual_rent_per_sf = 35  # $35/SF/year
        occupancy_rate = 0.90  # 90% stabilized occupancy
        
        annual_revenue = rentable_sf * annual_rent_per_sf * occupancy_rate
        operating_expenses = annual_revenue * 0.35  # 35% operating expense ratio
        noi = annual_revenue - operating_expenses
        
        # Debt metrics
        loan_amount = total_cost * 0.70  # 70% LTV
        annual_debt_service = loan_amount * 0.075
        
        npv = self._calculate_npv(
            initial_investment=total_cost * 0.30,
            annual_cashflow=noi - annual_debt_service,
            growth_rate=0.025,
            discount_rate=0.075,
            years=10,
            terminal_value=noi / 0.07  # 7% cap rate
        )
        
        return {
            'roi': noi / total_cost if total_cost > 0 else 0,
            'npv': npv,
            'irr': self._calculate_irr(total_cost * 0.30, noi - annual_debt_service),
            'payback_period': (total_cost * 0.30) / (noi - annual_debt_service) if (noi - annual_debt_service) > 0 else 999,
            'dscr': noi / annual_debt_service if annual_debt_service > 0 else 0,
            'annual_revenue': annual_revenue,
            'noi': noi,
            'noi_margin': 0.65,  # 65% NOI margin for commercial
            'rentable_sf': rentable_sf
        }
    
    def _calculate_npv(self, initial_investment: float, annual_cashflow: float, 
                      growth_rate: float, discount_rate: float, years: int, 
                      terminal_value: float) -> float:
        """Calculate Net Present Value"""
        npv = -initial_investment
        
        for year in range(1, years + 1):
            cashflow = annual_cashflow * ((1 + growth_rate) ** (year - 1))
            npv += cashflow / ((1 + discount_rate) ** year)
        
        # Add terminal value
        if terminal_value > 0:
            npv += terminal_value / ((1 + discount_rate) ** years)
        
        return npv
    
    def _calculate_irr(self, initial_investment: float, annual_cashflow: float) -> float:
        """Simplified IRR calculation"""
        if initial_investment <= 0 or annual_cashflow <= 0:
            return 0
        
        # Simple approximation
        return annual_cashflow / initial_investment
    
    def _calculate_investment_decision(self, project_data: dict, analysis: dict) -> dict:
        """Calculate comprehensive investment decision with actionable feedback"""
        
        # Get building-specific thresholds
        building_type = project_data.get('building_type', 'office')
        thresholds = self._get_investment_thresholds(building_type)
        
        # Extract metrics
        roi = analysis.get('roi', 0)
        npv = analysis.get('npv', 0)
        payback = analysis.get('payback_period', 999)
        dscr = analysis.get('dscr', 0)
        total_investment = project_data.get('total_project_cost', 0)
        annual_revenue = analysis.get('annual_revenue', 0)
        annual_debt_service = analysis.get('annual_debt_service', total_investment * 0.08)  # Estimate
        
        # Initialize decision structure
        decision = {
            'recommendation': 'GO',
            'status_color': 'green',
            'failed_criteria': [],
            'improvements_needed': [],
            'summary': '',
            'metrics_table': [],
            'feasibility_score': 100  # Start at 100, deduct for failures
        }
        
        failures = []
        
        # ROI Check
        roi_pass = roi >= thresholds['min_roi']
        if not roi_pass:
            gap = thresholds['min_roi'] - roi
            revenue_needed = gap * total_investment
            failures.append({
                'metric': 'ROI',
                'current': f"{roi*100:.1f}%",
                'required': f"{thresholds['min_roi']*100:.0f}%",
                'gap': f"{gap*100:.1f}%",
                'fix': f"Increase annual revenue by ${revenue_needed:,.0f} or reduce costs by ${revenue_needed/2:,.0f}",
                'impact_score': 30  # Weight of this metric
            })
            decision['feasibility_score'] -= 30
        
        decision['metrics_table'].append({
            'metric': 'ROI',
            'current': f"{roi*100:.1f}%",
            'required': f"{thresholds['min_roi']*100:.0f}%",
            'status': 'pass' if roi_pass else 'fail'
        })
        
        # NPV Check
        npv_pass = npv >= thresholds['min_npv']
        if not npv_pass:
            gap = abs(npv)
            failures.append({
                'metric': 'NPV (10-year)',
                'current': f"${npv/1000000:.1f}M",
                'required': 'Positive',
                'gap': f"${gap/1000000:.1f}M",
                'fix': f"Project needs ${gap:,.0f} more value over 10 years - increase rents or reduce operating costs",
                'impact_score': 25
            })
            decision['feasibility_score'] -= 25
        
        decision['metrics_table'].append({
            'metric': 'NPV (10-year)',
            'current': f"${npv/1000000:.1f}M",
            'required': '> $0',
            'status': 'pass' if npv_pass else 'fail'
        })
        
        # Payback Period Check
        payback_pass = payback <= thresholds['max_payback_years']
        if not payback_pass and payback < 999:
            gap = payback - thresholds['max_payback_years']
            revenue_boost = annual_revenue * (gap / payback) if payback > 0 else 0
            failures.append({
                'metric': 'Payback Period',
                'current': f"{payback:.1f} years",
                'required': f"≤ {thresholds['max_payback_years']} years",
                'gap': f"{gap:.1f} years",
                'fix': f"Increase annual revenue by ${revenue_boost:,.0f} or reduce initial investment by ${gap * annual_revenue:,.0f}",
                'impact_score': 20
            })
            decision['feasibility_score'] -= 20
        
        decision['metrics_table'].append({
            'metric': 'Payback Period',
            'current': f"{payback:.1f} years" if payback < 999 else "N/A",
            'required': f"≤ {thresholds['max_payback_years']} years",
            'status': 'pass' if payback_pass else 'fail'
        })
        
        # DSCR Check
        dscr_pass = dscr >= thresholds['min_dscr']
        if not dscr_pass:
            gap = thresholds['min_dscr'] - dscr
            noi_needed = gap * annual_debt_service
            failures.append({
                'metric': 'DSCR',
                'current': f"{dscr:.2f}x",
                'required': f"{thresholds['min_dscr']}x",
                'gap': f"{gap:.2f}x",
                'fix': f"Increase NOI by ${noi_needed:,.0f} annually through higher occupancy or lower expenses",
                'impact_score': 25
            })
            decision['feasibility_score'] -= 25
        
        decision['metrics_table'].append({
            'metric': 'Debt Coverage',
            'current': f"{dscr:.2f}x",
            'required': f"≥ {thresholds['min_dscr']}x",
            'status': 'pass' if dscr_pass else 'fail'
        })
        
        # Set decision based on failures
        if failures:
            decision['recommendation'] = 'NO-GO'
            decision['status_color'] = 'red' if decision['feasibility_score'] < 50 else 'amber'
            decision['failed_criteria'] = failures
            
            # Create summary
            if len(failures) == 1:
                decision['summary'] = f"{failures[0]['metric']} of {failures[0]['current']} falls short of {failures[0]['required']} requirement"
            else:
                metrics_list = ', '.join([f['metric'] for f in failures])
                decision['summary'] = f"{len(failures)} metrics below requirements: {metrics_list}"
            
            # Prioritize improvements by impact
            sorted_failures = sorted(failures, key=lambda x: x['impact_score'], reverse=True)
            decision['improvements_needed'] = [
                {
                    'priority': i+1,
                    'action': f['fix'],
                    'impact': f"Fixes {f['metric']} gap of {f['gap']}",
                    'metric': f['metric']
                }
                for i, f in enumerate(sorted_failures)
            ]
        else:
            decision['summary'] = "All investment criteria met - project is financially viable"
            decision['improvements_needed'] = [{
                'priority': 1,
                'action': "Project ready to proceed as designed",
                'impact': "Consider accelerating timeline or expanding scope for higher returns",
                'metric': 'Overall'
            }]
        
        # Add legacy fields for compatibility
        decision['decision'] = decision['recommendation']
        decision['reason'] = decision['summary']
        decision['suggestions'] = [imp['action'] for imp in decision['improvements_needed'][:3]]
        decision['breakeven_metrics'] = self._calculate_breakeven(project_data, analysis)
        
        return decision
    
    def _get_investment_thresholds(self, building_type: str) -> dict:
        """Get investment thresholds by building type"""
        thresholds = {
            'restaurant': {
                'min_roi': 0.12,  # Higher risk, higher return needed
                'min_npv': 0,
                'max_payback_years': 5,  # Shorter due to concept risk
                'min_dscr': 1.35  # Higher due to volatility
            },
            'multifamily': {
                'min_roi': 0.08,
                'min_npv': 0,
                'max_payback_years': 7,
                'min_dscr': 1.25
            },
            'healthcare': {
                'min_roi': 0.09,
                'min_npv': 0,
                'max_payback_years': 8,
                'min_dscr': 1.30
            },
            'office': {
                'min_roi': 0.08,
                'min_npv': 0,
                'max_payback_years': 7,
                'min_dscr': 1.25
            },
            'retail': {
                'min_roi': 0.10,
                'min_npv': 0,
                'max_payback_years': 6,
                'min_dscr': 1.30
            },
            'industrial': {
                'min_roi': 0.07,
                'min_npv': 0,
                'max_payback_years': 10,
                'min_dscr': 1.20
            }
        }
        
        return thresholds.get(building_type, {
            'min_roi': 0.08,
            'min_npv': 0,
            'max_payback_years': 7,
            'min_dscr': 1.25
        })
    
    def _get_decision_reason(self, analysis: dict) -> str:
        """Generate decision reasoning"""
        roi = analysis['roi']
        npv = analysis['npv']
        dscr = analysis.get('dscr', 0)
        payback = analysis.get('payback_period', 999)
        
        if roi >= 0.08 and npv > 0 and dscr >= 1.25:
            return "Project meets all investment criteria with strong returns and debt coverage."
        
        # Build detailed failure reasons
        reasons = []
        if roi < 0.08:
            reasons.append(f"ROI of {roi:.1%} is below the 8% minimum threshold")
        if npv < 0:
            reasons.append(f"Negative NPV of ${npv/1000000:.1f}M over 10 years")
        if dscr < 1.25:
            reasons.append(f"DSCR of {dscr:.2f}x is below 1.25x lender requirement")
        if payback > 10:
            reasons.append(f"Payback period of {payback:.1f} years exceeds 10-year limit")
        
        if reasons:
            return ". ".join(reasons) + "."
        else:
            return "Project is marginal. Consider optimization strategies to improve returns."
    
    def _get_improvements_needed(self, data: dict, analysis: dict) -> List[dict]:
        """Generate specific improvements with quantified impacts"""
        improvements = []
        roi = analysis['roi']
        npv = analysis['npv']
        dscr = analysis.get('dscr', 0)
        total_cost = data.get('total_project_cost', 0)
        
        # ROI improvement needed
        if roi < 0.08:
            current_noi = analysis.get('annual_noi', 0)
            required_noi = total_cost * 0.08
            noi_gap = required_noi - current_noi
            
            improvements.append({
                'metric': 'ROI',
                'current': roi,
                'required': 0.08,
                'gap': 0.08 - roi,
                'suggestion': f"Increase annual NOI by ${noi_gap:,.0f} through rent increases or cost reductions"
            })
        
        # NPV improvement needed
        if npv < 0:
            improvements.append({
                'metric': 'NPV',
                'current': npv,
                'required': 0,
                'gap': abs(npv),
                'suggestion': f"Reduce costs by ${abs(npv * 0.3):,.0f} or increase revenue by ${abs(npv * 0.1):,.0f}/year"
            })
        
        # DSCR improvement needed
        if dscr < 1.25:
            current_noi = analysis.get('annual_noi', 0)
            debt_service = current_noi / max(dscr, 0.01)
            required_noi = debt_service * 1.25
            
            improvements.append({
                'metric': 'DSCR',
                'current': dscr,
                'required': 1.25,
                'gap': 1.25 - dscr,
                'suggestion': f"Increase NOI to ${required_noi:,.0f}/year or reduce debt by 20%"
            })
        
        # Payback period improvement
        payback = analysis.get('payback_period', 999)
        if payback > 10:
            improvements.append({
                'metric': 'Payback Period',
                'current': payback,
                'required': 10,
                'gap': payback - 10,
                'suggestion': f"Increase annual cash flow by {((payback - 10) / 10 * 100):.0f}% to achieve 10-year payback"
            })
        
        return improvements
    
    def _get_improvement_suggestions(self, data: dict, analysis: dict) -> List[str]:
        """Generate specific suggestions to improve returns"""
        suggestions = []
        building_type = data.get('building_type', 'office')
        
        if building_type == 'restaurant':
            seats = analysis.get('seats', 120)
            revenue_per_seat = analysis.get('annual_revenue', 0) / max(seats, 1)
            
            suggestions.append(f"Optimize seating layout to add 10-15 more seats")
            suggestions.append(f"Implement delivery/takeout to add 20% revenue stream")
            suggestions.append(f"Reduce kitchen equipment costs through leasing vs buying")
            suggestions.append(f"Consider fast-casual format to reduce labor costs by 25%")
        elif building_type == 'multifamily':
            current_rent = analysis.get('monthly_rent', 2200)
            required_rent = self._calculate_required_rent_for_target_return(data, analysis)
            
            if required_rent > current_rent:
                increase_pct = ((required_rent - current_rent) / current_rent * 100)
                suggestions.append(f"Increase average rent to ${required_rent:,.0f}/mo ({increase_pct:.0f}% increase)")
            
            suggestions.append(f"Reduce construction costs by ${(data['total_project_cost'] * 0.1 / 1000000):.1f}M through value engineering")
            suggestions.append("Add premium amenities (gym, pool, rooftop) to justify 10-15% rent premium")
            suggestions.append("Consider mixed-income strategy with 80/20 market/affordable split")
            
        elif building_type == 'healthcare':
            suggestions.append("Partner with health system for guaranteed occupancy")
            suggestions.append("Add outpatient services to increase revenue per SF")
            suggestions.append("Implement energy efficiency measures to reduce operating costs by 15%")
            suggestions.append("Consider phased opening to accelerate cash flow")
            
        elif building_type == 'office':
            suggestions.append("Pre-lease 60% before construction to reduce risk")
            suggestions.append("Add flexible co-working spaces for 20% premium")
            suggestions.append("Implement smart building tech to attract premium tenants")
            suggestions.append("Consider ground floor retail for additional revenue stream")
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def _calculate_required_rent_for_target_return(self, data: dict, analysis: dict) -> float:
        """Calculate rent needed for 8% ROI"""
        total_cost = data.get('total_project_cost', 0)
        units = analysis.get('units', 1)
        
        # Target NOI for 8% return
        target_noi = total_cost * 0.08
        
        # Back out required revenue (assuming 40% operating expenses)
        required_revenue = target_noi / 0.60
        
        # Calculate monthly rent per unit
        required_monthly_rent = required_revenue / (units * 12 * 0.93)  # 93% occupancy
        
        return required_monthly_rent
    
    def _calculate_breakeven(self, data: dict, analysis: dict) -> dict:
        """Calculate breakeven metrics"""
        building_type = data.get('building_type', 'office')
        
        if building_type == 'multifamily':
            return {
                'occupancy': 0.85,  # 85% breakeven occupancy
                'required_rent': self._calculate_required_rent_for_target_return(data, analysis)
            }
        elif building_type == 'healthcare':
            return {
                'occupancy': 0.75,  # 75% bed occupancy
                'revenue_per_bed': 450000  # Minimum revenue per bed
            }
        else:
            return {
                'occupancy': 0.85,
                'rent_per_sf': 32  # Minimum rent per SF
            }
    
    def _get_project_info(self, building_type: str, square_footage: float, subtype: str) -> dict:
        """Get project-specific labels and counts"""
        if building_type == 'multifamily':
            avg_unit_size = 1100 if 'luxury' in subtype else 950
            unit_count = int(square_footage / avg_unit_size)
            return {
                'unit_label': 'Apartment Units',
                'unit_count': unit_count,
                'unit_type': 'units',
                'completion_milestone': 'First Tenant Move-in'
            }
        elif building_type == 'healthcare':
            bed_count = int(square_footage / 1333)
            return {
                'unit_label': 'Beds Capacity',
                'unit_count': bed_count,
                'unit_type': 'beds',
                'completion_milestone': 'First Patient'
            }
        elif building_type == 'educational':
            classroom_count = int(square_footage / 900)
            return {
                'unit_label': 'Classrooms',
                'unit_count': classroom_count,
                'unit_type': 'classrooms',
                'completion_milestone': 'First Day of School'
            }
        else:
            floor_count = max(1, int(square_footage / 15000))
            return {
                'unit_label': 'Rentable Floors',
                'unit_count': floor_count,
                'unit_type': 'floors',
                'completion_milestone': 'First Tenant Occupancy'
            }
    
    def _get_department_allocation(self, building_type: str, total_cost: float, square_footage: float) -> List[dict]:
        """Get department cost allocation based on building type"""
        if building_type == 'multifamily':
            departments = [
                {'name': 'Residential Units', 'percent': 0.70, 'icon_name': 'Home', 
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Common Areas & Lobbies', 'percent': 0.20, 'icon_name': 'Users',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Amenities & Recreation', 'percent': 0.10, 'icon_name': 'Shield',
                 'gradient': 'from-purple-600 to-purple-700'}
            ]
        elif building_type == 'restaurant':
            departments = [
                {'name': 'Kitchen & Food Prep', 'percent': 0.35, 'icon_name': 'Utensils',
                 'gradient': 'from-orange-600 to-orange-700'},
                {'name': 'Dining Areas', 'percent': 0.40, 'icon_name': 'Users',
                 'gradient': 'from-red-600 to-red-700'},
                {'name': 'Bar & Beverage', 'percent': 0.15, 'icon_name': 'Wine',
                 'gradient': 'from-purple-600 to-purple-700'},
                {'name': 'Support Areas', 'percent': 0.10, 'icon_name': 'Package',
                 'gradient': 'from-gray-600 to-gray-700'}
            ]
        elif building_type == 'retail':
            departments = [
                {'name': 'Sales Floor', 'percent': 0.70, 'icon_name': 'ShoppingCart',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Storage & Receiving', 'percent': 0.20, 'icon_name': 'Package',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Customer Service', 'percent': 0.10, 'icon_name': 'Headphones',
                 'gradient': 'from-purple-600 to-purple-700'}
            ]
        elif building_type == 'industrial':
            departments = [
                {'name': 'Production Floor', 'percent': 0.60, 'icon_name': 'Factory',
                 'gradient': 'from-gray-600 to-gray-700'},
                {'name': 'Warehouse & Storage', 'percent': 0.30, 'icon_name': 'Package',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Office & Support', 'percent': 0.10, 'icon_name': 'Briefcase',
                 'gradient': 'from-green-600 to-green-700'}
            ]
        elif building_type == 'hospitality':
            departments = [
                {'name': 'Guest Rooms', 'percent': 0.65, 'icon_name': 'Bed',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Public Areas & Lobby', 'percent': 0.20, 'icon_name': 'Users',
                 'gradient': 'from-purple-600 to-purple-700'},
                {'name': 'Food & Beverage', 'percent': 0.10, 'icon_name': 'Utensils',
                 'gradient': 'from-orange-600 to-orange-700'},
                {'name': 'Support Services', 'percent': 0.05, 'icon_name': 'Wrench',
                 'gradient': 'from-gray-600 to-gray-700'}
            ]
        elif building_type == 'healthcare':
            departments = [
                {'name': 'Clinical Department', 'percent': 0.60, 'icon_name': 'Heart',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Support Department', 'percent': 0.30, 'icon_name': 'Headphones',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Infrastructure Department', 'percent': 0.10, 'icon_name': 'Cpu',
                 'gradient': 'from-purple-600 to-purple-700'}
            ]
        elif building_type == 'educational':
            departments = [
                {'name': 'Academic Spaces', 'percent': 0.65, 'icon_name': 'GraduationCap',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Support Facilities', 'percent': 0.25, 'icon_name': 'Users',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Athletics/Recreation', 'percent': 0.10, 'icon_name': 'Activity',
                 'gradient': 'from-purple-600 to-purple-700'}
            ]
        elif building_type == 'office':
            departments = [
                {'name': 'Office Spaces', 'percent': 0.75, 'icon_name': 'Briefcase',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Common Areas', 'percent': 0.15, 'icon_name': 'Users',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Building Systems', 'percent': 0.10, 'icon_name': 'Building2',
                 'gradient': 'from-purple-600 to-purple-700'}
            ]
        else:
            # Generic fallback for any other building types
            departments = [
                {'name': 'Primary Function Space', 'percent': 0.70, 'icon_name': 'Building',
                 'gradient': 'from-blue-600 to-blue-700'},
                {'name': 'Support Areas', 'percent': 0.20, 'icon_name': 'Users',
                 'gradient': 'from-green-600 to-green-700'},
                {'name': 'Infrastructure', 'percent': 0.10, 'icon_name': 'Settings',
                 'gradient': 'from-gray-600 to-gray-700'}
            ]
        
        # Calculate amounts for each department
        for dept in departments:
            dept['amount'] = total_cost * dept['percent']
            dept['square_footage'] = square_footage * dept['percent']
            dept['cost_per_sf'] = dept['amount'] / dept['square_footage'] if dept['square_footage'] > 0 else 0
        
        return departments
    
    def _get_operational_metrics(self, building_type: str, subtype: str, analysis: dict) -> dict:
        """Get operational metrics based on building type"""
        if building_type == 'multifamily':
            monthly_rent = analysis.get('monthly_rent', 2200)
            return {
                'staffing': [
                    {'label': 'Units per Manager', 'value': 50},
                    {'label': 'Maintenance Staff', 'value': 8}
                ],
                'revenue': {
                    'Revenue per Unit': f"${analysis.get('annual_revenue', 0) / max(analysis.get('units', 1), 1) / 1000:.1f}K",
                    'Average Rent': f"${monthly_rent:,.0f}/mo",
                    'Occupancy Target': '93%'
                },
                'kpis': [
                    {'label': 'Lease-up', 'value': '6mo', 'color': 'blue'},
                    {'label': 'Occupancy', 'value': '93%', 'color': 'green'},
                    {'label': 'Rent/Unit', 'value': f"${monthly_rent/1000:.1f}K", 'color': 'purple'}
                ]
            }
        elif building_type == 'restaurant':
            seats = analysis.get('seats', 120)
            revenue_per_seat = analysis.get('annual_revenue', 0) / max(seats, 1)
            return {
                'staffing': [
                    {'label': 'Seats', 'value': seats},
                    {'label': 'Staff Required', 'value': int(seats * 0.3)}  # Industry standard 0.3 staff per seat
                ],
                'revenue': {
                    'Revenue per Seat': f"${revenue_per_seat/1000:.1f}K/yr",
                    'Revenue per SF': f"${analysis.get('annual_revenue', 0) / max(analysis.get('square_footage', 1), 1):.0f}",
                    'Table Turns': f"{2.5 if subtype == 'quick_service' else 1.8}/day"
                },
                'kpis': [
                    {'label': 'Seats', 'value': str(seats), 'color': 'blue'},
                    {'label': 'Rev/Seat', 'value': f"${revenue_per_seat/1000:.0f}K", 'color': 'green'},
                    {'label': 'Food Cost', 'value': '30%', 'color': 'purple'}
                ]
            }
        elif building_type == 'healthcare':
            return {
                'staffing': [
                    {'label': 'Beds per Nurse', 'value': 4.2},
                    {'label': 'Total FTEs', 'value': 750}
                ],
                'revenue': {
                    'Revenue per Employee': '$111K',
                    'Revenue per Bed': '$553K',
                    'Labor Cost Ratio': '52%'
                },
                'kpis': [
                    {'label': 'ALOS', 'value': '3.8d', 'color': 'blue'},
                    {'label': 'Occupancy', 'value': '85%', 'color': 'green'},
                    {'label': 'Rev/Admit', 'value': '$11K', 'color': 'purple'}
                ]
            }
        elif building_type == 'educational':
            return {
                'staffing': [
                    {'label': 'Students per Teacher', 'value': 25},
                    {'label': 'Faculty & Staff', 'value': 45}
                ],
                'revenue': {
                    'Cost per Student': '$12K',
                    'Student/Teacher Ratio': '15:1',
                    'State Funding': '65%'
                },
                'kpis': [
                    {'label': 'School Days', 'value': '180', 'color': 'blue'},
                    {'label': 'Attendance', 'value': '95%', 'color': 'green'},
                    {'label': 'Ratio', 'value': '15:1', 'color': 'purple'}
                ]
            }
        else:
            return {
                'staffing': [
                    {'label': 'SF per Employee', 'value': 150},
                    {'label': 'Janitorial Staff', 'value': 12}
                ],
                'revenue': {
                    'Revenue per SF': '$35',
                    'Lease Rate': '$35/SF',
                    'Occupancy Target': '90%'
                },
                'kpis': [
                    {'label': 'Lease Rate', 'value': '$35/SF', 'color': 'blue'},
                    {'label': 'Occupancy', 'value': '90%', 'color': 'green'},
                    {'label': 'NNN', 'value': '$8/SF', 'color': 'purple'}
                ]
            }
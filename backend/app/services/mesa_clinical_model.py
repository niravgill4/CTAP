import mesa
import random
import math
from typing import Dict, Any, List
import sys
import os
from geopy.distance import geodesic

# Import sibling engine
from .pbpk_engine import PBPKEngine

class ClinicalSiteAgent(mesa.Agent):
    """
    Simulates a physical clinical site / principal investigator.
    Responsible for managing patient visits. When AE cases spike, the site capacity
    breaks down, creating logistical friction for all assigned patients.
    Phase 9: Incorporates 'Investigator Empathy' to mitigate or worsen congestion.
    Phase 10: Incorporates 'Compliance Risk' for site fraud invalidation.
    Phase 11: Incorporates literal Geospatial LAT/LON coordinates.
    """
    def __init__(self, unique_id: int, model: mesa.Model, capacity_modifier: float = 1.0, empathy_modifier: float = 1.0, compliance_risk: float = 0.05, lat: float = 42.3601, lon: float = -71.0589):
        # In Mesa 3.x, Agent constructor takes 'model' as first argument
        super().__init__(model)
        self.unique_id = unique_id
        # Base capability of a site to handle normal patient visits
        self.base_capacity = 20 * capacity_modifier 
        self.empathy_modifier = empathy_modifier # <1.0 is highly empathetic, >1.0 is burned out
        self.compliance_risk = compliance_risk # Chance 0.0-1.0 that this site's data gets thrown out by FDA
        
        self.lat = lat
        self.lon = lon
        
        self.current_burden = 0.0
        self.congestion_penalty_cache = 0.0

    def step(self):
        # Sites act before patients to publish their congestion penalty
        if self.current_burden > self.base_capacity:
            # Overwhelmed site -> high friction for patients
            # Phase 9: A highly empathetic investigator mitigates the friction of a congested wait-room
            raw_penalty = min((self.current_burden - self.base_capacity) / self.base_capacity, 1.0) * 0.4
            self.congestion_penalty_cache = raw_penalty * self.empathy_modifier
        else:
            self.congestion_penalty_cache = 0.0
            
        # Site recovers slowly over time as administrative tasks clear
        self.current_burden = max(0.0, self.current_burden * 0.7)
        
    def report_adverse_event(self, severity: float):
        """Called by a patient when they suffer an AE. Dramatically spikes site burden."""
        self.current_burden += (10.0 * severity)


class PatientAgent(mesa.Agent):
    """
    A single patient going through the trial. Contains demographic RWE,
    a PBPK biological engine state, and a mathematical logistical fatigue state.
    """
    def __init__(self, unique_id: int, model: mesa.Model, demographics: Dict[str, Any], site: ClinicalSiteAgent, subjectivity_scalar: float = 1.0):
        super().__init__(model)
        self.unique_id = unique_id
        self.demographics = demographics
        self.site = site
        self.schedule_idx = 0
        
        # Phase 11: True Geospatial Transit Calculation via API
        agent_lat = self.demographics.get("lat", 42 + random.uniform(-0.5, 0.5))
        agent_lon = self.demographics.get("lon", -71 + random.uniform(-0.5, 0.5))
        self.commute_distance_miles = geodesic((agent_lat, agent_lon), (self.site.lat, self.site.lon)).miles
        
        # Phase 11: True PGx Phenotype Assignment based on Race Geography
        raw_race = str(self.demographics.get("race", "unknown")).lower()
        roll = random.random()
        
        # Historic CYP2D6 Poor Metabolizer Distributions
        if "asian" in raw_race:
            pm_chance, ur_chance = 0.01, 0.02
        elif "black" in raw_race or "african" in raw_race:
            pm_chance, ur_chance = 0.05, 0.15
        elif "white" in raw_race or "caucasian" in raw_race:
            pm_chance, ur_chance = 0.08, 0.05
        else:
            pm_chance, ur_chance = 0.06, 0.06 # Global average
            
        if roll < pm_chance: self.cyp_phenotype = "Poor Metabolizer"
        elif roll < (pm_chance + ur_chance): self.cyp_phenotype = "Ultra-Rapid Metabolizer"
        else: self.cyp_phenotype = "Normal"
            
        # Phase 9: Placebo / Nocebo setup
        self.treatment_arm = "Active" if random.random() < 0.66 else "Placebo"
        self.suggestibility = random.uniform(0.0, 1.0) * subjectivity_scalar # Scaled by Oracle Subjectivity Input
        self.curiosity = random.uniform(0.0, 1.0) # Phase 10: Desire to illegally unblind themselves
        
        # Dual-State Model Variables
        self.compounding_fatigue = 0.0
        self.accumulated_plasma = {"A_absorp": 0.0, "A_central": 0.0, "A_periph": 0.0}
        self.last_visit_day = 0
        
        # Phase 10: Real Disease Progression
        self.disease_progression = random.uniform(0.1, 0.4) # Starting disease severity (0.0 to 1.0)
        
        # Output Tracking
        self.dropped_out = False
        self.dropout_reason = None
        self.dropout_day = None

    def step(self):
        if self.dropped_out:
            return # Dead/Removed agents do nothing
            
        # Continuous Biological execution (PBPK calculation runs every day)
        # Assuming for this simulation, doses happen only exactly at visits.
        # But PK/PD still calculates daily decay and potential acute AEs.
        current_day = self.model.current_day
        days_since_last = current_day - self.last_visit_day
        
        # Phase 9: Placebo vs Active Logic
        if self.treatment_arm == "Active":
            pk_result = self.model.pbpk_engine.calculate_plasma_concentration(
                days_since_dose=days_since_last, 
                state=self.accumulated_plasma,
                is_new_dose=False,
                agent_cyp450_phenotype=self.cyp_phenotype
            )
            plasma_conc = pk_result["plasma_conc"]
            self.accumulated_plasma = pk_result["state"]
            
            # Real AE Check based on true plasma
            ae_result = self.model.pbpk_engine.evaluate_adverse_event(plasma_conc, self.demographics)
            if ae_result["ae_triggered"]:
                self.dropped_out = True
                self.dropout_reason = f"Actual Adverse Event (Plasma: {plasma_conc:.2f}, DNA: {self.cyp_phenotype})"
                self.dropout_day = current_day
                self.site.report_adverse_event(severity=ae_result['toxicity_ratio'])
                return
        else:
            # Phase 9: Psychosomatic Nocebo Effect (No true drug in plasma)
            if random.random() < (0.01 * self.suggestibility):
                self.dropped_out = True
                self.dropout_reason = f"Psychosomatic Nocebo Event (Hallucinated AE)"
                self.dropout_day = current_day
                self.site.report_adverse_event(severity=0.5) # Still requires PI time to manage the fake AE
                return
                
        # Phase 10: Efficacy & Disease Progression
        # If on Placebo, disease gets worse. If Active, disease gets better based on Plasma.
        if self.treatment_arm == "Placebo":
            self.disease_progression += 0.002 # Linear daily worsening
        else:
            # Active drug reduces disease proportionally to plasma concentration
            self.disease_progression = max(0.0, self.disease_progression - (0.005 * plasma_conc))
            
        if self.disease_progression > 0.95:
            self.dropped_out = True
            self.dropout_reason = f"Disease Progression (Lack of Efficacy). Seeking rescue med."
            self.dropout_day = current_day
            return
            
        # Phase 10: Accidental Unblinding (Patient figures out they are on Placebo)
        if self.treatment_arm == "Placebo" and self.curiosity > 0.9:
            # High curiosity patient orders a private home test
            if random.random() < 0.005: 
                self.dropped_out = True
                self.dropout_reason = "Unblinding Fraud (Patient discovered Placebo assignment)"
                self.dropout_day = current_day
                return
            
        # Check if today is a Visit Day based on the protocol schedule
        if self.schedule_idx < len(self.model.visit_schedule):
            next_visit = self.model.visit_schedule[self.schedule_idx]
            
            # Simple modeling: Visit happens on the exact day
            if current_day == next_visit["day"]:
                self.execute_visit(next_visit, current_day, days_since_last)
                
    def execute_visit(self, visit: Dict[str, Any], current_day: int, days_since_last: int):
        # Phase 10: Stochastic Supply Chain Failure
        supply_chain_failure = False
        if random.random() < 0.02: # 2% chance the drug shipment to the site was ruined
            supply_chain_failure = True
            
        # 1. Biological Update (Patient receives dose at visit, IF there was no supply failure)
        if self.treatment_arm == "Active":
            pk_result = self.model.pbpk_engine.calculate_plasma_concentration(
                days_since_dose=0.1, 
                state=self.accumulated_plasma,
                is_new_dose=not supply_chain_failure, # Dose missed if logistics failed
                agent_cyp450_phenotype=self.cyp_phenotype
            )
            self.accumulated_plasma = pk_result["state"]
            
        self.last_visit_day = current_day
        self.schedule_idx += 1
        
        # 2. Logistical State Update
        base_friction = visit["friction_base"]
        
        # Phase 11: Geodesic Commute Friction
        if self.commute_distance_miles > 50:
            base_friction += 0.25 # Over an hour drive each way is very hard for a trial
        elif self.commute_distance_miles > 15:
            base_friction += 0.10
        
        if supply_chain_failure:
            base_friction += 0.35 # Massive frustration for being told to go home without the drug
        
        # Add Site Congestion Friction (MESA SPECIFIC)
        # This is where patients who never "see each other" suffer from the same overworked PI.
        site_friction = self.site.congestion_penalty_cache
        base_friction += site_friction
        
        # Add Global Macro Shocks
        global_shock = self.model.get_global_shock()
        base_friction += global_shock
        
        # Add Demographic Adjustments
        if self.demographics.get("income_tier") == "Low" and self.demographics.get("transit_accessibility") == "Low":
            base_friction += 0.25 
        if self.demographics.get("caregiver_support") == "Yes":
            base_friction -= 0.15 
            
        # 3. Mathematical Decay Memory Update
        recovery = 0.02 * days_since_last
        self.compounding_fatigue = max(0.0, self.compounding_fatigue - recovery) + base_friction
        
        # Attrition Check
        tolerance = 0.85
        if self.compounding_fatigue > tolerance:
            drop_chance = (self.compounding_fatigue - tolerance) * 2.0
            if random.random() < drop_chance:
                self.dropped_out = True
                self.dropout_reason = f"Compounded Logistical Burnout (Site Overload? {site_friction > 0})"
                self.dropout_day = current_day
                

class ClinicalTrialModel(mesa.Model):
    """
    The orchestrator for the entire 2-year simulation. Steps forward chronologically
    day by day, firing environmental shocks and orchestrating Site/Patient interactions.
    """
    def __init__(self, agents_data: List[Dict[str, Any]], num_sites: int = 5, visit_schedule: List[Dict] = None, compound_smiles: str = None, biomarker_variance: str = None, endpoint_subjectivity: str = None, investigator_skill: str = None):
        super().__init__()
        # In Mesa 3.x, the model automatically tracks agents in self.agents
        self.current_day = 0
        self.max_days = 200 # Approx 6 month timeline
        
        # Connect Chemprop to dynamically predict DILI / Renal Tox threshold from SMILES
        from .chemprop_wrapper import ChempropToxPredictor
        
        # Phase 11: Remove hardcoded Wegovy SMILES. Use the actual frontend input.
        actual_smiles = compound_smiles if compound_smiles else "CC(C)CC(C(=O)NC(CCC(=O)O)C(=O)NC(CC1=CNC2=CC=CC=C21)C(=O)NC(CC3=CC=CC=C3)C(=O)N)NC(=O)C(CC4=CC=C(C=C4)O)NC(=O)C(CO)NC(=O)C(CC(C)C)NC(=O)C(C)NC(=O)C(CCC(=O)O)NC(=O)C(C)NC(=O)C5CCCN5C(=O)C(CC(C)C)NC(=O)C(CCC(=O)N)NC(=O)C(CC(=O)N)NC(=O)C(C(C)O)NC(=O)C(CC6=CC=CC=C6)NC(=O)C(CC(=O)O)NC(=O)CNC(=O)C(CCC(=O)O)NC(=O)C(C)(C)C"
        
        chemprop_ai = ChempropToxPredictor()
        predicted_tox_profile = chemprop_ai.get_full_tox_profile(actual_smiles)
        
        # The drug profile mathematically aligns SciPy PBPK with Chemprop ML
        drug_profile = {
            "dose_mg": 2.4,
            "half_life_days": 7.0,
            "toxicity_threshold_mg_L": predicted_tox_profile["toxicity_threshold_mg_L"]
        }
        
        # Phase 9: In Vivo Biomarker Calibration
        # We override Chemprop because we have real Phase II bloodwork from Oracle input.
        phase2_mult = 1.0
        if biomarker_variance and "elevation" in biomarker_variance.lower():
            import re
            m = re.search(r"(\d+)%", biomarker_variance)
            if m: phase2_mult = 1.0 - (float(m.group(1)) / 100.0)
            else: phase2_mult = 0.8
            
        phase2_calibration = {
            "real_tox_threshold_mg_L": predicted_tox_profile["toxicity_threshold_mg_L"] * phase2_mult
        }
        self.pbpk_engine = PBPKEngine(drug_profile, phase2_calibration)
        
        # Phase 11: Bind the actual frontend Visit Schedule parsed from the Zep protocol.
        if visit_schedule:
            self.visit_schedule = visit_schedule
            # Adjust max_days to match the final visit
            if len(self.visit_schedule) > 0:
                self.max_days = self.visit_schedule[-1].get("day", 200) + 14
        else:
            # Fallback Mocked Visit Schedule
            self.visit_schedule = [
                {"visit_id": 1, "day": 0, "name": "Screening", "friction_base": 0.1},
                {"visit_id": 2, "day": 14, "name": "Randomization", "friction_base": 0.1},
                {"visit_id": 3, "day": 28, "name": "Treatment Week 4", "friction_base": 0.15},
                {"visit_id": 4, "day": 84, "name": "Treatment Week 12", "friction_base": 0.20},
                {"visit_id": 5, "day": 168, "name": "End of Study", "friction_base": 0.25}
            ]
        
        # Macro Events
        self.macro_events = [
            {"day": 84, "name": "Competitor Drug Approved", "attrition_spike": 0.15},
            {"day": 150, "name": "Negative Media Article (Side Effects)", "attrition_spike": 0.10}
        ]
        
        # 1. Create Sites (Driven by Investigator Oracle)
        self.sites = []
        for i in range(num_sites):
            capacity_mod = random.uniform(0.5, 1.5)
            
            # Apply Investigator Skill Oracle
            base_empathy = 1.0
            if investigator_skill and "top-tier" in investigator_skill.lower():
                base_empathy = 0.5  # highly empathetic
            elif investigator_skill and "struggling" in investigator_skill.lower():
                base_empathy = 1.5  # high burnout
                
            empathy_mod = base_empathy * random.uniform(0.8, 1.2)
            
            # Phase 10: Site Compliance Risk (Chance the site is investigated and thrown out)
            compliance_risk = random.uniform(0.0, 0.15) 
            
            # Phase 11: Real Coordinates
            site_lat = 42.0 + random.uniform(-0.3, 0.3)
            site_lon = -71.5 + random.uniform(-0.3, 0.3)
            
            site = ClinicalSiteAgent(i, self, capacity_modifier=capacity_mod, empathy_modifier=empathy_mod, compliance_risk=compliance_risk, lat=site_lat, lon=site_lon)
            self.sites.append(site)
            
        # Subjectivity Oracle Parsing
        subjectivity_scalar = 1.0
        if endpoint_subjectivity:
            if "highly objective" in endpoint_subjectivity.lower(): subjectivity_scalar = 0.1
            elif "highly subjective" in endpoint_subjectivity.lower(): subjectivity_scalar = 2.5
            
        # 2. Create Patients and assign to sites
        for a_dict in agents_data:
            assigned_site = random.choice(self.sites)
            patient = PatientAgent(a_dict.get("agent_id", random.randint(1000,99999)), self, a_dict, assigned_site, subjectivity_scalar=subjectivity_scalar)
            
        self.running = True

    def get_global_shock(self) -> float:
        """Calculates identical global friction for all agents based on current day."""
        shock_val = 0.0
        for ev in self.macro_events:
            if self.current_day >= ev["day"] and self.current_day <= (ev["day"] + 14):
                shock_val += ev["attrition_spike"]
        return shock_val

    def step(self):
        """Advance the model by one logic step (1 day)."""
        if self.current_day > self.max_days:
            self.running = False
            return
            
        # Phase 10: Regulatory/Protocol Amendment Chaos
        # Microscopic daily chance that the DSMB forces an amendment (like an emergency safety MRI),
        # pushing up the friction of every remaining visit globally.
        if random.random() < 0.002: 
            for visit in self.visit_schedule:
                visit["friction_base"] += 0.10
            
        # Mesa 3.x: Explicitly step through agent categories
        # Sites update congestion first, then patients react
        self.agents.select(lambda a: isinstance(a, ClinicalSiteAgent)).do("step")
        self.agents.select(lambda a: isinstance(a, PatientAgent)).do("step")
        self.current_day += 1

    def generate_results(self) -> List[Dict]:
        results = []
        for agent in self.agents:
            if isinstance(agent, PatientAgent):
                # Phase 10: Site Fraud / FDA Audit Failure
                # If the site fails the audit, all patient data is invalidated (treated as dropped out)
                if random.random() < agent.site.compliance_risk:
                    agent.dropped_out = True
                    agent.dropout_reason = f"FDA Audit Failure (Site Data Scrapped)"
                    
                # Phase 10: Missing Data Imputation (MCAR)
                # Randomly mask 5% of final fatigue stats representing sloppy nursing logs
                final_fatigue_record = agent.compounding_fatigue
                if random.random() < 0.05:
                    final_fatigue_record = None # Statistician must impute this later
                    
                results.append({
                    "user_name": agent.demographics.get("user_name"),
                    "bio": agent.demographics.get("bio"),
                    "visits_completed": agent.schedule_idx,
                    "dropped_out": agent.dropped_out,
                    "dropout_reason": agent.dropout_reason,
                    "dropout_day": agent.dropout_day,
                    "final_fatigue": final_fatigue_record
                })
        return results

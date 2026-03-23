import math
import random
import numpy as np
from scipy.integrate import odeint
from typing import Dict, Any

class PBPKEngine:
    """
    Physiologically Based Pharmacokinetic (PBPK) Engine.
    Uses SciPy Ordinary Differential Equations (ODEs) to model true
    multi-compartment drug distribution and plasma concentration tracking.
    """
    def __init__(self, drug_profile: Dict[str, Any], phase2_calibration: Dict[str, float] = None):
        """
        Initialize with standard kinetic parameters.
        Phase 9: Added `phase2_calibration` to allow real human biomarker bloodwork
        (e.g., AST/ALT ratios from Phase II trials) to override Chemprop Deep Learning predictions.
        """
        self.dose = drug_profile.get("dose_mg", 2.4)
        self.F = drug_profile.get("bioavailability", 0.89)
        self.V_c = drug_profile.get("volume_central_L", 10.0) # Central plasma compartment
        self.V_p = drug_profile.get("volume_peripheral_L", 25.0) # Tissue compartment
        
        half_life = drug_profile.get("half_life_days", 7.0)
        self.base_ke = math.log(2) / half_life # Baseline Elimination from central
        self.ka = drug_profile.get("absorption_rate_day", 0.5) # Absorption from SubQ/GI
        self.k12 = drug_profile.get("clearance_central_to_periph", 0.1)
        self.k21 = drug_profile.get("clearance_periph_to_central", 0.05)
        
        # Phase 9: In Vivo Biomarker Calibration
        # If real world human bloodwork data is passed, we NEVER trust exactly what the AI predicted.
        if phase2_calibration and "real_tox_threshold_mg_L" in phase2_calibration:
            self.tox_threshold = phase2_calibration["real_tox_threshold_mg_L"]
        else:
            self.tox_threshold = drug_profile.get("toxicity_threshold_mg_L", 0.45)
        
        # This will hold the dynamic elimination rate per-agent during the ODE solve
        self._current_agent_ke = self.base_ke
        
    def _ode_system(self, y, t):
        """
        Differential equations governing the 3-state body system.
        y[0] = Amount at absorption site (e.g. GI tract, SubQ depot)
        y[1] = Amount in Central Compartment (Plasma)
        y[2] = Amount in Peripheral Compartment (Tissue)
        """
        A_absorp, A_central, A_periph = y
        dAbsorp_dt = -self.ka * A_absorp
        dCentral_dt = (self.ka * A_absorp) - (self._current_agent_ke * A_central) - (self.k12 * A_central) + (self.k21 * A_periph)
        dPeriph_dt = (self.k12 * A_central) - (self.k21 * A_periph)
        return [dAbsorp_dt, dCentral_dt, dPeriph_dt]

    def calculate_plasma_concentration(self, days_since_dose: float, state: Dict[str, float] = None, is_new_dose: bool = False, agent_cyp450_phenotype: str = "Normal") -> Dict[str, Any]:
        """
        Solves the ODE system over the specified time gap using SciPy.
        Phase 9: Integrates Pharmacogenomic (PGx) clearance rate adjustment based on the patient's DNA.
        """
        # PGx CYP450 Modifier
        if agent_cyp450_phenotype == "Poor Metabolizer":
            self._current_agent_ke = self.base_ke * 0.4 # Extremely slow elimination = extreme toxicity risk
        elif agent_cyp450_phenotype == "Ultra-Rapid Metabolizer":
            self._current_agent_ke = self.base_ke * 2.5 # Extremely fast elimination = no efficacy
        else:
            self._current_agent_ke = self.base_ke
            
        if state is None:
            # Initialization zero-state
            state = {"A_absorp": 0.0, "A_central": 0.0, "A_periph": 0.0}
            
        if is_new_dose:
            # Patient takes their shot/pill, adding mass to the absorption site
            state["A_absorp"] += (self.dose * self.F)
            
        y0 = [state["A_absorp"], state["A_central"], state["A_periph"]]
        
        # High resolution time grid for ODE solver
        t = np.linspace(0, max(0.1, days_since_dose), 50)
        
        sol = odeint(self._ode_system, y0, t)
        
        # Pull the final biological state at the end of the time period
        final_Absorp, final_Central, final_Periph = sol[-1]
        
        # Plasma Concentration = Mass in Central / Volume of Central
        plasma_conc = max(0.0, final_Central / self.V_c)
        
        new_state = {
            "A_absorp": final_Absorp,
            "A_central": final_Central,
            "A_periph": final_Periph
        }
        
        return {
            "plasma_conc": plasma_conc,
            "state": new_state
        }

    def evaluate_adverse_event(self, concentration: float, agent_demographics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pharmacodynamics (PD): Does this True Plasma Concentration trigger an AE?
        Phase 11 Fix: Replaced arbitrary exponential algebra with the classical
        Emax / Hill Equation, which is the global biological standard for Dose-Response modeling.
        """
        # Emax Model: Probability_AE = (Emax * C^Hill) / (EC50^Hill + C^Hill)
        # Emax = 1.0 (100% chance of AE at infinite dose)
        # EC50 = self.tox_threshold (Concentration where 50% of people suffer Severe AEs)
        
        hill_coefficient = 2.5 # Steepness of the toxicity onset (biologics usually have steep sigmoid curves)
        
        if concentration <= 0:
            base_ae_prob = 0.0
        else:
            base_ae_prob = (1.0 * (concentration ** hill_coefficient)) / ((self.tox_threshold ** hill_coefficient) + (concentration ** hill_coefficient))
            
        # Age-based Organ Clearance Adjustments
        try:
            age = int(agent_demographics.get("age", 50))
        except (ValueError, TypeError):
            age = 50
            
        if age > 65:
            base_ae_prob *= 1.4 # Elderly renal clearance adjustments
            
        variance = random.uniform(0.8, 1.2)
        final_prob = min(base_ae_prob * variance, 1.0)
        
        trigger_ae = random.random() < final_prob
        
        return {
            "ae_triggered": trigger_ae,
            "plasma_concentration": concentration,
            "toxicity_ratio": concentration / max(0.001, self.tox_threshold),
            "severity": "Severe" if trigger_ae else "Mild"
        }

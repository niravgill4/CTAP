import os
import sys
import json
import logging

# Ensure the app directories are on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.mesa_clinical_model import ClinicalTrialModel

logger = logging.getLogger(__name__)

def run_mesa_simulation(simulation_id: str):
    """
    Executes the pure Mesa Agent-Based timeline simulation.
    This replaces basic loop iteration.
    """
    sim_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads/simulations', simulation_id))
    
    # Phase 8: Synthea True EHR Integration
    from app.services.synthea_parser import SyntheaEHRParser
    parser = SyntheaEHRParser(sim_dir)
    
    if parser.has_synthea_data():
        logger.info("Synthea Phase 8: Massive synthetic CSV data detected. Overriding LLM hallucinated profiles.")
        agents = parser.parse_patients(limit=250)
    else:
        logger.warning("No Synthea CSV found in simulation dir. Falling back to LLM-generated profiles.")
        with open(os.path.join(sim_dir, "reddit_profiles.json"), 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
    logger.info(f"Loaded {len(agents)} agents for Mesa Simulation.")
    
    # Phase 11: Connect the actual frontend config driving the UI
    config_path = os.path.join(sim_dir, "simulation_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            sim_config = json.load(f)
            visit_schedule = sim_config.get("compiled_events", None)
            compound_smiles = sim_config.get("compound_smiles", None)
            biomarker_variance = sim_config.get("biomarker_variance", None)
            endpoint_subjectivity = sim_config.get("endpoint_subjectivity", None)
            investigator_skill = sim_config.get("investigator_skill", None)
    else:
        visit_schedule, compound_smiles = None, None
        biomarker_variance, endpoint_subjectivity, investigator_skill = None, None, None
        
    # Initialize the continuous FDA-grade ABM
    # We assign them to 5 disparate Clinical Sites
    model = ClinicalTrialModel(
        agents, 
        num_sites=5, 
        visit_schedule=visit_schedule, 
        compound_smiles=compound_smiles,
        biomarker_variance=biomarker_variance,
        endpoint_subjectivity=endpoint_subjectivity,
        investigator_skill=investigator_skill
    )
    
    # Run the model day by day for 200 days
    logger.info(f"Executing Mesa Engine for 200 continuous days of PK/PD modeling...")
    while model.running:
        model.step()
        
    results = model.generate_results()
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_clinical_workflow.py <simulation_id>")
        sys.exit(1)
        
    data = run_mesa_simulation(sys.argv[1])
    drops = sum(1 for a in data if a["dropped_out"])
    
    # Check site congestion logs
    overloaded_sites = 0 # To be tracked deeply in future
    
    print(f"Mesa Simulation Enterprise Execution Complete: {len(data)} patients across 5 Sites evaluated.")
    print(f"Final Attrition: {drops}/{len(data)} ({(drops/len(data))*100:.1f}%)")

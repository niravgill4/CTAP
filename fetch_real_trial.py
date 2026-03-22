import urllib.request
import json
import os

def fetch_trial_data(nct_id="NCT04280705"):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    protocolSection = data.get("protocolSection", {})
    descriptionModule = protocolSection.get("descriptionModule", {})
    eligibilityModule = protocolSection.get("eligibilityModule", {})
    designModule = protocolSection.get("designModule", {})
    contactsLocationsModule = protocolSection.get("contactsLocationsModule", {})
    outcomesModule = protocolSection.get("outcomesModule", {})
    
    os.makedirs("test_data", exist_ok=True)
    
    # 1. Clinical Trial Protocol (CTP)
    ctp_content = f"CLINICAL TRIAL PROTOCOL\nNCT ID: {nct_id}\n\n"
    ctp_content += f"Brief Summary:\n{descriptionModule.get('briefSummary', '')}\n\n"
    ctp_content += f"Detailed Description:\n{descriptionModule.get('detailedDescription', '')}\n\n"
    ctp_content += f"Eligibility Criteria:\n{eligibilityModule.get('eligibilityCriteria', '')}\n"
    
    with open(f"test_data/{nct_id}_Protocol.txt", "w", encoding="utf-8") as f:
        f.write(ctp_content)
        
    # 2. Schedule of Assessments (SoA)
    soa_content = f"SCHEDULE OF ASSESSMENTS\nNCT ID: {nct_id}\n\n"
    soa_content += f"Study Type: {designModule.get('studyType', '')}\n"
    phases = designModule.get("phases", [])
    soa_content += f"Phases: {', '.join(phases)}\n\n"
    
    soa_content += "Primary Outcomes:\n"
    for outcome in outcomesModule.get("primaryOutcomes", []):
        soa_content += f"- {outcome.get('measure')}: {outcome.get('description', '')} (Time Frame: {outcome.get('timeFrame', '')})\n"
        
    soa_content += "\nSecondary Outcomes:\n"
    for outcome in outcomesModule.get("secondaryOutcomes", []):
        soa_content += f"- {outcome.get('measure')}: {outcome.get('description', '')} (Time Frame: {outcome.get('timeFrame', '')})\n"

    with open(f"test_data/{nct_id}_SoA.txt", "w", encoding="utf-8") as f:
        f.write(soa_content)

    # 3. Informed Consent Form (ICF) mock based on arms
    icf_content = f"INFORMED CONSENT FORM (Derived Summary)\nNCT ID: {nct_id}\n\n"
    icf_content += "Intervention Arms:\n"
    for arm in designModule.get("armsInterventionsModule", {}).get("armGroups", []):
        icf_content += f"- {arm.get('label')}:\n  Description: {arm.get('description', '')}\n"
        
    with open(f"test_data/{nct_id}_ICF.txt", "w", encoding="utf-8") as f:
        f.write(icf_content)

    # 4. Investigator Brochure (IB) mock based on locations
    ib_content = f"INVESTIGATOR BROCHURE & SITE DETAILS\nNCT ID: {nct_id}\n\n"
    ib_content += f"Central Contact: {contactsLocationsModule.get('centralContacts', [{'name': 'N/A'}])[0].get('name')}\n\n"
    ib_content += "Facility Locations:\n"
    for loc in contactsLocationsModule.get("locations", [])[:20]: # limit to 20
        ib_content += f"- {loc.get('facility', 'Unknown')}, {loc.get('city', '')}, {loc.get('country', '')}\n"
        
    with open(f"test_data/{nct_id}_IB.txt", "w", encoding="utf-8") as f:
        f.write(ib_content)
        
    print(f"Successfully generated 4 real-data documents for {nct_id} in test_data folder.")

if __name__ == "__main__":
    fetch_trial_data("NCT04280705") # Remdesivir ACTT-1 trial

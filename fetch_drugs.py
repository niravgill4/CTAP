import urllib.request
import json
import os

trials = {
    'NCT04368728': 'Pfizer_BioNTech_COVID_Vaccine',
    'NCT03548935': 'Wegovy_Semaglutide_STEP1',
    'NCT03525818': 'Trikafta_Cystic_Fibrosis'
}

for nct, name in trials.items():
    url = f'https://clinicaltrials.gov/api/v2/studies/{nct}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            protocol = data.get('protocolSection', {})
            desc_mod = protocol.get('descriptionModule', {})
            elig_mod = protocol.get('eligibilityModule', {})
            cond_mod = protocol.get('conditionsModule', {})
            
            out_lines = [
                f"TRIAL NAME: {name.replace('_', ' ')}",
                f"NCT ID: {nct}",
                f"CONDITIONS: {', '.join(cond_mod.get('conditions', []))}",
                "",
                "--- BRIEF SUMMARY ---",
                desc_mod.get('briefSummary', ''),
                "",
                "--- DETAILED DESCRIPTION ---",
                desc_mod.get('detailedDescription', ''),
                "",
                "--- ELIGIBILITY CRITERIA ---",
                elig_mod.get('eligibilityCriteria', ''),
                "",
                "--- DEMOGRAPHIC STRICTNESS ---",
                f"Sex: {elig_mod.get('sex', 'ALL')}",
                f"Min Age: {elig_mod.get('minimumAge', 'N/A')}",
                f"Max Age: {elig_mod.get('maximumAge', 'N/A')}"
            ]
            
            filepath = f"c:/Users/Nirav/.vscode/projects/MiroFish/frontend/public/{nct}_{name}_Protocol.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(out_lines))
            print(f"Saved: {filepath}")
    except Exception as e:
        print(f"Failed {nct}: {e}")

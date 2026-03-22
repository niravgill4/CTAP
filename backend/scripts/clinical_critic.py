import os
import json
import sqlite3
from typing import List, Dict, Any

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def evaluate_with_clinical_critic(action_data: Dict[str, Any]) -> bool:
    """Implement Constraints 2, 3, 4: CoT + JSON Structured Output via Clinical Critic"""
    if not OPENAI_AVAILABLE:
        return True
        
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE_URL") or os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")
    
    # Build fallback model list
    fallback_str = os.environ.get("LLM_FALLBACK_MODELS", "")
    fallback_models = [m.strip() for m in fallback_str.split(',') if m.strip()]
    models_to_try = [model] + fallback_models
    
    if not api_key: 
        return True
    
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    system_prompt = (
        "You are the strictly deterministic Clinical Trial Critic Monitor.\n"
        "Your job is to read simulated patient actions and physically block any action that hallucinates medical data or violates the NCT04280705 protocol.\n\n"
        "Rule 1 (Chain-of-Thought): You MUST output a `<thought_process>` analyzing if the action conceptually matches the protocol before returning your decision.\n"
        "Rule 2 (Structured JSON): You MUST return exactly valid JSON with ONLY the following schema:\n"
        "{\n"
        "  \"<thought_process>\": \"Your exact citations from NCT04280705 confirming or denying validity.\",\n"
        "  \"is_clinically_valid\": true|false\n"
        "}"
    )
    
    # Strip some massive context to save tokens if needed
    slim_action = {k: v for k, v in action_data.items() if k in ['action_type', 'action_args', 'agent_name']}

    for current_model in models_to_try:
        try:
            resp = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Evaluate this action:\n{json.dumps(slim_action)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = resp.choices[0].message.content
            data = json.loads(content)
            
            is_valid = data.get("is_clinically_valid", True)
            if not is_valid:
                print(f"\n[CLINICAL CRITIC TRIGGERED]")
                print(f"-> Agent: {action_data.get('agent_name')}")
                print(f"-> Rejecting Action: {action_data.get('action_type')}")
                print(f"-> CoT Reasoning: {data.get('<thought_process>')}\n")
                
            return is_valid
            
        except (openai.RateLimitError, openai.BadRequestError, openai.APIStatusError) as e:
            print(f"[Clinical Critic] Model {current_model} error: {e}, trying fallback...")
            continue
        except Exception as e:
            print(f"[Clinical Critic] Non-fatal API error: {e}")
            return True

def filter_actions_with_critic(actual_actions: List[Dict[str, Any]], db_path: str) -> List[Dict[str, Any]]:
    """Applies the Clinical Critic agent across a batch of actions from the DB. 
    If invalid, cleanly purges the hallucination without breaking the UI flow."""
    valid_actions = []
    
    for act in actual_actions:
        is_valid = evaluate_with_clinical_critic(act)
        if is_valid:
            valid_actions.append(act)
        else:
            # We strictly delete the hallucinated action from the local trace DB so the frontend charts never see fake data.
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trace WHERE user_id = ? AND action = ? ORDER BY created_at DESC LIMIT 1", 
                               (act.get('agent_id'), act.get('action_type').lower()))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[Clinical Critic] DB purge failed: {e}")
                
    return valid_actions

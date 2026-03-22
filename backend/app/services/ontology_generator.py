"""
本体生成服务
接口1：分析文本内容，生成适合社会模拟的实体和关系类型定义
"""

import json
from typing import Dict, Any, List, Optional, Callable
from ..utils.llm_client import LLMClient
from ..config import Config


# Clinical Trial Attrition Predictor — Ontology System Prompt
ONTOLOGY_SYSTEM_PROMPT = """You are an expert clinical trial knowledge graph ontology designer for the Clinical Trial Attrition Predictor system.
Your task is to analyze uploaded clinical trial documents (Protocol, Schedule of Assessments, ICF, Investigator's Brochure) and design an ontology for SIMULATING PATIENT ATTRITION.

**CRITICAL: Output ONLY valid JSON. No explanation, no markdown fences, no extra text.**

## Core Task Background

We are building a **Clinical Trial Attrition Predictor**. In this system:
- Patient agents experience the trial day by day, weighing protocol compliance against physical and logistical friction
- The motivation decay model: ΔM(t) = cumulative_rewards - (physical_friction + logistical_friction)
- When M(t) < dropout_threshold, the patient agent drops out
- We must extract entities and relationships that model THIS SPECIFIC DYNAMIC from the uploaded clinical trial documents

Entities must be **real clinical entities** that participate in or affect trial dynamics:
- **Can be**: Patient (participant), Investigator, ClinicalSite, TreatmentArm, ClinicalVisit, AdverseEvent, Regulator, Sponsor, Procedure
- **Cannot be**: abstract concepts like "patient burden", "attrition", "compliance" as standalone entities

## Output Format

Output JSON with this exact structure:

{
    "entity_types": [
        {
            "name": "EntityName (PascalCase English)",
            "description": "Description under 95 chars English",
            "attributes": [
                {
                    "name": "attribute_name_snake_case",
                    "type": "text",
                    "description": "What this captures for attrition modeling"
                }
            ],
            "examples": ["Example 1", "Example 2"]
        }
    ],
    "edge_types": [
        {
            "name": "RELATIONSHIP_UPPER_SNAKE_CASE",
            "description": "Description under 95 chars English",
            "source_targets": [
                {"source": "SourceEntityType", "target": "TargetEntityType"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Analysis of uploaded trial documents and key attrition risk factors identified."
}

## Design Guidelines

### 1. Entity Types — EXACTLY 10 required

The LAST 2 must always be these fallback types:
- `Person`: Fallback for any individual not matching a more specific type
- `Organization`: Fallback for any organization not matching a more specific type

The FIRST- Focus on two categories of entities:
    1. **Participants** (Human): e.g., Patient, Investigator, ClinicalSite. These will be simulated as active agents.
    2. **Protocol Evidence** (Systems/Events): e.g., Medication, DrugDose, AdverseEvent, SideEffect, DiagnosticTest. These are constraints or events, NOT people.
- Labels for Participants should be singular (e.g., 'Patient', not 'Patients').
- Ensure drug dosages (e.g., '2.4mg') are labeled as 'DrugDose', not 'Person' or 'Participant'.
Priority entity types to use (adapt based on document content):
- `Patient`: Trial participant who may drop out. Attributes: age_range, income_tier (Low/Medium/High), digital_literacy (Low/High), transit_accessibility (Low/High), mobility_score (1-10), caregiver_support (Yes/No)
- `Investigator`: Principal investigator or site physician. Attributes: trial_role, site_affiliation
- `ClinicalSite`: Hospital, clinic, research center. Attributes: site_location, site_type
- `TreatmentArm`: Intervention group (drug, placebo, dose). Attributes: arm_label, dosing_frequency
- `ClinicalVisit`: Scheduled protocol visit. Attributes: visit_week, assessment_burden_hours
- `AdverseEvent`: Reported side effect or safety signal. Attributes: severity_grade, occurrence_rate
- `Sponsor`: Pharmaceutical company or CRO. Attributes: org_type
- `Regulator`: FDA, EMA, IRB overseeing the trial. Attributes: jurisdiction

### 2. Edge Types — 6-10 required

Priority relationships for attrition modeling:
- `PARTICIPATES_IN`: Patient participates in TreatmentArm
- `DROPS_OUT_OF`: Patient drops out of TreatmentArm (the key attrition event)
- `REPORTS_SIDE_EFFECT`: Patient reports AdverseEvent
- `ATTENDS_VISIT`: Patient attends ClinicalVisit
- `CONDUCTED_AT`: ClinicalVisit conducted at ClinicalSite
- `OVERSEEN_BY`: TreatmentArm overseen by Investigator
- `SPONSORED_BY`: Trial sponsored by Sponsor
- `REGULATED_BY`: Trial regulated by Regulator
- `CAUSES_COMPLIANCE_FRICTION`: AdverseEvent causes friction for Patient

### 3. Attribute Rules
- NEVER use reserved words: `name`, `uuid`, `group_id`, `created_at`, `summary`
- USE instead: `full_name`, `patient_id`, `trial_role`, `site_location`, `arm_label`, etc.
- Keep descriptions under 95 characters
"""


class OntologyGenerator:
    """
    本体生成器
    分析文本内容，生成实体和关系类型定义
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        if llm_client:
            self.llm_client = llm_client
        else:
            # 优先使用本体生成专用配置，否则回退到全局LLM配置
            api_key = Config.ONTOLOGY_LLM_API_KEY or Config.LLM_API_KEY
            base_url = Config.ONTOLOGY_LLM_BASE_URL or Config.LLM_BASE_URL
            model_name = Config.ONTOLOGY_LLM_MODEL_NAME or Config.LLM_MODEL_NAME
            
            self.llm_client = LLMClient(
                api_key=api_key,
                base_url=base_url,
                model=model_name
            )
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None,
        wait_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        生成本体定义
        
        Args:
            document_texts: 文档文本列表
            simulation_requirement: 模拟需求描述
            additional_context: 额外上下文
            
        Returns:
            本体定义（entity_types, edge_types等）
        """
        # 构建用户消息
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # 调用LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.0,
            max_tokens=4096,
            wait_callback=wait_callback
        )
        
        # 验证和后处理
        result = self._validate_and_process(result)
        
        return result
    
    # 传给 LLM 的文本最大长度（缩减至1.5万字以适应本地模型性能和上下文限制）
    MAX_TEXT_LENGTH_FOR_LLM = 15000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """构建用户消息"""
        
        # 合并文本
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # 如果文本超过5万字，截断（仅影响传给LLM的内容，不影响图谱构建）
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...(原文共{original_length}字，已截取前{self.MAX_TEXT_LENGTH_FOR_LLM}字用于本体分析)..."
        
        message = f"""## 模拟需求

{simulation_requirement}

## 文档内容

{combined_text}
"""
        
        if additional_context:
            message += f"""
## 额外说明

{additional_context}
"""
        
        message += """
请根据以上内容，设计适合社会舆论模拟的实体类型和关系类型。

**必须遵守的规则**：
1. 必须正好输出10个实体类型
2. 最后2个必须是兜底类型：Person（个人兜底）和 Organization（组织兜底）
3. 前8个是根据文本内容设计的具体类型
4. 所有实体类型必须是现实中可以发声的主体，不能是抽象概念
5. 属性名不能使用 name、uuid、group_id 等保留字，用 full_name、org_name 等替代
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证和后处理结果"""
        
        # 确保必要字段存在
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # 验证实体类型
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # 确保description不超过100字符
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # 验证关系类型
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API 限制：最多 10 个自定义实体类型，最多 10 个自定义边类型
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        # 兜底类型定义
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # 检查是否已有兜底类型
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # 需要添加的兜底类型
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # 如果添加后会超过 10 个，需要移除一些现有类型
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # 计算需要移除多少个
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # 从末尾移除（保留前面更重要的具体类型）
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # 添加兜底类型
            result["entity_types"].extend(fallbacks_to_add)
        
        # 最终确保不超过限制（防御性编程）
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        将本体定义转换为Python代码（类似ontology.py）
        
        Args:
            ontology: 本体定义
            
        Returns:
            Python代码字符串
        """
        code_lines = [
            '"""',
            '自定义实体类型定义',
            '由MiroFish自动生成，用于社会舆论模拟',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== 实体类型定义 ==============',
            '',
        ]
        
        # 生成实体类型
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== 关系类型定义 ==============')
        code_lines.append('')
        
        # 生成关系类型
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # 转换为PascalCase类名
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # 生成类型字典
        code_lines.append('# ============== 类型配置 ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # 生成边的source_targets映射
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)


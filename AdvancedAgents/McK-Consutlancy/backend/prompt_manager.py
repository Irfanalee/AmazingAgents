import os
import re
from typing import Dict, List, Optional

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

PROMPT_METADATA = [
    {"id": "executive_strategy", "filename": "0_ExecutiveStrategy-Master.md", "order": 0},
    {"id": "tam_analysis", "filename": "1_TAM.md", "order": 1},
    {"id": "competitive_landscape", "filename": "2_CompetetiveLandscapte.md", "order": 2},
    {"id": "customer_personas", "filename": "3_CustomerPersonas.md", "order": 3},
    {"id": "industry_trends", "filename": "4_IndustryTrendAnalysis.md", "order": 4},
    {"id": "swot_porters", "filename": "5_SWOTandP5F.md", "order": 5},
    {"id": "pricing_strategy", "filename": "6_PricingStrategyAnalysis.md", "order": 6},
    {"id": "gtm_strategy", "filename": "7_GTMStrategy.md", "order": 7},
    {"id": "customer_journey", "filename": "8_CustomerJourneyMappy.md", "order": 8},
    {"id": "financial_model", "filename": "9_FinModUnitEco.md", "order": 9},
    {"id": "risk_assessment", "filename": "10_RiskAssesmentAndScenerioPlan.md", "order": 10},
    {"id": "market_entry", "filename": "11_MarketEntryNExpan.md", "order": 11},
]

# Short display names for sidebar
PROMPT_SHORT_NAMES = {
    "executive_strategy": "Executive Strategy",
    "tam_analysis": "TAM Analysis",
    "competitive_landscape": "Competitive Landscape",
    "customer_personas": "Customer Personas",
    "industry_trends": "Industry Trends",
    "swot_porters": "SWOT + Porter's 5",
    "pricing_strategy": "Pricing Strategy",
    "gtm_strategy": "GTM Strategy",
    "customer_journey": "Customer Journey",
    "financial_model": "Financial Model",
    "risk_assessment": "Risk Assessment",
    "market_entry": "Market Entry",
}

# Extra inputs specific to each prompt beyond shared context
EXTRA_INPUT_DEFINITIONS = {
    "gtm_strategy": [
        {
            "key": "budget",
            "label": "Marketing Budget",
            "placeholder": "e.g. $50,000",
            "required": False,
        }
    ],
    "market_entry": [
        {
            "key": "target_market",
            "label": "Target Market / Geography",
            "placeholder": "e.g. Southeast Asia, Enterprise B2B in EU",
            "required": False,
        }
    ],
    "financial_model": [
        {
            "key": "current_revenue",
            "label": "Current Monthly Revenue",
            "placeholder": "e.g. $10,000/mo or pre-revenue",
            "required": False,
        },
        {
            "key": "growth_rate",
            "label": "Current Growth Rate",
            "placeholder": "e.g. 15% MoM",
            "required": False,
        },
    ],
    "pricing_strategy": [
        {
            "key": "current_price",
            "label": "Current Price Point",
            "placeholder": "e.g. $99/mo or not launched yet",
            "required": False,
        },
        {
            "key": "cost_structure",
            "label": "Cost Structure",
            "placeholder": "e.g. $20 COGS, $30 support per customer",
            "required": False,
        },
    ],
    "customer_journey": [
        {
            "key": "conversion_rate",
            "label": "Current Conversion Rate",
            "placeholder": "e.g. 3% trial-to-paid",
            "required": False,
        }
    ],
}


def load_prompt_file(filename: str) -> Optional[Dict]:
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        content = f.read().strip()
    lines = content.split("\n")
    title = lines[0].strip() if lines else filename
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else content
    return {"title": title, "body": body, "raw": content}


def extract_placeholders(text: str) -> List[str]:
    return list(set(re.findall(r"\[([^\]]+)\]", text)))


def get_all_prompts() -> List[Dict]:
    prompts = []
    for meta in PROMPT_METADATA:
        data = load_prompt_file(meta["filename"])
        if data:
            placeholders = extract_placeholders(data["raw"])
            prompts.append(
                {
                    "id": meta["id"],
                    "order": meta["order"],
                    "title": data["title"],
                    "short_name": PROMPT_SHORT_NAMES.get(meta["id"], data["title"]),
                    "body": data["body"],
                    "placeholders": placeholders,
                    "extra_inputs": EXTRA_INPUT_DEFINITIONS.get(meta["id"], []),
                }
            )
    return prompts


def get_prompt_by_id(prompt_id: str) -> Optional[Dict]:
    for p in get_all_prompts():
        if p["id"] == prompt_id:
            return p
    return None


def build_full_context(ctx) -> str:
    parts = []
    if ctx.business_name:
        parts.append(f"Business: {ctx.business_name}")
    if ctx.product_description:
        parts.append(f"Product: {ctx.product_description}")
    if ctx.industry:
        parts.append(f"Industry: {ctx.industry}")
    if ctx.stage:
        parts.append(f"Stage: {ctx.stage}")
    if ctx.target_customer:
        parts.append(f"Target Customer: {ctx.target_customer}")
    if ctx.geography:
        parts.append(f"Geography: {ctx.geography}")
    if ctx.revenue:
        parts.append(f"Revenue: {ctx.revenue}")
    if ctx.team_size:
        parts.append(f"Team Size: {ctx.team_size}")
    if ctx.main_challenge:
        parts.append(f"Main Challenge: {ctx.main_challenge}")
    return "; ".join(parts) if parts else "No context provided"


def fill_prompt(prompt_id: str, ctx, extra_inputs: Dict[str, str] = {}) -> str:
    prompt = get_prompt_by_id(prompt_id)
    if not prompt:
        return ""

    full_context = build_full_context(ctx)

    values = {
        "business_name": ctx.business_name or "our business",
        "product_description": ctx.product_description or "our product",
        "industry": ctx.industry or "our industry",
        "target_customer": ctx.target_customer or "our target customers",
        "geography": ctx.geography or "our primary market",
        "full_context": full_context,
        # extra inputs with sensible defaults
        "budget": extra_inputs.get("budget", "the available budget"),
        "target_market": extra_inputs.get(
            "target_market", ctx.geography or "new target market"
        ),
        "current_revenue": extra_inputs.get(
            "current_revenue", ctx.revenue or "not disclosed"
        ),
        "growth_rate": extra_inputs.get("growth_rate", "not specified"),
        "current_price": extra_inputs.get("current_price", "not yet determined"),
        "cost_structure": extra_inputs.get("cost_structure", "not detailed"),
        "conversion_rate": extra_inputs.get("conversion_rate", "not specified"),
    }

    # Ordered most-specific first to avoid partial replacements
    replacements = [
        # Long describe / full context placeholders
        (
            "[PROVIDE FULL CONTEXT — PRODUCT, MARKET, STAGE, TEAM SIZE, REVENUE, GOALS, BIGGEST CHALLENGE]",
            values["full_context"],
        ),
        (
            "[DESCRIBE PRODUCT, MARKET, BUDGET, TIMELINE]",
            values["full_context"],
        ),
        (
            "[DESCRIBE YOUR BUSINESS AND POSITIONING]",
            values["full_context"],
        ),
        (
            "[DESCRIBE YOUR BUSINESS AND MARKET]",
            values["full_context"],
        ),
        (
            "[DESCRIBE BUSINESS, STAGE, KEY DEPENDENCIES]",
            values["full_context"],
        ),
        (
            "[DESCRIBE BUSINESS MODEL, CURRENT REVENUE, COSTS, GROWTH RATE]",
            values["full_context"],
        ),
        (
            "[DESCRIBE PRODUCT, CURRENT PRICE, TARGET CUSTOMER, COST STRUCTURE]",
            values["full_context"],
        ),
        (
            "[DESCRIBE PRODUCT, CUSTOMER TYPE, CURRENT CONVERSION RATE]",
            values["full_context"],
        ),
        (
            "[DESCRIBE CURRENT BUSINESS, TARGET MARKET, AVAILABLE RESOURCES]",
            values["full_context"],
        ),
        ("[DESCRIBE COMPANY, PRODUCT, INDUSTRY, STAGE]", values["full_context"]),
        ("[DESCRIBE PRODUCT]", values["product_description"]),
        # Short / specific placeholders
        ("[YOUR BUSINESS/ PROJECT]", values["business_name"]),
        ("[YOUR COMPANY/PRODUCT]", values["business_name"]),
        ("[YOUR PRODUCT/SERVICE]", values["product_description"]),
        ("[YOUR INDUSTRY/PRODUCT]", values["industry"]),
        ("[YOUR BUSINESS]", values["business_name"]),
        ("[YOUR PRODUCT]", values["product_description"]),
        ("[YOUR INDUSTRY]", values["industry"]),
        ("[TARGET MARKET/GEOGRAPHY/SEGMENT]", values["target_market"]),
        ("[TARGET CUSTOMER]", values["target_customer"]),
        ("[GEOGRAPHY]", values["geography"]),
        ("[INDUSTRY]", values["industry"]),
        ("[BUDGET]", values["budget"]),
    ]

    text = prompt["body"]
    for placeholder, replacement in replacements:
        text = text.replace(placeholder, replacement)

    return text

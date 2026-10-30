"""Deterministic, keyword-based SWOT and PESTLE suggestions (no AI service)."""

from __future__ import annotations

import re

CATEGORIES = (
    "Strengths",
    "Weaknesses",
    "Opportunities",
    "Threats",
    "Political",
    "Economic",
    "Social",
    "Technological",
    "Legal",
    "Environmental",
)

# Each cue maps to an illustrative prompt, not a factual claim about the user.
RULES: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {
    "Strengths": (
        (("experience", "experienced", "expert", "skilled"), "Relevant skills or experience may help the team deliver consistently."),
        (("quality", "reliable", "craft", "premium"), "A focus on quality or reliability could support customer trust."),
        (("brand", "reputation", "loyal", "community"), "An existing reputation or community may provide a foundation for growth."),
        (("innovative", "innovation", "unique", "patent"), "A distinctive offering or approach may help the project stand out."),
        (("efficient", "efficiently", "streamline", "low-cost"), "An efficient operating approach may help control delivery costs."),
    ),
    "Weaknesses": (
        (("limited", "small", "few", "early-stage", "startup"), "A small team or early stage may limit capacity and reach."),
        (("cost", "expensive", "budget", "funding"), "Cost or funding constraints could limit investment and flexibility."),
        (("depend", "rely", "single supplier", "one supplier"), "Reliance on a small number of suppliers or people may create a continuity risk."),
        (("lack", "inexperienced", "training", "gap"), "Skills, experience, or training gaps may need to be addressed."),
        (("awareness", "marketing", "visibility"), "Limited awareness or marketing reach could make customer acquisition harder."),
    ),
    "Opportunities": (
        (("demand", "growing", "growth", "popular"), "If demand continues to grow, the project could test a focused expansion."),
        (("online", "digital", "e-commerce", "website"), "Digital channels may create additional ways to reach and serve customers."),
        (("partner", "partnership", "collaborate", "supplier"), "Partnerships could extend capabilities or access to new audiences."),
        (("expand", "new market", "region", "international"), "A carefully tested new market or region may offer room to expand."),
        (("sustainable", "green", "recycle", "renewable"), "Interest in sustainable options may create opportunities for responsible differentiation."),
    ),
    "Threats": (
        (("competitor", "competition", "rival"), "Competitors may pressure pricing, customer loyalty, or market share."),
        (("regulation", "policy", "compliance", "law"), "Regulatory or policy changes could increase compliance work or costs."),
        (("inflation", "recession", "interest rate", "economic uncertainty"), "Economic uncertainty may affect costs and customer spending."),
        (("cyber", "security", "privacy", "data breach"), "Security or privacy incidents could disrupt operations and reduce trust."),
        (("shortage", "disruption", "supply chain", "delay"), "Supply or delivery disruptions could affect availability and service."),
    ),
    "Political": (
        (("government", "policy", "public sector", "election"), "Government priorities or policy changes could affect demand and operating conditions."),
        (("trade", "tariff", "import", "export"), "Trade rules, tariffs, or border processes could affect sourcing and costs."),
        (("permit", "license", "licence", "zoning"), "Permits, licensing, or local rules may influence where and how the project operates."),
        ((), "Review local government priorities, public funding, and policy stability relevant to this industry."),
    ),
    "Economic": (
        (("inflation", "price", "cost", "expensive"), "Inflation and input-price changes may affect margins and affordability."),
        (("recession", "income", "budget", "spending"), "Household or business spending conditions could shift customer demand."),
        (("interest", "loan", "credit", "funding"), "Interest rates and access to finance may affect investment and cash flow."),
        ((), "Track relevant economic indicators, including demand, wages, and input costs."),
    ),
    "Social": (
        (("community", "local", "culture", "inclusive"), "Community expectations and cultural context may shape customer acceptance."),
        (("aging", "ageing", "student", "family", "young"), "Changes in the needs or size of target demographic groups could affect demand."),
        (("health", "wellbeing", "well-being", "convenience"), "Lifestyle, health, and convenience preferences may influence adoption."),
        ((), "Validate customer needs, accessibility expectations, and changing social preferences."),
    ),
    "Technological": (
        (("digital", "online", "software", "app", "platform"), "Digital tools may improve reach or efficiency, while requiring ongoing maintenance."),
        (("data", "analytics", "automation", "ai"), "Data or automation could support better decisions, subject to quality and privacy safeguards."),
        (("cyber", "security", "privacy"), "Cybersecurity and privacy practices are important as technology use grows."),
        ((), "Monitor relevant technology changes and assess adoption, support, and security costs."),
    ),
    "Legal": (
        (("privacy", "data", "customer information"), "Privacy and data-protection obligations may apply to information handling."),
        (("employee", "staff", "workforce", "hire"), "Employment rules and workplace obligations should be checked as the team grows."),
        (("product", "safety", "food", "health"), "Product, consumer, or sector-specific safety requirements may apply."),
        ((), "Identify applicable contracts, consumer protection, intellectual property, and industry rules."),
    ),
    "Environmental": (
        (("energy", "electricity", "fuel", "transport"), "Energy use and transport impacts may affect both operating costs and emissions."),
        (("waste", "packaging", "plastic", "recycle"), "Waste and packaging choices may present compliance and improvement considerations."),
        (("water", "climate", "weather", "flood", "drought"), "Climate, weather, or water conditions may affect operations or supply continuity."),
        ((), "Review relevant resource use, environmental requirements, and opportunities to reduce impact."),
    ),
}


def _matches(text: str, cue: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(cue) + r"(?!\w)", text))


def _suggest(category: str, text: str, name: str, industry: str) -> list[str]:
    found = [
        suggestion
        for cues, suggestion in RULES[category]
        if cues and any(_matches(text, cue) for cue in cues)
    ]
    fallback = next((suggestion for cues, suggestion in RULES[category] if not cues), None)
    if category in ("Strengths", "Weaknesses", "Opportunities", "Threats") and not found:
        found.append(
            fallback
            or f"Review the current position of {name} in the {industry} industry for {category.lower()}."
        )
    elif category not in ("Strengths", "Weaknesses", "Opportunities", "Threats"):
        found.append(fallback)
    if len(found) < 3:
        context = f"for {industry} projects"
        found.append(
            f"Consider how {name} can respond to {category.lower()} factors "
            f"{context}, then validate this with current local evidence."
        )
    return found[:3]


def generate_analysis(name: str, industry: str, description: str) -> dict[str, list[str]]:
    """Create three explainable prompts per category from local keyword matches."""
    text = f"{name} {industry} {description}".lower()
    return {
        category: _suggest(category, text, name, industry)
        for category in CATEGORIES
    }

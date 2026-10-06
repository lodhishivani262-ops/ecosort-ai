"""EcoSort AI - Safety Guardrails & Hazardous Overrides (Stage 4).

Guarantees that safety-sensitive waste (batteries, chemicals, medical sharps,
aerosols, broken glass) overrides normal material recycling logic.
"""

from dataclasses import dataclass
from typing import List, Optional
from app.rules.categories import WasteCategory
from app.rules.material_rules import (
    BATTERY_KEYWORDS,
    E_WASTE_KEYWORDS,
    matches_keyword_group,
)
from app.schemas.classification import WastePerception


@dataclass
class SafetyAssessment:
    """Encapsulates a safety override decision."""
    category: WasteCategory
    warnings: List[str]
    preparation_steps: List[str]
    reason: str
    disposal_guidance: str


# Keyword indicators for safety-sensitive items
CHEMICAL_KEYWORDS = {
    "chemical", "pesticide", "insecticide", "fertilizer", "solvent",
    "paint", "acid", "bleach", "ammonia", "motor oil", "brake fluid",
    "flammable", "toxic", "poison", "corrosive", "cleaner bottle",
}

SHARPS_KEYWORDS = {
    "needle", "syringe", "sharp", "scalpel", "lancet", "razor blade",
}

MEDICINE_KEYWORDS = {
    "medicine", "pharmaceutical", "pill", "tablet", "capsule",
    "syrup bottle", "blister pack", "antibiotic", "prescription",
}

AEROSOL_KEYWORDS = {
    "aerosol", "spray can", "pressurized", "canister", "hairspray",
    "insect spray", "butane", "propane", "deodorant spray",
}

BROKEN_GLASS_KEYWORDS = {
    "broken glass", "shattered glass", "broken jar", "broken bottle",
    "shard", "sharp glass",
}


def evaluate_safety_override(perception: WastePerception) -> Optional[SafetyAssessment]:
    """Evaluates whether the item triggers an immediate safety override.

    Priority:
    Safety rules override standard material and contamination recycling rules.
    """
    item_lower = perception.item_name.lower()
    mat_lower = perception.material.lower()
    cond_lower = perception.condition.lower()
    combined_text = f"{item_lower} {mat_lower} {cond_lower}"

    # 1. Batteries (Fire and heavy metal risk)
    if perception.is_safety_sensitive and matches_keyword_group(combined_text, BATTERY_KEYWORDS) or matches_keyword_group(combined_text, BATTERY_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "CRITICAL FIRE HAZARD: Do NOT dispose of batteries in household trash or recycling bins.",
                "Compacting batteries in waste trucks can cause explosive thermal runaway fires.",
            ],
            preparation_steps=[
                "Tape the terminal ends (+ and -) with clear or electrical tape to prevent short circuits.",
                "Store in a cool, dry plastic container away from flammable items.",
                "Take to a designated battery drop-off kiosk, hardware store, or municipal collection depot.",
            ],
            reason="Item is a chemical battery cell containing toxic or flammable components.",
            disposal_guidance="Dispose only through authorized battery collection kiosks or hazardous waste drop-off events.",
        )

    # 2. Medical Sharps & Needles (Biohazard puncture risk)
    if matches_keyword_group(combined_text, SHARPS_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "BIOHAZARD INJURY RISK: Never place loose needles or sharps in household recycling or trash bins.",
            ],
            preparation_steps=[
                "Immediately place inside an FDA-cleared sharps container or rigid, puncture-resistant plastic container (e.g. heavy-duty detergent bottle).",
                "Seal the lid securely with duct tape.",
                "Label clearly: 'BIOHAZARD - MEDICAL SHARPS - DO NOT RECYCLE'.",
            ],
            reason="Medical sharp items pose severe puncture and biohazard infection risks to sanitation workers.",
            disposal_guidance="Deliver to a hospital, pharmacy drop box, or designated hazardous biohazard disposal facility.",
        )

    # 3. Hazardous Chemicals & Pesticides (Toxicity and contamination risk)
    if matches_keyword_group(combined_text, CHEMICAL_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "TOXIC SUBSTANCE: Do NOT pour leftover chemicals down drains, toilets, or onto the ground.",
                "Do NOT mix chemical containers with standard household recycling.",
            ],
            preparation_steps=[
                "Keep the substance in its original labeled container with the cap tightly closed.",
                "Do not rinse container if chemical residue could contaminate the sewer system.",
                "Transport upright in a secure cardboard box to prevent leaks.",
            ],
            reason="Chemical substances and toxic containers contaminate soil and water systems and require specialized treatment.",
            disposal_guidance="Take to a certified municipal Household Hazardous Waste (HHW) collection facility.",
        )

    # 4. Pressurized Aerosol Containers (Explosion risk)
    if matches_keyword_group(combined_text, AEROSOL_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "EXPLOSION & FIRE HAZARD: Pressurized cans can explode or ignite if punctured, crushed, or incinerated in standard waste machinery.",
            ],
            preparation_steps=[
                "Check that the canister is completely empty by discharging residual gas in a well-ventilated area.",
                "Do NOT puncture, crush, or expose to heat or open flames.",
                "Remove plastic spray cap if detachable.",
            ],
            reason="Pressurized canisters present high physical explosion risks when compacted.",
            disposal_guidance="If completely empty, follow local metal/aerosol guidance; if any contents remain, treat as hazardous waste.",
        )

    # 5. Broken Glass (Laceration injury risk)
    is_broken = any(k in cond_lower for k in ["broken", "shattered", "cracked", "sharp"])
    is_glass = matches_keyword_group(mat_lower, {"glass"}) or "glass" in item_lower
    if (is_glass and is_broken) or matches_keyword_group(combined_text, BROKEN_GLASS_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.GLASS,
            warnings=[
                "SAFETY WARNING: Broken glass causes lacerations. Protect sanitation workers by handling with extreme care.",
            ],
            preparation_steps=[
                "Wrap shards thoroughly in multiple layers of newspaper, heavy cardboard, or place in a rigid cardboard box.",
                "Tape the wrapping securely shut so no edges protrude.",
                "Label the package visibly: 'CAUTION: BROKEN GLASS'.",
            ],
            reason="Broken glass poses severe injury hazards during collection and handling.",
            disposal_guidance="Follow local regulations for secure broken glass drop-off or residual waste handling. Do not toss loose into recycling bins.",
        )

    # 6. Medicines / Pharmaceuticals (Water table contamination)
    if matches_keyword_group(combined_text, MEDICINE_KEYWORDS):
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "PHARMACEUTICAL HAZARD: Do NOT flush medications down the sink or toilet; wastewater plants cannot filter them out.",
            ],
            preparation_steps=[
                "Keep medication in its original blister pack or container.",
                "Black out personal prescription information on the label for privacy.",
                "Deposit at an official pharmacy take-back kiosk or national medicine return program.",
            ],
            reason="Pharmaceuticals disrupt aquatic ecosystems and contaminate public water supplies if improperly discarded.",
            disposal_guidance="Return unused or expired medications to a pharmacy take-back drop box.",
        )

    # 7. Generic safety sensitive flag fallback
    if perception.is_safety_sensitive:
        return SafetyAssessment(
            category=WasteCategory.HAZARDOUS,
            warnings=[
                "SAFETY SENSITIVE: This item presents potential handling hazards. Do not place in ordinary household recycling.",
            ],
            preparation_steps=[
                "Handle with protective gloves if appropriate.",
                "Store separately from combustible household materials.",
                "Contact your local municipal waste department for special collection protocols.",
            ],
            reason="Item was identified as potentially hazardous, volatile, or safety-sensitive.",
            disposal_guidance="Deposit through designated hazardous or special municipal collection programs.",
        )

    return None

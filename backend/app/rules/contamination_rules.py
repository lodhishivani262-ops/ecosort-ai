"""EcoSort AI - Contamination & Physical Condition Rules (Stage 4).

Handles the critical distinction between clean and soiled items,
specifically applying the porous vs non-porous degradation principle.
"""

from dataclasses import dataclass
from typing import List, Optional
from app.rules.categories import WasteCategory
from app.rules.material_rules import is_porous_material
from app.schemas.classification import ContaminationLevel, WastePerception


@dataclass
class ContaminationAssessment:
    """Encapsulates the condition and contamination evaluation."""
    category: WasteCategory
    preparation_steps: List[str]
    reason: str
    warnings: List[str]
    disposal_guidance: str


def evaluate_contamination_rules(
    perception: WastePerception,
    is_porous: bool,
    base_material_name: str,
) -> ContaminationAssessment:
    """Applies physical condition and contamination logic.

    Porous items (paper/cardboard):
      - High/Medium food grease contaminates recycling pulp permanently ->
        Downgrades to ORGANIC / WET WASTE (if compostable) or DRY WASTE.

    Non-porous items (rigid plastic, metal, glass):
      - Food contamination can be rinsed and remediated ->
        Remains RECYCLABLE with explicit cleaning instructions.
    """
    contam = perception.contamination
    cond_lower = perception.condition.lower()

    is_heavily_soiled = (
        contam == ContaminationLevel.HIGH
        or any(k in cond_lower for k in ["food-contaminated", "greasy", "oily", "soiled", "dirty"])
    )
    is_liquid_filled = any(k in cond_lower for k in ["liquid-filled", "full", "half-full", "unemptied"])
    is_wet = "wet" in cond_lower

    # --------------------------------------------------------------------------
    # 1. Porous Material (Paper & Cardboard)
    # --------------------------------------------------------------------------
    if is_porous:
        if is_heavily_soiled:
            return ContaminationAssessment(
                category=WasteCategory.ORGANIC,
                preparation_steps=[
                    "Scrape any solid food leftovers into the organic / wet waste bin.",
                    "Do NOT place greasy paper or cardboard into the paper recycling bin.",
                    "If home composting, tear soiled cardboard into small pieces.",
                ],
                reason=(
                    "Food grease and cooking oils permanently bind to paper fibers, making chemical "
                    "repulping impossible in standard mechanical recycling facilities."
                ),
                warnings=[
                    "Placing grease-soaked paper in recycling batches risks contaminating clean paper bales.",
                ],
                disposal_guidance="Place in organic/compost stream if compostable, or general residual dry waste.",
            )
        elif is_wet:
            return ContaminationAssessment(
                category=WasteCategory.DRY_WASTE,
                preparation_steps=[
                    "Allow to air-dry completely if you intend to recycle.",
                    "If mildew or mold has developed, dispose with general residual dry waste.",
                ],
                reason="Wet paper fibers break down prematurely and stick to recycling sorting machinery.",
                warnings=["Wet paper cannot be processed by standard paper recycling facilities."],
                disposal_guidance="Dispose in general residual waste unless completely dried out.",
            )
        elif contam == ContaminationLevel.UNKNOWN:
            return ContaminationAssessment(
                category=WasteCategory.RECYCLABLE,
                preparation_steps=[
                    "Inspect item for food oil, grease, or liquids.",
                    "If completely clean and dry, flatten to conserve volume.",
                    "If stained with food grease, segregate away from clean paper recycling.",
                ],
                reason="Clean paper and cardboard are highly recyclable; verify that no grease contamination exists.",
                warnings=["Condition could not be reliably verified from input. Confirm item is free of grease."],
                disposal_guidance="Place in clean paper recycling if free of food residues.",
            )
        else:
            # Clean dry paper/cardboard
            return ContaminationAssessment(
                category=WasteCategory.RECYCLABLE,
                preparation_steps=[
                    "Ensure paper/cardboard is clean and free of tape, plastic wrap, or staples where easily removable.",
                    "Flatten boxes to save bin capacity.",
                    "Keep dry until collection.",
                ],
                reason="Clean, dry paper and corrugated cardboard are widely accepted in mechanical recycling streams.",
                warnings=[],
                disposal_guidance="Place in the dry recycling stream.",
            )

    # --------------------------------------------------------------------------
    # 2. Non-Porous Material (Plastics, Metals, Glass)
    # --------------------------------------------------------------------------
    prep_steps: List[str] = []
    warnings: List[str] = []

    if is_liquid_filled:
        prep_steps.append("Empty all remaining liquid contents down the sink before disposal.")

    if is_heavily_soiled or contam in (ContaminationLevel.HIGH, ContaminationLevel.MEDIUM):
        prep_steps.extend([
            "Empty any remaining food residues.",
            "Rinse container with minimal water to remove food sauces and oils.",
            "Allow to air-dry before placing into the recycling bin.",
        ])
        reason = (
            f"Identified as {base_material_name} with food contamination. "
            "Rinsing and drying is required so residues do not attract pests or contaminate recycling streams."
        )
    elif contam == ContaminationLevel.UNKNOWN:
        prep_steps.extend([
            "Check that container is empty.",
            "Quick rinse if liquids or food were previously stored.",
            "Allow to dry.",
        ])
        warnings.append("Internal cleanliness could not be confirmed; please verify the container is empty and rinsed.")
        reason = f"Identified as {base_material_name}. Ensure container is clean and empty before recycling."
    else:
        prep_steps.extend([
            "Empty container completely.",
            "Keep clean and dry.",
            "Flatten plastic bottles or aluminum cans where applicable to save space.",
        ])
        reason = f"Clean {base_material_name} is recyclable-eligible in standard household recycling systems."

    return ContaminationAssessment(
        category=WasteCategory.RECYCLABLE,
        preparation_steps=prep_steps,
        reason=reason,
        warnings=warnings,
        disposal_guidance="Place in standard dry recycling stream after preparation.",
    )

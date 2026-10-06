"""EcoSort AI - Deterministic Waste Rule & Recommendation Engine (Stage 4).

Architectural Rule:
This engine is 100% deterministic, explainable, and testable.
It takes a WastePerception observation and applies a strict priority hierarchy
to produce actionable preparation steps, safety warnings, and waste categories.
It NEVER calls an LLM and NEVER randomly generates advice.
"""

from typing import List, Optional
from app.rules.categories import WasteCategory
from app.rules.contamination_rules import evaluate_contamination_rules
from app.rules.material_rules import (
    CONTAINER_TOKENS,
    COMPOSITE_DRY_KEYWORDS,
    E_WASTE_KEYWORDS,
    GLASS_KEYWORDS,
    METAL_KEYWORDS,
    ORGANIC_KEYWORDS,
    PAPER_KEYWORDS,
    PLASTIC_KEYWORDS,
    SANITARY_KEYWORDS,
    UNKNOWN_KEYWORDS,
    is_porous_material,
    matches_keyword_group,
)
from app.rules.safety_rules import evaluate_safety_override
from app.schemas.classification import (
    ConfidenceLevel,
    ContaminationLevel,
    WastePerception,
    WasteRecommendation,
)

STANDARD_MUNICIPAL_DISCLAIMER = (
    "Note: Municipal recycling rules and bin color schemes vary by region. "
    "Follow your local waste authority's guidelines."
)


class EcoSortRuleEngine:
    """Deterministic, explainable rule engine converting perception to disposal guidance."""

    @classmethod
    def evaluate(cls, perception: WastePerception) -> WasteRecommendation:
        """Evaluates waste perception attributes against the deterministic rule hierarchy.

        Priority Order:
        1. Safety Override (batteries, chemicals, medical sharps, aerosols, broken glass)
        2. Unknown / Insufficient Information (ambiguous object, low confidence unknown material)
        3. E-Waste (electronics, cables, chargers, appliances)
        4. Sanitary Waste (diapers, napkins, bandages, personal hygiene)
        5. Organic / Wet Waste (food scraps, fruit/vegetable peels, garden cuttings)
        6. Glass (intact jars, bottles)
        7. Material-based Dry / Recyclable Logic (paper, cardboard, plastics, metals)
        8. General Fallback (non-recyclable dry residual waste)
        """
        item_lower = perception.item_name.lower().strip()
        mat_lower = perception.material.lower().strip()
        combined = f"{item_lower} {mat_lower}"

        # ----------------------------------------------------------------------
        # Priority 1: Safety Override Engine
        # ----------------------------------------------------------------------
        safety_override = evaluate_safety_override(perception)
        if safety_override is not None:
            final_conf = perception.confidence
            warnings = list(safety_override.warnings)
            warnings.append(STANDARD_MUNICIPAL_DISCLAIMER)

            return WasteRecommendation(
                category=safety_override.category,
                preparation_steps=safety_override.preparation_steps,
                disposal_guidance=safety_override.disposal_guidance,
                warnings=warnings,
                confidence=final_conf,
                reason=safety_override.reason,
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 2: Unknown / Insufficient Information
        # ----------------------------------------------------------------------
        is_unknown_mat = not mat_lower or mat_lower in ("unknown", "none", "unidentified", "unclear") or matches_keyword_group(mat_lower, UNKNOWN_KEYWORDS)
        is_unknown_item = not item_lower or item_lower in ("unknown", "none", "unidentified", "item", "object", "scrap") or matches_keyword_group(item_lower, UNKNOWN_KEYWORDS)

        if (is_unknown_mat and is_unknown_item) or (is_unknown_mat and perception.confidence == ConfidenceLevel.LOW):
            return WasteRecommendation(
                category=WasteCategory.UNKNOWN,
                preparation_steps=[
                    "Check packaging for resin identification codes or recycling logos (e.g. Mobius loop with number).",
                    "If item composition remains unknown, do not mix with clean recycling to prevent contamination.",
                ],
                disposal_guidance="Unable to determine the correct disposal category reliably. Consult local waste guidance.",
                warnings=[
                    "Uncertain identification: To prevent recycling batch contamination, avoid placing unverified items into recycling bins.",
                    STANDARD_MUNICIPAL_DISCLAIMER,
                ],
                confidence=ConfidenceLevel.LOW,
                reason="The item's material composition could not be reliably determined from visual or textual inputs.",
                uncertainty_reason=perception.uncertainty_reason or "Material and item identity are ambiguous.",
            )

        # ----------------------------------------------------------------------
        # Priority 3: E-Waste
        # ----------------------------------------------------------------------
        if matches_keyword_group(combined, E_WASTE_KEYWORDS):
            prep_steps = [
                "Disconnect all power cables, adapters, and accessories.",
                "Remove any detachable batteries (deposit batteries separately in a dedicated battery kiosk).",
                "Wipe personal data if discarding storage media, computers, or smartphones.",
            ]
            return WasteRecommendation(
                category=WasteCategory.E_WASTE,
                preparation_steps=prep_steps,
                disposal_guidance="Deliver to an authorized electronic waste drop-off kiosk, electronics retailer take-back program, or municipal e-waste drive.",
                warnings=[
                    "Do NOT place electronic devices, e-waste, or cables in regular household recycling or trash bins.",
                    STANDARD_MUNICIPAL_DISCLAIMER,
                ],
                confidence=cls._calculate_confidence(perception),
                reason="Item is an electronic device containing integrated circuitry and specialized recyclable metals.",
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 4: Sanitary Waste
        # ----------------------------------------------------------------------
        if matches_keyword_group(combined, SANITARY_KEYWORDS):
            return WasteRecommendation(
                category=WasteCategory.SANITARY,
                preparation_steps=[
                    "Wrap securely in newspaper, toilet paper, or a dedicated disposal bag.",
                    "Seal securely to protect waste collectors from biological exposure.",
                ],
                disposal_guidance="Dispose in non-recyclable residual household waste for controlled incineration or landfill.",
                warnings=[
                    "Never flush sanitary products down toilets as they cause severe pipe blockages.",
                    "Sanitary waste is strictly non-recyclable.",
                    STANDARD_MUNICIPAL_DISCLAIMER,
                ],
                confidence=cls._calculate_confidence(perception),
                reason="Personal hygiene and sanitary items present biological contamination risks and must not be recycled.",
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 5: Organic / Wet Waste
        # ----------------------------------------------------------------------
        # Avoid treating food packaging/containers as organic food scraps
        is_container = matches_keyword_group(item_lower, CONTAINER_TOKENS)
        is_organic_material = matches_keyword_group(mat_lower, {"organic", "compostable", "biodegradable"})
        is_organic_matter = matches_keyword_group(combined, ORGANIC_KEYWORDS)

        if is_organic_material or (is_organic_matter and not is_container):
            return WasteRecommendation(
                category=WasteCategory.ORGANIC,
                preparation_steps=[
                    "Drain excess cooking liquids and gravy.",
                    "Remove any non-biodegradable stickers, rubber bands, plastic tags, or packaging.",
                ],
                disposal_guidance="Place in the green organic/wet waste bin or add to a home compost system.",
                warnings=[STANDARD_MUNICIPAL_DISCLAIMER],
                confidence=cls._calculate_confidence(perception),
                reason="Biodegradable organic matter can be naturally composted or processed into biogas.",
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 6: Glass (Intact)
        # ----------------------------------------------------------------------
        if matches_keyword_group(combined, GLASS_KEYWORDS):
            return WasteRecommendation(
                category=WasteCategory.GLASS,
                preparation_steps=[
                    "Empty any remaining contents and rinse with water.",
                    "Remove metal or plastic caps/corks (recycle caps separately with their respective materials).",
                    "Keep intact; avoid breaking glass in collection containers.",
                ],
                disposal_guidance="Place in dedicated glass bottle banks or municipal dry recyclables container.",
                warnings=[STANDARD_MUNICIPAL_DISCLAIMER],
                confidence=cls._calculate_confidence(perception),
                reason="Intact glass containers can be recycled indefinitely without loss of structural quality.",
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 6.5: Multi-layer Composite & Non-Recyclable Flexible Dry Packaging
        # ----------------------------------------------------------------------
        if matches_keyword_group(combined, COMPOSITE_DRY_KEYWORDS):
            return WasteRecommendation(
                category=WasteCategory.DRY_WASTE,
                preparation_steps=[
                    "Ensure completely empty of food crumbs and grease.",
                    "Keep dry and compress flat to conserve household bin space.",
                ],
                disposal_guidance="Dispose in non-recyclable residual dry waste unless your local region has a specialized flexible film drop-off program.",
                warnings=[
                    "Multi-layer metallized film composites cannot be separated mechanically in standard curbside recycling.",
                    STANDARD_MUNICIPAL_DISCLAIMER,
                ],
                confidence=cls._calculate_confidence(perception),
                reason=f"Multi-material composite packaging ('{perception.item_name}') cannot be mechanically recycled in standard municipal facilities.",
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 7: Material-based Dry / Recyclable Logic
        # ----------------------------------------------------------------------
        is_paper = matches_keyword_group(combined, PAPER_KEYWORDS)
        is_plastic = matches_keyword_group(combined, PLASTIC_KEYWORDS)
        is_metal = matches_keyword_group(combined, METAL_KEYWORDS)

        if is_paper or is_plastic or is_metal:
            porous = is_porous_material(perception.material, perception.item_name)
            base_mat = "paper / cardboard" if is_paper else ("plastic" if is_plastic else "metal")

            contam_eval = evaluate_contamination_rules(perception, is_porous=porous, base_material_name=base_mat)
            prep_steps = list(contam_eval.preparation_steps)
            warnings = list(contam_eval.warnings)

            # Check for multiple materials (e.g. plastic bottle + metal cap, or box with plastic window)
            clues_text = " ".join(perception.visual_clues).lower()
            if any(k in clues_text or k in combined for k in ["cap", "lid", "film", "window", "sleeve"]):
                prep_steps.append("Separate detachable components (e.g. caps, lids, plastic sleeves) if easily removable.")

            warnings.append(STANDARD_MUNICIPAL_DISCLAIMER)

            return WasteRecommendation(
                category=contam_eval.category,
                preparation_steps=prep_steps,
                disposal_guidance=contam_eval.disposal_guidance,
                warnings=warnings,
                confidence=cls._calculate_confidence(perception),
                reason=contam_eval.reason,
                uncertainty_reason=perception.uncertainty_reason,
            )

        # ----------------------------------------------------------------------
        # Priority 8: General Fallback (Non-Recyclable Dry Waste)
        # ----------------------------------------------------------------------
        return WasteRecommendation(
            category=WasteCategory.DRY_WASTE,
            preparation_steps=[
                "Keep dry.",
                "Compress or fold where possible to save waste bin space.",
            ],
            disposal_guidance="Dispose with general non-recyclable household dry waste.",
            warnings=[
                "Composite multi-materials and mixed textiles are generally not accepted in curbside mechanical recycling.",
                STANDARD_MUNICIPAL_DISCLAIMER,
            ],
            confidence=cls._calculate_confidence(perception),
            reason=f"Identified as '{perception.item_name}' ({perception.material}), which is typically classified as general dry residual waste.",
            uncertainty_reason=perception.uncertainty_reason,
        )

    @classmethod
    def _calculate_confidence(cls, perception: WastePerception) -> ConfidenceLevel:
        """Determines recommendation confidence conservatively.

        Rule Engine Confidence Policy:
        - NEVER elevates confidence beyond the perception layer.
        - Downgrades confidence if material is uncertain or contamination is unknown.
        """
        # If AI was already uncertain, recommendation must remain LOW
        if perception.confidence == ConfidenceLevel.LOW:
            return ConfidenceLevel.LOW

        # If contamination is completely unknown or material is ambiguous, downgrade HIGH -> MEDIUM
        if perception.contamination == ContaminationLevel.UNKNOWN:
            return ConfidenceLevel.MEDIUM

        mat_lower = perception.material.lower().strip()
        if not mat_lower or mat_lower in ("unknown", "none", "unidentified", "unclear") or matches_keyword_group(mat_lower, UNKNOWN_KEYWORDS):
            return ConfidenceLevel.MEDIUM

        return perception.confidence

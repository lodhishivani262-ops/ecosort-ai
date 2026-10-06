"""Extensive Unit Tests for the EcoSort Deterministic Rule Engine (Stage 4).

Verifies all 18+ mandated segregation scenarios, safety overrides,
contamination penalties, uncertainty handlings, and determinism.
"""

import copy
import pytest
from app.rules.categories import WasteCategory
from app.rules.rule_engine import EcoSortRuleEngine
from app.schemas.classification import (
    ConfidenceLevel,
    ContaminationLevel,
    WastePerception,
)


# ------------------------------------------------------------------------------
# Test 1: Clean plastic bottle
# ------------------------------------------------------------------------------
def test_clean_plastic_bottle():
    perception = WastePerception(
        item_name="plastic water bottle",
        material="plastic (PET-1)",
        condition="clean / empty",
        contamination=ContaminationLevel.NONE,
        visual_clues=["transparent body", "plastic cap"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    assert rec.confidence == ConfidenceLevel.HIGH
    assert any("empty" in s.lower() for s in rec.preparation_steps)
    assert "plastic" in rec.reason.lower()


# ------------------------------------------------------------------------------
# Test 2: Food-contaminated plastic container
# ------------------------------------------------------------------------------
def test_food_contaminated_plastic_container():
    perception = WastePerception(
        item_name="takeaway food container",
        material="polypropylene plastic (PP-5)",
        condition="food-contaminated",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["sauce stains on base"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    # Non-porous plastic can be recycled IF cleaned/rinsed
    assert any("rinse" in s.lower() for s in rec.preparation_steps)
    assert any("dry" in s.lower() for s in rec.preparation_steps)
    assert "food contamination" in rec.reason.lower()


# ------------------------------------------------------------------------------
# Test 3: Paper/cardboard - clean vs greasy (Porous degradation rule)
# ------------------------------------------------------------------------------
def test_clean_cardboard_box():
    perception = WastePerception(
        item_name="shipping box",
        material="corrugated cardboard",
        condition="clean / dry",
        contamination=ContaminationLevel.NONE,
        visual_clues=["brown cardboard", "folded flat"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    assert any("flatten" in s.lower() for s in rec.preparation_steps)


def test_greasy_pizza_box_porous_degradation():
    perception = WastePerception(
        item_name="pizza box",
        material="corrugated cardboard",
        condition="food-contaminated",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["heavy grease stains on bottom"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    # Porous cardboard with food grease CANNOT be recycled! Downgraded to ORGANIC/compost
    assert rec.category == WasteCategory.ORGANIC
    assert any("grease" in w.lower() or "contaminat" in w.lower() for w in rec.warnings)
    assert any("scrape" in s.lower() for s in rec.preparation_steps)
    assert "repulping" in rec.reason.lower() or "fibers" in rec.reason.lower()


# ------------------------------------------------------------------------------
# Test 4: Organic food waste
# ------------------------------------------------------------------------------
def test_organic_food_waste():
    perception = WastePerception(
        item_name="banana peel",
        material="organic matter",
        condition="fresh / decomposing",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["yellow fruit skin"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.ORGANIC
    assert "compost" in rec.disposal_guidance.lower() or "green" in rec.disposal_guidance.lower()


# ------------------------------------------------------------------------------
# Test 5: Intact glass bottle
# ------------------------------------------------------------------------------
def test_intact_glass_bottle():
    perception = WastePerception(
        item_name="olive oil glass jar",
        material="glass",
        condition="intact / empty",
        contamination=ContaminationLevel.LOW,
        visual_clues=["clear glass", "metal screw cap"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.GLASS
    assert any("rinse" in s.lower() for s in rec.preparation_steps)
    assert any("intact" in s.lower() for s in rec.preparation_steps)


# ------------------------------------------------------------------------------
# Test 6: Broken glass safety handling
# ------------------------------------------------------------------------------
def test_broken_glass_safety_override():
    perception = WastePerception(
        item_name="shattered glass tumbler",
        material="glass",
        condition="broken / shattered",
        contamination=ContaminationLevel.NONE,
        visual_clues=["sharp glass shards"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.GLASS
    # Must trigger safety laceration warning and wrapping steps
    assert any("wrap" in s.lower() for s in rec.preparation_steps)
    assert any("laceration" in w.lower() or "cuts" in w.lower() or "caution" in w.lower() for w in rec.warnings)


# ------------------------------------------------------------------------------
# Test 7: Metal item (aluminum can / tin)
# ------------------------------------------------------------------------------
def test_metal_aluminum_can():
    perception = WastePerception(
        item_name="soda can",
        material="aluminum",
        condition="empty / crushed",
        contamination=ContaminationLevel.NONE,
        visual_clues=["metallic cylinder", "pull tab intact"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    assert "aluminum" in rec.reason.lower() or "metal" in rec.reason.lower()


# ------------------------------------------------------------------------------
# Test 8: Battery (Safety Override)
# ------------------------------------------------------------------------------
def test_battery_safety_override():
    perception = WastePerception(
        item_name="lithium ion battery",
        material="lithium / metal",
        condition="used",
        contamination=ContaminationLevel.NONE,
        visual_clues=["cylindrical cell", "positive and negative terminals"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=True,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.HAZARDOUS
    assert any("fire" in w.lower() for w in rec.warnings)
    assert any("tape" in s.lower() for s in rec.preparation_steps)
    assert "kiosk" in rec.disposal_guidance.lower() or "hazardous" in rec.disposal_guidance.lower()


# ------------------------------------------------------------------------------
# Test 9: Electronic device (E-Waste)
# ------------------------------------------------------------------------------
def test_electronic_device():
    perception = WastePerception(
        item_name="broken computer keyboard",
        material="plastic and electronic circuitry",
        condition="broken",
        contamination=ContaminationLevel.NONE,
        visual_clues=["keys", "usb cable attached"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.E_WASTE
    assert any("data" in s.lower() or "cable" in s.lower() for s in rec.preparation_steps)
    assert any("e-waste" in w.lower() for w in rec.warnings)


# ------------------------------------------------------------------------------
# Test 10: Sanitary item
# ------------------------------------------------------------------------------
def test_sanitary_item():
    perception = WastePerception(
        item_name="disposable baby diaper",
        material="sanitary polymers and cellulose",
        condition="soiled",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["folded pad", "elastic cuffs"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.SANITARY
    assert any("wrap" in s.lower() for s in rec.preparation_steps)
    assert any("never flush" in w.lower() for w in rec.warnings)
    assert rec.category != WasteCategory.RECYCLABLE


# ------------------------------------------------------------------------------
# Test 11: Unknown material
# ------------------------------------------------------------------------------
def test_unknown_material():
    perception = WastePerception(
        item_name="unidentified scrap",
        material="unknown",
        condition="unknown",
        contamination=ContaminationLevel.UNKNOWN,
        visual_clues=[],
        confidence=ConfidenceLevel.LOW,
        uncertainty_reason="Image lacked lighting and material details.",
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.UNKNOWN
    assert rec.confidence == ConfidenceLevel.LOW
    assert "reliable" in rec.disposal_guidance.lower() or "consult" in rec.disposal_guidance.lower()


# ------------------------------------------------------------------------------
# Test 12: Low-confidence perception remains LOW
# ------------------------------------------------------------------------------
def test_low_confidence_perception_remains_low():
    perception = WastePerception(
        item_name="possible plastic bottle",
        material="plastic",
        condition="clean",
        contamination=ContaminationLevel.LOW,
        visual_clues=["blurry silhouette"],
        confidence=ConfidenceLevel.LOW,
        uncertainty_reason="Blurry camera snapshot.",
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    # The rule engine must never upgrade LOW confidence to HIGH
    assert rec.confidence == ConfidenceLevel.LOW


# ------------------------------------------------------------------------------
# Test 13: Unknown contamination handling
# ------------------------------------------------------------------------------
def test_unknown_contamination_handling():
    perception = WastePerception(
        item_name="metal soup can",
        material="steel tinplate",
        condition="used",
        contamination=ContaminationLevel.UNKNOWN,
        visual_clues=["cylindrical metal tin"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    # Downgrades confidence to MEDIUM due to unknown contamination
    assert rec.confidence == ConfidenceLevel.MEDIUM
    assert any("cleanliness" in w.lower() or "confirm" in w.lower() for w in rec.warnings)


# ------------------------------------------------------------------------------
# Test 14: Conflicting material/item signals (item=battery, material=plastic)
# ------------------------------------------------------------------------------
def test_conflicting_signals_safety_priority():
    perception = WastePerception(
        item_name="laptop battery pack",
        material="plastic casing",
        condition="used",
        contamination=ContaminationLevel.NONE,
        visual_clues=["black plastic casing with battery warning label"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=True,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    # Must prioritize battery safety override despite material being listed as "plastic"
    assert rec.category == WasteCategory.HAZARDOUS
    assert any("fire" in w.lower() for w in rec.warnings)


# ------------------------------------------------------------------------------
# Test 15: Multiple-material item (e.g. plastic bottle + metal cap)
# ------------------------------------------------------------------------------
def test_multiple_material_separation_step():
    perception = WastePerception(
        item_name="plastic drink bottle",
        material="plastic (PET)",
        condition="empty",
        contamination=ContaminationLevel.LOW,
        visual_clues=["plastic bottle body", "metal screw cap attached"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    assert any("separate" in s.lower() and ("cap" in s.lower() or "detachable" in s.lower()) for s in rec.preparation_steps)


# ------------------------------------------------------------------------------
# Test 16: Safety override (Pesticide / Toxic Chemical Container)
# ------------------------------------------------------------------------------
def test_chemical_container_safety_override():
    perception = WastePerception(
        item_name="lawn pesticide bottle",
        material="high-density polyethylene plastic (HDPE)",
        condition="unemptied / toxic",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["skull and crossbones poison symbol"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=True,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.HAZARDOUS
    assert any("toxic" in w.lower() or "drain" in w.lower() for w in rec.warnings)
    assert "hazardous waste" in rec.disposal_guidance.lower() or "hhw" in rec.disposal_guidance.lower()


# ------------------------------------------------------------------------------
# Test 17: Normal recyclable item (clean aluminum beverage can)
# ------------------------------------------------------------------------------
def test_normal_recyclable_item():
    perception = WastePerception(
        item_name="sparkling water can",
        material="aluminum",
        condition="clean / empty",
        contamination=ContaminationLevel.NONE,
        visual_clues=["aluminum beverage can"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.RECYCLABLE
    assert rec.confidence == ConfidenceLevel.HIGH
    assert rec.disposal_guidance != ""


# ------------------------------------------------------------------------------
# Test 18: Determinism verification (100 runs yield identical output)
# ------------------------------------------------------------------------------
def test_rule_engine_is_strictly_deterministic():
    perception = WastePerception(
        item_name="takeaway coffee cup",
        material="poly-coated paper",
        condition="wet / soiled",
        contamination=ContaminationLevel.MEDIUM,
        visual_clues=["paper cup with coffee dregs"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )

    baseline = EcoSortRuleEngine.evaluate(perception)

    for _ in range(100):
        iteration = EcoSortRuleEngine.evaluate(copy.deepcopy(perception))
        assert iteration.category == baseline.category
        assert iteration.preparation_steps == baseline.preparation_steps
        assert iteration.disposal_guidance == baseline.disposal_guidance
        assert iteration.warnings == baseline.warnings
        assert iteration.confidence == baseline.confidence
        assert iteration.reason == baseline.reason


# ------------------------------------------------------------------------------
# Test 19: Dry waste fallback for multi-layer composite wrapper
# ------------------------------------------------------------------------------
def test_dry_waste_composite_packaging():
    perception = WastePerception(
        item_name="potato chip bag",
        material="metallized plastic film composite",
        condition="empty / crinkled",
        contamination=ContaminationLevel.LOW,
        visual_clues=["shiny foil interior", "printed plastic exterior"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.DRY_WASTE
    assert "composite" in rec.reason.lower() or "dry" in rec.disposal_guidance.lower()


# ------------------------------------------------------------------------------
# Test 20: Aerosol spray can safety override
# ------------------------------------------------------------------------------
def test_pressurized_aerosol_safety_override():
    perception = WastePerception(
        item_name="hairspray aerosol canister",
        material="aluminum / pressurized propellant",
        condition="half-full / pressurized",
        contamination=ContaminationLevel.NONE,
        visual_clues=["nozzle", "flammable symbol"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=True,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    # Overrides aluminum recycling: must be HAZARDOUS / SPECIAL HANDLING
    assert rec.category == WasteCategory.HAZARDOUS
    assert any("puncture" in w.lower() or "flammable" in w.lower() or "fire" in w.lower() for w in rec.warnings)


# ------------------------------------------------------------------------------
# Test 21: Sanitary medical bandage
# ------------------------------------------------------------------------------
def test_sanitary_adhesive_bandage():
    perception = WastePerception(
        item_name="used adhesive medical bandage",
        material="fabric and adhesive polymer",
        condition="used / soiled",
        contamination=ContaminationLevel.HIGH,
        visual_clues=["bandage strip"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.SANITARY
    assert any("wrap" in s.lower() for s in rec.preparation_steps)
    assert rec.category != WasteCategory.RECYCLABLE


# ------------------------------------------------------------------------------
# Test 22: Unknown material with low confidence NEVER upgraded
# ------------------------------------------------------------------------------
def test_unknown_with_ambiguous_features_never_upgraded():
    perception = WastePerception(
        item_name="unidentified dark lump",
        material="unknown",
        condition="unknown",
        contamination=ContaminationLevel.UNKNOWN,
        visual_clues=[],
        confidence=ConfidenceLevel.LOW,
        uncertainty_reason="Insufficient lighting.",
        is_safety_sensitive=False,
    )
    rec = EcoSortRuleEngine.evaluate(perception)
    assert rec.category == WasteCategory.UNKNOWN
    assert rec.confidence == ConfidenceLevel.LOW


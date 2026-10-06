"""EcoSort AI - Centralized Material Mapping & Taxonomies (Stage 4)."""

from typing import Set

# Packaging container tokens to distinguish containers from contents (e.g. food container vs food scrap)
CONTAINER_TOKENS: Set[str] = {
    "container", "bottle", "box", "jar", "can", "tray", "tub",
    "wrapper", "packet", "pouch", "bag", "carton", "cup",
}

# Material classification keyword groups
PAPER_KEYWORDS: Set[str] = {
    "paper", "cardboard", "carton", "newspaper", "magazine", "box",
    "envelope", "corrugated", "flyer", "pamphlet", "notebook",
}

PLASTIC_KEYWORDS: Set[str] = {
    "plastic", "pet", "pet-1", "hdpe", "hdpe-2", "pvc", "pvc-3", "ldpe",
    "ldpe-4", "polypropylene", "pp", "pp-5", "polystyrene", "ps", "ps-6",
    "resin", "polymer",
}

METAL_KEYWORDS: Set[str] = {
    "metal", "aluminum", "aluminium", "steel", "tin", "iron", "copper",
    "brass", "can", "tinplate",
}

GLASS_KEYWORDS: Set[str] = {
    "glass", "silica", "mason jar", "bottle glass",
}

# Pure organic matter tokens (food scraps, peels, leftovers)
ORGANIC_KEYWORDS: Set[str] = {
    "organic", "food scrap", "food waste", "vegetable", "fruit", "peel",
    "leftover", "coffee ground", "tea bag", "eggshell", "bread", "leaf",
    "plant", "compostable", "decomposing", "flower", "garden", "meat scrap",
    "scrap", "bone",
}

E_WASTE_KEYWORDS: Set[str] = {
    "electronic", "electronics", "circuit", "phone", "smartphone", "laptop",
    "computer", "charger", "cable", "wire", "adapter", "appliance", "remote",
    "keyboard", "mouse", "monitor", "gadget", "printed circuit",
}

BATTERY_KEYWORDS: Set[str] = {
    "battery", "accumulator", "lithium", "alkaline", "nimh", "nicd", "lead-acid",
    "power bank", "coin cell", "button cell",
}

SANITARY_KEYWORDS: Set[str] = {
    "sanitary", "diaper", "pad", "napkin", "tampon", "bandage", "medical swab",
    "cotton bud", "hygiene wipe", "wet wipe", "surgical mask", "dental floss",
}

COMPOSITE_DRY_KEYWORDS: Set[str] = {
    "composite", "metallized", "foil pouch", "chip bag", "crisp packet",
    "snack wrapper", "snack pouch", "candy wrapper", "laminate film", "blister pack",
}

UNKNOWN_KEYWORDS: Set[str] = {
    "unknown", "unidentified", "unclear", "unclassified",
}


def matches_keyword_group(text: str, group: Set[str]) -> bool:
    """Checks if any non-empty keyword from the group exists as a substring or token."""
    if not text or not text.strip():
        return False
    lower_text = text.lower()
    for kw in group:
        if kw and kw in lower_text:
            return True
    return False


def is_porous_material(material: str, item_name: str = "") -> bool:
    """Returns True if the material absorbs moisture/grease (e.g. paper/cardboard).

    Crucial distinction: Porous materials cannot be cleaned after heavy food grease contamination
    and lose mechanical recyclability, whereas non-porous rigid plastics and metals can be rinsed.
    """
    combined = f"{material} {item_name}".lower()
    if matches_keyword_group(combined, PAPER_KEYWORDS):
        return True
    return False

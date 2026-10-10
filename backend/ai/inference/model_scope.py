"""
AniCare AI — Multi-Species Architecture & Clinical Model Scope Guard
Defines formal model deployment scopes across livestock and domestic animal species.
Guarantees that unvalidated species are never evaluated by an incompatible model.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class ModelScopeDefinition(BaseModel):
    species: List[str]
    conditions: List[str]
    status: str  # "validated" | "in_development" | "MODEL_NOT_VALIDATED_FOR_SPECIES"
    model_id: Optional[str] = None
    architecture: Optional[str] = None
    message: Optional[str] = None


class ModelScopeRegistry:
    """
    Maintains species-to-model routing table.
    Enforces that only species with validated datasets & benchmarked checkpoints
    execute deep vision inference.
    """

    # Currently validated production models
    ACTIVE_REGISTRY: Dict[str, Dict[str, Any]] = {
        "cattle": {
            "canonical_name": "Cattle",
            "aliases": ["cattle", "cow", "bovine", "bos taurus", "bos indicus"],
            "model_id": "anicare_vision_bovine_v1",
            "architecture": "EfficientNet-B0",
            "conditions": ["lumpy_skin_disease", "healthy_normal"],
            "status": "validated",
            "dataset_citation": "Mendeley Data DOI: 10.17632/w36hpf86j2.1 (CC BY 4.0)"
        }
    }

    # Species roadmap planned for future hackathon/national phases
    SPECIES_ROADMAP: Dict[str, Dict[str, Any]] = {
        "buffalo": {"canonical_name": "Buffalo", "status": "in_development", "target_disease": "FMD / Mastitis"},
        "goat": {"canonical_name": "Goat", "status": "in_development", "target_disease": "PPR / Goat Pox"},
        "sheep": {"canonical_name": "Sheep", "status": "in_development", "target_disease": "Sheep Pox"},
        "pig": {"canonical_name": "Pig", "status": "planned", "target_disease": "African Swine Fever"},
        "poultry": {"canonical_name": "Poultry", "status": "in_development", "target_disease": "Avian Pox / Coryza"},
        "dog": {"canonical_name": "Dog", "status": "planned", "target_disease": "Rabies / Canine Parvovirus"}
    }

    @classmethod
    def resolve_species_scope(cls, input_species: Optional[str]) -> Tuple[bool, ModelScopeDefinition]:
        """
        Validates whether a requested species has an active, benchmarked vision model.
        Returns (is_validated, ModelScopeDefinition).
        """
        norm_species = str(input_species or "Cattle").strip().lower()

        # Check validated models
        for scope_key, spec in cls.ACTIVE_REGISTRY.items():
            if norm_species in spec["aliases"] or any(a in norm_species for a in spec["aliases"]):
                return True, ModelScopeDefinition(
                    species=[spec["canonical_name"].lower()],
                    conditions=spec["conditions"],
                    status="validated",
                    model_id=spec["model_id"],
                    architecture=spec["architecture"],
                    message=f"Vision model operational for {spec['canonical_name']} cutaneous screening."
                )

        # Unsupported / unvalidated species
        return False, ModelScopeDefinition(
            species=[norm_species],
            conditions=[],
            status="MODEL_NOT_VALIDATED_FOR_SPECIES",
            model_id=None,
            architecture=None,
            message=(
                f"Vision model is validated exclusively for Cattle (Bovine). "
                f"Vision analysis is not validated for '{input_species}'. "
                "Routing safely to syndromic symptom evaluation and mandatory veterinary review."
            )
        )

    @classmethod
    def is_species_validated(cls, input_species: Optional[str]) -> bool:
        """Convenience method returning True if requested species has active validated model."""
        is_val, _ = cls.resolve_species_scope(input_species)
        return is_val

    @classmethod
    def create_species_guard_response(cls, input_species: Optional[str]) -> Dict[str, Any]:
        """Generates standard species guard payload for unvalidated species."""
        is_val, scope_def = cls.resolve_species_scope(input_species)
        return {
            "is_validated": is_val,
            "guard_code": scope_def.status,
            "species": scope_def.species,
            "syndromic_triage_only": not is_val,
            "message": scope_def.message
        }

    @classmethod
    def get_full_architecture_roadmap(cls) -> Dict[str, Any]:
        """Returns the full multi-species architectural registry for system discovery."""
        return {
            "validated_species": list(cls.ACTIVE_REGISTRY.keys()),
            "active_models": cls.ACTIVE_REGISTRY,
            "future_roadmap": cls.SPECIES_ROADMAP,
            "policy": (
                "AniCare AI adheres to veterinary evidence standards: image-based disease predictions "
                "are enabled ONLY for species backed by verified, peer-reviewed clinical benchmarks."
            )
        }


model_scope_registry = ModelScopeRegistry()

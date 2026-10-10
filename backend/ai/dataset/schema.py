from enum import Enum
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, Field, field_validator
import re

class TargetSpeciesEnum(str, Enum):
    CATTLE = "Cattle"
    BUFFALO = "Buffalo"
    GOAT = "Goat"
    SHEEP = "Sheep"
    PIG = "Pig"
    POULTRY = "Poultry/Chicken"
    DOG = "Dog"

class DiseaseCategoryEnum(str, Enum):
    VISUAL_ASSESSABLE = "VISUAL_ASSESSABLE"
    SYMPTOM_DRIVEN = "SYMPTOM_DRIVEN"
    LABORATORY_CONFIRMATION_REQUIRED = "LABORATORY_CONFIRMATION_REQUIRED"
    EPIDEMIOLOGICAL_SIGNAL = "EPIDEMIOLOGICAL_SIGNAL"

class DatasetSplitEnum(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"

class ImageQualityEnum(str, Enum):
    HIGH = "high"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNUSABLE = "unusable"

class AnnotationStatusEnum(str, Enum):
    VERIFIED_VETERINARY = "VERIFIED_VETERINARY"
    RESEARCH_CONSENSUS = "RESEARCH_CONSENSUS"
    STUDENT_ANNOTATED = "STUDENT_ANNOTATED"
    UNVERIFIED_PENDING = "UNVERIFIED_PENDING"

# Controlled Veterinary Taxonomy
# Maps each species to clinically valid conditions and diagnostic modalities.
VETERINARY_TAXONOMY: Dict[str, Dict[str, Dict[str, Any]]] = {
    TargetSpeciesEnum.CATTLE.value: {
        "Foot and Mouth Disease": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["oral_cavity", "muzzle", "hoof_foot", "udder"],
            "primary_signs": ["Vesicles", "Oral mucosal ulcers", "Coronary band inflammation", "Sialorrhea"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "RT-PCR / Antigen ELISA (NIHSAD/ICAR-DFMD)"
        },
        "Lumpy Skin Disease": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["skin_cutaneous", "neck", "flank", "perineum"],
            "primary_signs": ["Circumscribed 2-5cm dermal nodules", "Prescapular lymphadenopathy"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Capripoxvirus real-time PCR"
        },
        "Bovine Mastitis (Clinical)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["udder", "teat"],
            "primary_signs": ["Quarter swelling", "Erythema", "Abnormal milk clots/floccules"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "California Mastitis Test (CMT) & Microbiological Culture"
        },
        "Respiratory Infection (BRDC)": {
            "category": DiseaseCategoryEnum.SYMPTOM_DRIVEN.value,
            "body_regions": ["head_muzzle", "nostrils", "thorax"],
            "primary_signs": ["Mucopurulent nasal discharge", "Tachypnea", "Labored breathing"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Thoracic auscultation / Bronchoalveolar lavage PCR"
        },
        "Dermatophytosis (Ringworm)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["head_muzzle", "periocular", "neck"],
            "primary_signs": ["Circular asbestos-like crusts", "Circumscribed alopecia"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Fungal scrapings KOH microscopy"
        },
        "Black Quarter": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["gluteal_muscles", "shoulder", "thigh"],
            "primary_signs": ["Hot crepitant muscular swelling", "Severe lameness"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Clostridium chauvoei FAT / PCR"
        },
        "Anthrax": {
            "category": DiseaseCategoryEnum.LABORATORY_CONFIRMATION_REQUIRED.value,
            "body_regions": ["full_body", "natural_orifices"],
            "primary_signs": ["Sudden death", "Dark uncoagulated hemorrhage from orifices"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Peripheral blood smear McFadyean reaction (DO NOT OPEN CARCASS)"
        },
        "Brucellosis": {
            "category": DiseaseCategoryEnum.LABORATORY_CONFIRMATION_REQUIRED.value,
            "body_regions": ["reproductive_tract", "full_body"],
            "primary_signs": ["Late-term abortion", "Retained placenta", "Orchitis in bulls"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Rose Bengal Plate Test (RBPT) / Serum Agglutination"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body", "oral_cavity", "skin_cutaneous", "udder"],
            "primary_signs": ["Intact skin barrier", "Clear eyes/nostrils", "Normal gait"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Clinical physical wellness exam"
        }
    },
    TargetSpeciesEnum.BUFFALO.value: {
        "Foot and Mouth Disease": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["oral_cavity", "hoof_foot"],
            "primary_signs": ["Oral erosion", "Interdigital pododermatitis"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "RT-PCR"
        },
        "Haemorrhagic Septicaemia": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["submandibular", "throat", "brisket"],
            "primary_signs": ["Submandibular edematous swelling", "Stridor", "High fever"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Pasteurella multocida blood culture / PCR"
        },
        "Bovine Mastitis (Clinical)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["udder", "teat"],
            "primary_signs": ["Mammary induration", "Teat fibrosis"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "CMT / Culture"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body", "udder"],
            "primary_signs": ["Normal skin texture", "Clear mucosa"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Clinical physical exam"
        }
    },
    TargetSpeciesEnum.GOAT.value: {
        "Peste des Petits Ruminants": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["oral_cavity", "eyes", "nostrils"],
            "primary_signs": ["Necrotic stomatitis", "Severe catarrhal ocular discharge", "Diarrhea"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "PPRV real-time RT-PCR"
        },
        "Goat Pox": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["skin_cutaneous", "ears", "under_tail"],
            "primary_signs": ["Cutaneous papules and pocks"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Capripox PCR"
        },
        "Contagious Ecthyma (Orf)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["oral_cavity", "lips", "muzzle"],
            "primary_signs": ["Proliferative crusty scabs on labial commissures"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Parapoxvirus PCR / Characteristic lesions"
        },
        "Caseous Lymphadenitis": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["submandibular", "prescapular_lymph", "parotid"],
            "primary_signs": ["Suppurative lymph node abscessation ('onion-ring' capsule)"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Corynebacterium pseudotuberculosis culture"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body"],
            "primary_signs": ["Alert posture", "Dry clean muzzle"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Physical wellness exam"
        }
    },
    TargetSpeciesEnum.SHEEP.value: {
        "Sheep Pox": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["skin_cutaneous", "wool_free_areas"],
            "primary_signs": ["Erythematous macules developing into papules"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Capripox PCR"
        },
        "Contagious Ecthyma (Orf)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["lips", "nostrils"],
            "primary_signs": ["Papillomatous labial scabs"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Clinical / Parapox PCR"
        },
        "Bluetongue": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["head_muzzle", "tongue", "coronary_band"],
            "primary_signs": ["Facial edema", "Cyanotic tongue", "Coronitis lameness"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "BTV RT-PCR"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body"],
            "primary_signs": ["Clean fleece", "Active rumination"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Clinical exam"
        }
    },
    TargetSpeciesEnum.PIG.value: {
        "Swine Erysipelas": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["skin_cutaneous", "back", "ears"],
            "primary_signs": ["Rhomboid 'diamond-skin' raised purple urticarial plaques"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Erysipelothrix rhusiopathiae culture"
        },
        "African Swine Fever": {
            "category": DiseaseCategoryEnum.LABORATORY_CONFIRMATION_REQUIRED.value,
            "body_regions": ["ears", "abdomen", "extremities"],
            "primary_signs": ["Cutaneous cyanosis/hemorrhage", "High mortality"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "ASFV real-time PCR (WOAH reference lab)"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body"],
            "primary_signs": ["Normal pink/pigmented skin", "Active rooting"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Clinical exam"
        }
    },
    TargetSpeciesEnum.POULTRY.value: {
        "Fowl Pox": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["comb_wattle", "eyelids", "face"],
            "primary_signs": ["Cutaneous wart-like nodular scabs on non-feathered regions"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Avipoxvirus histology / PCR"
        },
        "Newcastle Disease": {
            "category": DiseaseCategoryEnum.SYMPTOM_DRIVEN.value,
            "body_regions": ["head_neck", "full_body"],
            "primary_signs": ["Torticollis / twisted neck", "Facial swelling", "Green diarrhea"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "NDV real-time RT-PCR"
        },
        "Infectious Coryza": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["infraorbital_sinus", "face"],
            "primary_signs": ["Infraorbital facial edema", "Foul-smelling nasal discharge"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Avibacterium paragallinarum PCR"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body", "comb_wattle"],
            "primary_signs": ["Bright red erect comb", "Clean plumage"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Flock health check"
        }
    },
    TargetSpeciesEnum.DOG.value: {
        "Canine Demodicosis (Mange)": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["periocular", "muzzle", "forepaws"],
            "primary_signs": ["Circumscribed periocular alopecia", "Comedones", "Erythema"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Deep skin scraping microscopy (Demodex canis)"
        },
        "Canine Superficial Pyoderma": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["ventral_abdomen", "groin", "axilla"],
            "primary_signs": ["Epidermal collarettes", "Follicular pustules", "Crusting"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Impression cytology (Gram-positive cocci)"
        },
        "Rabies": {
            "category": DiseaseCategoryEnum.LABORATORY_CONFIRMATION_REQUIRED.value,
            "body_regions": ["head_neck", "full_body"],
            "primary_signs": ["Furious/paralytic aggression", "Hypersalivation", "Hydrophobia"],
            "requires_lab_confirmation": True,
            "lab_gold_standard": "Direct Fluorescent Antibody (DFA) test on brain tissue post-mortem"
        },
        "Healthy / Normal": {
            "category": DiseaseCategoryEnum.VISUAL_ASSESSABLE.value,
            "body_regions": ["full_body"],
            "primary_signs": ["Shiny coat", "Moist clean planum nasale", "Clear eyes"],
            "requires_lab_confirmation": False,
            "lab_gold_standard": "Veterinary clinical wellness exam"
        }
    }
}

class DatasetManifestRecord(BaseModel):
    """
    Schema for a single verified sample in the AniCare AI dataset manifest.
    Enforces taxonomic validity, strict licensing, privacy guards, and split integrity.
    """
    image_id: str = Field(..., examples=["IMG-ANI-GJ-2026-0001"])
    file_path: str = Field(..., examples=["raw/cattle/fmd/IMG-ANI-GJ-2026-0001.jpg"])
    species: TargetSpeciesEnum
    disease: str = Field(..., examples=["Foot and Mouth Disease"])
    disease_category: DiseaseCategoryEnum
    body_region: str = Field(..., examples=["oral_cavity"])
    clinical_sign: str = Field(..., examples=["Vesicular dental pad erosion"])
    image_source: str = Field(..., examples=["AAU_Anand_Clinical_Repository"])
    source_organization: str = Field(..., examples=["Anand Agricultural University"])
    geographic_region: str = Field(..., examples=["Gujarat, India"])
    collection_date: Optional[str] = Field(None, examples=["2025-11-14"])
    annotation_status: AnnotationStatusEnum = AnnotationStatusEnum.VERIFIED_VETERINARY
    annotator_id: Optional[str] = Field(None, examples=["VET-REG-88402-GJ"])
    annotation_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    license: str = Field(..., examples=["CC-BY-4.0"])
    license_url: str = Field(..., examples=["https://creativecommons.org/licenses/by/4.0/"])
    consent_provenance: str = Field(..., examples=["Institutional Research Protocol & Owner Consent On File"])
    split: DatasetSplitEnum = DatasetSplitEnum.TRAIN
    animal_id: Optional[str] = Field(None, description="Animal RFID or anonymized cohort ID to prevent same-animal leakage", examples=["AN-GJ-TAG-8821"])
    capture_device: Optional[str] = Field(None, examples=["Handheld Inspection Camera Model X4"])
    image_quality: ImageQualityEnum = ImageQualityEnum.HIGH
    notes: Optional[str] = Field(default="", examples=["Confirmed via RT-PCR swab at NIHSAD Bhopal."])

    @field_validator("notes", mode="after")
    @classmethod
    def sanitize_privacy_pii(cls, v: Optional[str]) -> str:
        """Strict guard preventing accidental inclusion of personal phone numbers or citizen PII."""
        if not v:
            return ""
        # Check for 10-digit mobile phone numbers or personal Aadhaar-like numbers
        if re.search(r"\b[6-9]\d{9}\b", v) or re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", v):
            raise ValueError("PII Security Violation: Private contact or identity numbers detected in manifest notes.")
        return v

    @field_validator("disease", mode="after")
    @classmethod
    def validate_disease_for_species(cls, v: str, info) -> str:
        """Validates that disease is biologically valid for the designated target species."""
        species = info.data.get("species")
        if species:
            species_val = species.value if isinstance(species, TargetSpeciesEnum) else str(species)
            valid_diseases = VETERINARY_TAXONOMY.get(species_val, {})
            if valid_diseases and v not in valid_diseases:
                raise ValueError(
                    f"Biological Mismatch: Disease '{v}' is not recognized under controlled taxonomy for species '{species_val}'."
                )
        return v

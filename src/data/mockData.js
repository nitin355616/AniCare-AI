/**
 * AniCare AI — Realistic Demo Dataset
 * 
 * DISCLAIMER:
 * All data in this file is synthetic demo data tailored for the Smart India Hackathon (SIH 2026).
 * No live backend, database, or actual AI diagnostic inference is connected in this prototype.
 * AI confidence values, vitals, and diagnostic suggestions are simulated representations.
 */

export const DEMO_DISCLAIMER = {
  badge: "SIH 2026 PROTOTYPE - DEMO ENVIRONMENT",
  notice: "Simulated clinical & telemetry data. Real-world deployment requires ICAR-certified edge sensors and veterinary officer validation.",
  aiModelVersion: "AniCare-Net v1.2-beta (Quantized Vision-Transformer + BioClinical-BERT)"
};

export const CURRENT_USER = {
  name: "Dr. Arvind Verma",
  role: "Senior Veterinary Epidemiologist",
  department: "Department of Animal Husbandry & Dairying (DAHD)",
  center: "Amul Anand Surveillance Cluster #12, Gujarat",
  email: "arvind.verma@dahd.gov.in",
  avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
  id: "VET-ID-88402"
};

export const MOCK_SUMMARY_METRICS = {
  totalAnimals: 1420,
  healthyAnimals: 1318,
  atRisk: 83,
  critical: 19,
  activeAlerts: 9,
  herdHealthIndex: 92.4, // percentage
  herdHealthDelta: "+2.1% from last week",
  vaccinationCoverage: 95.8,
  averageTemp: 101.4, // Fahrenheit
  surveillanceSheds: 12,
  activeVetsOnDuty: 4,
  lastSync: "Just now (Live IoT Stream)"
};

export const MOCK_ANIMALS = [
  {
    id: "AN-GJ-2024-0104",
    tag: "TAG-8821",
    name: "Ganga",
    species: "Cattle",
    breed: "Gir (Indigenous Dairy)",
    gender: "Female",
    age: "4.2 years",
    weight: "440 kg",
    location: "Shed 04 - Milking Bay A",
    farmUnit: "Amul Co-op Farm #12, Anand, Gujarat",
    healthStatus: "Critical",
    riskScore: 92,
    lastCheck: "15 mins ago",
    temperature: "104.8 °F",
    heartRate: "88 bpm",
    respiratoryRate: "34 bpm",
    ruminationTime: "210 min/day",
    milkYield: "8.2 L/day (-35%)",
    appetite: "Anorexic (Refusing fodder)",
    activityLevel: "Recumbent / Reluctant to stand",
    breathingCondition: "Rapid / Dyspneic",
    lastVaccination: "FMD Booster - Oct 12, 2025",
    riskFactor: "High Risk (Suspected FMD / Vesicular Lesions)",
    registeredDate: "2023-04-10",
    avatar: "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80",
    symptoms: [
      "Excessive ropy salivation",
      "Vesicles and erosions on tongue and gums",
      "Coronary band inflammation",
      "Marked pyrexia (>104°F)"
    ],
    notes: "Exhibiting hypersalivation and severe lameness. Transferred to Isolation Pen 04. Quarantine protocol instituted.",
    healthTimeline: [
      { date: "Oct 06, 2026 - 08:30 AM", event: "Automated telemetry alert: Core body temperature spiked to 104.8°F.", severity: "Critical" },
      { date: "Oct 06, 2026 - 09:15 AM", event: "Physical examination by Dr. Rajesh Patel noted tongue ulcerations.", severity: "Critical" },
      { date: "Oct 04, 2026", event: "Milk parlor sensor noted sudden yield drop of 35%.", severity: "Warning" },
      { date: "Aug 15, 2026", event: "Routine bi-monthly health screening: Clean bill of health.", severity: "Normal" }
    ],
    treatments: [
      {
        medicine: "Flunixin Meglumine (Supportive Analgesic)",
        dosage: "2.2 mg/kg IV once daily",
        prescribedBy: "Dr. Rajesh Patel",
        date: "Oct 06, 2026",
        status: "Active",
        requiresVetApproval: true
      },
      {
        medicine: "Boric Acid & Glycerin Oral Swab",
        dosage: "Topical application 3x daily",
        prescribedBy: "Dr. Rajesh Patel",
        date: "Oct 06, 2026",
        status: "Active",
        requiresVetApproval: false
      }
    ],
    vaccinations: [
      { name: "Foot-and-Mouth Disease (FMD) Quadrivalent", date: "Oct 12, 2025", batch: "NADCP-FMD-992", status: "Valid" },
      { name: "Hemorrhagic Septicemia (HS) Alum Precipit.", date: "May 10, 2025", batch: "HS-2025-04", status: "Valid" },
      { name: "Brucellosis S19 Strain", date: "Jan 15, 2024", batch: "BR-CALF-11", status: "Lifelong" }
    ],
    aiHistory: [
      {
        date: "Oct 06, 2026",
        scanType: "Computer Vision + Ruminal Telemetry",
        predictedCondition: "Foot and Mouth Disease (FMD)",
        confidence: 94.6,
        risk: "HIGH",
        status: "Flagged for Isolation"
      }
    ]
  },
  {
    id: "AN-GJ-2024-0412",
    tag: "TAG-7719",
    name: "Nandi",
    species: "Cattle",
    breed: "Kankrej",
    gender: "Male (Bull)",
    age: "6.0 years",
    weight: "620 kg",
    location: "Shed 06 - Breeding Enclosure",
    farmUnit: "Amul Co-op Farm #12, Anand, Gujarat",
    healthStatus: "Critical",
    riskScore: 89,
    lastCheck: "45 mins ago",
    temperature: "105.1 °F",
    heartRate: "96 bpm",
    respiratoryRate: "38 bpm",
    ruminationTime: "180 min/day",
    milkYield: "N/A (Sire)",
    appetite: "Severely Reduced",
    activityLevel: "Lethargic / Dull",
    breathingCondition: "Labored / Tachypnea",
    lastVaccination: "Anthrax Spore - Feb 14, 2025",
    riskFactor: "Critical (Cutaneous Nodules / Suspected LSD)",
    registeredDate: "2021-09-03",
    avatar: "https://images.unsplash.com/photo-1500595046743-cd271d694d30?auto=format&fit=crop&w=400&q=80",
    symptoms: [
      "Circumscribed 2-5cm cutaneous nodules",
      "Prescapular lymph node enlargement",
      "Persistent pyrexia (>105°F)",
      "Edema of brisket and limbs"
    ],
    notes: "Widespread cutaneous nodules across neck, flanks, and perineum. Vector mosquito nets and deltamethrin sprays applied.",
    healthTimeline: [
      { date: "Oct 05, 2026", event: "Multiple circular dermal nodules observed during evening grooming.", severity: "Critical" },
      { date: "Oct 05, 2026", event: "Zonal viral surveillance team alerted under ICAR protocol.", severity: "Warning" }
    ],
    treatments: [
      {
        medicine: "Meloxicam + Paracetamol (Anti-inflammatory)",
        dosage: "0.5 mg/kg IM stat",
        prescribedBy: "Dr. Ananya Sharma",
        date: "Oct 05, 2026",
        status: "Active",
        requiresVetApproval: true
      },
      {
        medicine: "Enrofloxacin 10% (Secondary Bacterial Prophylaxis)",
        dosage: "5 mg/kg IM for 5 days",
        prescribedBy: "Dr. Ananya Sharma",
        date: "Oct 05, 2026",
        status: "Active",
        requiresVetApproval: true
      }
    ],
    vaccinations: [
      { name: "Lumpy Skin Disease (Goat Pox Strain)", date: "Nov 15, 2024", batch: "LSD-NDDB-01", status: "Booster Overdue" },
      { name: "Anthrax Spore Vaccine", date: "Feb 14, 2025", batch: "ANT-2025-B", status: "Valid" }
    ],
    aiHistory: [
      {
        date: "Oct 05, 2026",
        scanType: "Dermatological Image Feature Extraction",
        predictedCondition: "Lumpy Skin Disease (Capripox)",
        confidence: 91.2,
        risk: "HIGH",
        status: "Quarantined"
      }
    ]
  },
  {
    id: "AN-GJ-2024-0105",
    tag: "TAG-8822",
    name: "Shyamali",
    species: "Buffalo",
    breed: "Murrah",
    gender: "Female",
    age: "5.5 years",
    weight: "580 kg",
    location: "Shed 02 - Lactation Unit",
    farmUnit: "Amul Co-op Farm #12, Anand, Gujarat",
    healthStatus: "At Risk",
    riskScore: 68,
    lastCheck: "1 hour ago",
    temperature: "102.3 °F",
    heartRate: "72 bpm",
    respiratoryRate: "24 bpm",
    ruminationTime: "390 min/day",
    milkYield: "14.5 L/day (-12%)",
    appetite: "Normal Fodder Intake",
    activityLevel: "Normal",
    breathingCondition: "Normal",
    lastVaccination: "Brucellosis S19 - Jan 04, 2026",
    riskFactor: "Moderate Risk (Subclinical Mastitis Signs)",
    registeredDate: "2022-11-18",
    avatar: "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?auto=format&fit=crop&w=400&q=80",
    symptoms: [
      "Right hind udder quarter induration",
      "Milk electrical conductivity > 6.8 mS/cm",
      "Mild flakes in foremilk strip cup",
      "Yield drop in right rear quarter"
    ],
    notes: "Electrical conductivity of quarter milk increased by 18%. Somatic cell count CMT strip showed 2+ reaction.",
    healthTimeline: [
      { date: "Oct 04, 2026", event: "Automated parlor conductivity sensor flagged right hind quarter.", severity: "Warning" },
      { date: "Oct 04, 2026", event: "California Mastitis Test confirmed subclinical inflammation.", severity: "Warning" }
    ],
    treatments: [
      {
        medicine: "Cefquinome Intramammary Infusion",
        dosage: "1 syringe in affected quarter post-milking",
        prescribedBy: "Dr. Vikram Rao",
        date: "Oct 04, 2026",
        status: "Active",
        requiresVetApproval: true
      }
    ],
    vaccinations: [
      { name: "Brucellosis S19", date: "Jan 04, 2026", batch: "BR-2026-A", status: "Valid" },
      { name: "FMD Booster", date: "Oct 12, 2025", batch: "NADCP-FMD-992", status: "Valid" }
    ],
    aiHistory: [
      {
        date: "Oct 04, 2026",
        scanType: "Milk Conductivity Telemetry + CMT Matrix",
        predictedCondition: "Subclinical Bovine Mastitis",
        confidence: 88.5,
        risk: "MODERATE",
        status: "Under Treatment"
      }
    ]
  },
  {
    id: "AN-RJ-2024-0309",
    tag: "TAG-6119",
    name: "Badal",
    species: "Goat",
    breed: "Jamnapari",
    gender: "Male",
    age: "2.0 years",
    weight: "62 kg",
    location: "Pen 08 - Small Ruminants",
    farmUnit: "Bikaner Livestock Centre, Rajasthan",
    healthStatus: "At Risk",
    riskScore: 74,
    lastCheck: "2 hours ago",
    temperature: "103.9 °F",
    heartRate: "92 bpm",
    respiratoryRate: "32 bpm",
    ruminationTime: "310 min/day",
    milkYield: "N/A (Buck)",
    appetite: "Reduced by 30%",
    activityLevel: "Lethargic",
    breathingCondition: "Rapid / Nasal Rattling",
    lastVaccination: "PPR Homologous - Aug 10, 2025",
    riskFactor: "Elevated (Nasal Catarrh & Coughing)",
    registeredDate: "2024-01-20",
    avatar: "https://images.unsplash.com/photo-1524024973431-2ad916746881?auto=format&fit=crop&w=400&q=80",
    symptoms: [
      "Seromucous oculonasal discharge",
      "Mild erosive stomatitis inside lower lip",
      "Frequent coughing and sneezing",
      "Fever of 103.9°F"
    ],
    notes: "Nasal catarrh and coughing observed during morning inspection. Pen cohort isolated from main pasture.",
    healthTimeline: [
      { date: "Oct 06, 2026", event: "Discharge from eyes and nose reported by livestock attendant.", severity: "Warning" }
    ],
    treatments: [
      {
        medicine: "Oxytetracycline 20% LA (Broad spectrum)",
        dosage: "20 mg/kg deep IM",
        prescribedBy: "Dr. Meenakshi Sundaram",
        date: "Oct 06, 2026",
        status: "Active",
        requiresVetApproval: true
      }
    ],
    vaccinations: [
      { name: "Peste des Petits Ruminants (PPR) Vaccine", date: "Aug 10, 2025", batch: "PPR-IVRI-22", status: "Valid" }
    ],
    aiHistory: [
      {
        date: "Oct 06, 2026",
        scanType: "Respiratory & Facial Lesion AI Triage",
        predictedCondition: "Peste des Petits Ruminants (Suspected)",
        confidence: 87.0,
        risk: "HIGH",
        status: "Pending Confirmatory PCR"
      }
    ]
  },
  {
    id: "AN-PB-2024-0210",
    tag: "TAG-9014",
    name: "Rani",
    species: "Cattle",
    breed: "Sahiwal",
    gender: "Female",
    age: "3.1 years",
    weight: "410 kg",
    location: "Shed 01 - Prime Pasture",
    farmUnit: "Ludhiana Dairy Collective, Punjab",
    healthStatus: "Healthy",
    riskScore: 8,
    lastCheck: "3 hours ago",
    temperature: "101.2 °F",
    heartRate: "64 bpm",
    respiratoryRate: "20 bpm",
    ruminationTime: "480 min/day",
    milkYield: "16.8 L/day",
    appetite: "Optimal / High Ruminant Vigour",
    activityLevel: "Active & Alert",
    breathingCondition: "Normal",
    lastVaccination: "LSD Neethling Strain - Nov 20, 2025",
    riskFactor: "Nominal / Low Risk",
    registeredDate: "2023-08-15",
    avatar: "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?auto=format&fit=crop&w=400&q=80",
    symptoms: ["None - All physiological benchmarks optimal"],
    notes: "Body condition score 3.5/5. Excellent milk production and normal rumination curve.",
    healthTimeline: [
      { date: "Oct 01, 2026", event: "Bi-annual reproductive and milk quality check: All clear.", severity: "Normal" }
    ],
    treatments: [],
    vaccinations: [
      { name: "LSD Neethling Strain", date: "Nov 20, 2025", batch: "LSD-NDDB-08", status: "Valid" },
      { name: "FMD Booster", date: "Nov 05, 2025", batch: "NADCP-FMD-990", status: "Valid" }
    ],
    aiHistory: [
      {
        date: "Oct 01, 2026",
        scanType: "Routine Biometrics Audit",
        predictedCondition: "Healthy / Optimal Physiological Status",
        confidence: 98.4,
        risk: "LOW",
        status: "Cleared"
      }
    ]
  },
  {
    id: "AN-HR-2024-0518",
    tag: "TAG-4410",
    name: "Champa",
    species: "Buffalo",
    breed: "Nili-Ravi",
    gender: "Female",
    age: "4.8 years",
    weight: "540 kg",
    location: "Shed 03 - Lactation Unit B",
    farmUnit: "NDRI Research Herd, Karnal, Haryana",
    healthStatus: "Healthy",
    riskScore: 12,
    lastCheck: "4 hours ago",
    temperature: "101.5 °F",
    heartRate: "66 bpm",
    respiratoryRate: "22 bpm",
    ruminationTime: "460 min/day",
    milkYield: "13.2 L/day",
    appetite: "Normal",
    activityLevel: "Normal",
    breathingCondition: "Normal",
    lastVaccination: "HS & BQ Combined - May 15, 2025",
    riskFactor: "Nominal / Low Risk",
    registeredDate: "2022-07-29",
    avatar: "https://images.unsplash.com/photo-1596733430284-f7437764b14d?auto=format&fit=crop&w=400&q=80",
    symptoms: ["None detected"],
    notes: "Normal feeding index, heat detection tracker shows day 14 of estrous cycle.",
    healthTimeline: [
      { date: "May 15, 2025", event: "Pre-monsoon combined HS & BQ vaccination administered.", severity: "Normal" }
    ],
    treatments: [],
    vaccinations: [
      { name: "HS & BQ Combined Vaccine", date: "May 15, 2025", batch: "HSBQ-2025-09", status: "Valid" }
    ],
    aiHistory: []
  },
  {
    id: "AN-TN-2024-0622",
    tag: "TAG-3190",
    name: "Selvi",
    species: "Sheep",
    breed: "Mecheri",
    gender: "Female",
    age: "1.8 years",
    weight: "38 kg",
    location: "Range Area 02",
    farmUnit: "Salem District Pastoral Cooperative, Tamil Nadu",
    healthStatus: "Recovering",
    riskScore: 24,
    lastCheck: "5 hours ago",
    temperature: "102.0 °F",
    heartRate: "80 bpm",
    respiratoryRate: "24 bpm",
    ruminationTime: "420 min/day",
    milkYield: "1.1 L/day",
    appetite: "Normal",
    activityLevel: "Alert and Grazing",
    breathingCondition: "Normal",
    lastVaccination: "Enterotoxaemia - Dec 01, 2025",
    riskFactor: "Low (Post-Deworming Recovery)",
    registeredDate: "2024-02-11",
    avatar: "https://images.unsplash.com/photo-1484557052118-f32bd25b45b5?auto=format&fit=crop&w=400&q=80",
    symptoms: ["Resolving anemia, mucous membranes turning pink"],
    notes: "Fecal egg count reduced by 92% post anthelmintic therapy. Re-entry to main flock scheduled in 48h.",
    healthTimeline: [
      { date: "Sep 28, 2026", event: "Administered Albendazole 10% suspension for gastrointestinal helminthiasis.", severity: "Normal" }
    ],
    treatments: [
      {
        medicine: "Iron Dextran + Vitamin B12 Injection",
        dosage: "2 mL IM single dose",
        prescribedBy: "Dr. Meenakshi Sundaram",
        date: "Sep 28, 2026",
        status: "Completed",
        requiresVetApproval: true
      }
    ],
    vaccinations: [
      { name: "Enterotoxaemia Pulpy Kidney Vaccine", date: "Dec 01, 2025", batch: "ET-2025-12", status: "Valid" }
    ],
    aiHistory: []
  },
  {
    id: "AN-MH-2024-0731",
    tag: "TAG-9920",
    name: "Surya",
    species: "Cattle",
    breed: "Deoni",
    gender: "Male",
    age: "3.5 years",
    weight: "480 kg",
    location: "Shed 05 - Open Yard",
    farmUnit: "Marathwada Agro-Vet Center, Latur, Maharashtra",
    healthStatus: "Healthy",
    riskScore: 6,
    lastCheck: "6 hours ago",
    temperature: "101.4 °F",
    heartRate: "68 bpm",
    respiratoryRate: "21 bpm",
    ruminationTime: "475 min/day",
    milkYield: "N/A (Draft)",
    appetite: "Optimal",
    activityLevel: "Strong, Alert",
    breathingCondition: "Normal",
    lastVaccination: "FMD Booster - Nov 05, 2025",
    riskFactor: "Nominal / Low Risk",
    registeredDate: "2023-12-04",
    avatar: "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80",
    symptoms: ["None"],
    notes: "Excellent muscle tone, zero lameness indicators detected on automated gait pressure sensors.",
    healthTimeline: [],
    treatments: [],
    vaccinations: [
      { name: "FMD Booster", date: "Nov 05, 2025", batch: "NADCP-FMD-990", status: "Valid" }
    ],
    aiHistory: []
  }
];

export const MOCK_DISEASE_PRESETS = [
  {
    id: "preset-respiratory",
    name: "Bovine Respiratory Disease (BRD) Complex",
    conditionLabel: "Respiratory Infection",
    species: "Cattle / Bovine",
    typicalSymptoms: [
      "Rapid, shallow dyspneic breathing",
      "Serous to mucopurulent nasal discharge",
      "Spontaneous or induced coughing",
      "Elevated core temperature (>104°F)",
      "Depressed appetite and droopy ears"
    ],
    sampleConfidence: 87.0,
    riskLevel: "HIGH",
    pathogen: "Pasteurella multocida / Mannheimia haemolytica",
    severity: "High Risk",
    contagious: true,
    quarantineRequired: true,
    detectedSymptoms: [
      "Labored abdominal respiration",
      "Mucopurulent bilateral nasal discharge",
      "Fever spike of 104.4°F",
      "Audible tracheal rales on auscultation"
    ],
    riskExplanation:
      "Rapid progression potential to fibrinous pleuropneumonia. Early telemetry flags severe oxygenation deficit and significant risk of cohort transmission in crowded indoor sheds.",
    recommendedActions: [
      "Immediately isolate affected animal in a well-ventilated, dry sick pen.",
      "Conduct physical thoracic auscultation and pulse oximetry within 2 hours.",
      "Isolate surrounding cohort calves sharing the water trough.",
      "Provide fresh warm water and easily digestible leafy green fodder."
    ],
    vetConsultationRecommendation:
      "Mandatory urgent veterinary review within 6 hours. Antimicrobial therapy (Florfenicol or Tulathromycin) must only be initiated following a certified veterinary prescription.",
    preventiveActions: [
      "Improve air exchange rate in Shed 04 to reduce aerosol bacterial density.",
      "Administer multivalent intranasal BRD vaccine to cohorts under 12 months.",
      "Disinfect water troughs with 1:1000 potassium permanganate solution.",
      "Minimize herd transport stress and dusty feeding environments."
    ],
    differentialDiagnoses: [
      { disease: "Bovine Respiratory Disease Complex", probability: 87.0, rationale: "Syndromic triad of tachypnea, fever, and purulent nasal catarrh." },
      { disease: "Infectious Bovine Rhinotracheitis (IBR)", probability: 8.8, rationale: "Lower necrotic plaque density observed on nasal septal mucosa." },
      { disease: "Aspiration Pneumonia", probability: 4.2, rationale: "No recent history of forced drenching or esophageal tubing." }
    ]
  },
  {
    id: "preset-fmd",
    name: "Foot and Mouth Disease (FMD) Screening",
    conditionLabel: "Foot and Mouth Disease (Suspected)",
    species: "Cattle / Buffalo / Small Ruminants",
    typicalSymptoms: [
      "Excessive ropy salivation",
      "Vesicular lesions on tongue & gums",
      "Lameness / coronary band sores",
      "High fever (>104°F)"
    ],
    sampleConfidence: 94.6,
    riskLevel: "CRITICAL",
    pathogen: "Aphthovirus (Picornaviridae)",
    severity: "Critical / Epizootic",
    contagious: true,
    quarantineRequired: true,
    detectedSymptoms: [
      "Characteristic ropy saliva drooling",
      "Ruptured vesicles on dental pad and tongue",
      "Tender coronary band erythema with painful gait",
      "High pyrexia (104.8°F)"
    ],
    riskExplanation:
      "Highly infectious OIE-listed epizootic viral contagion. Can rapidly spread airborne across a 10km radius if strict containment is breached.",
    recommendedActions: [
      "Immediate bio-secure quarantine in isolation pen (minimum 100m standoff).",
      "Notify District Animal Husbandry Officer (DAHO) under Infectious Diseases Act.",
      "Collect sterile vesicular fluid swab for RT-PCR confirmation at NIHSAD.",
      "Apply 4% sodium carbonate or 2% citric acid footbaths at all entry points."
    ],
    vetConsultationRecommendation:
      "Emergency statutory veterinary alert. Mandatory on-site official inspection within 2 hours. Strict movement freeze across the village boundary.",
    preventiveActions: [
      "Emergency ring vaccination of all susceptible cloven-hoofed stock within 5km radius.",
      "Suspend milk tanker dispatches from affected shed until sanitized.",
      "Incinerate or deeply bury contaminated bedding with quicklime.",
      "Restricted personnel access with mandatory boots change."
    ],
    differentialDiagnoses: [
      { disease: "Foot and Mouth Disease", probability: 94.6, rationale: "Vesicular stomatitis and pododermatitis match clinical presentation." },
      { disease: "Vesicular Stomatitis", probability: 4.1, rationale: "Similar mucosal erosion patterns but lower prevalence in this agro-zone." },
      { disease: "Bovine Viral Diarrhea (Mucosal)", probability: 1.3, rationale: "Absence of persistent leukopenia or gastrointestinal hemorrhage." }
    ]
  },
  {
    id: "preset-lsd",
    name: "Lumpy Skin Disease (LSD) Evaluation",
    conditionLabel: "Lumpy Skin Disease (Capripox)",
    species: "Cattle (Bovine)",
    typicalSymptoms: [
      "Firm circumscribed skin nodules (2-5cm)",
      "Enlarged superficial lymph nodes",
      "Persistent pyrexia (>104°F)",
      "Edema of limbs and dewlap"
    ],
    sampleConfidence: 91.2,
    riskLevel: "HIGH",
    pathogen: "Capripoxvirus (Poxviridae)",
    severity: "High Risk",
    contagious: true,
    quarantineRequired: true,
    detectedSymptoms: [
      "Distinct round dermal nodules across head, neck, and udder",
      "Prescapular lymphadenopathy marked bilaterally",
      "Core temperature 105.1°F",
      "Watery oculonasal discharge"
    ],
    riskExplanation:
      "Vector-borne capripox viral outbreak. Transmission mediated by stable flies (Stomoxys) and mosquitoes. Causes severe milk loss, skin damage, and emaciation.",
    recommendedActions: [
      "Isolate animal under fine insect-proof netting.",
      "Deploy vector control thermal fogging (deltamethrin / pyrethroids).",
      "Apply topical antiseptic sprays (zinc oxide / neem oil) on open nodules.",
      "Daily photographic tracking of nodule rupture and necrosis."
    ],
    vetConsultationRecommendation:
      "Veterinary officer assessment required for supportive anti-inflammatory and antibiotic coverage against secondary bacterial dermatomyositis.",
    preventiveActions: [
      "Ring vaccination with homologous Goat Pox vaccine (10x cattle dose) in 5km buffer.",
      "Eliminate standing water breeding pools around dairy sheds.",
      "Prohibit entry of external draft animals or cattle trading.",
      "Daily temperature logging of cohort livestock."
    ],
    differentialDiagnoses: [
      { disease: "Lumpy Skin Disease", probability: 91.2, rationale: "Nodular intradermal eruptions across neck and perineum align with acute capripox." },
      { disease: "Pseudo-Lumpy Skin (BHV-2)", probability: 6.7, rationale: "Lesions are deep-seated rather than superficial epidermal crusts." },
      { disease: "Demodectic Mange", probability: 2.1, rationale: "Sudden fever spikes distinguish viral etiology from parasitic follicular mite infestation." }
    ]
  },
  {
    id: "preset-mastitis",
    name: "Early Bovine Mastitis Triage",
    conditionLabel: "Subclinical / Acute Mastitis",
    species: "Cattle / Buffalo",
    typicalSymptoms: [
      "Swelling / heat in udder quarter",
      "Floccules or watery milk",
      "Yield decline >20%",
      "Elevated electrical conductivity"
    ],
    sampleConfidence: 88.5,
    riskLevel: "MODERATE",
    pathogen: "Staphylococcus aureus / Streptococcus uberis",
    severity: "Moderate Risk",
    contagious: false,
    quarantineRequired: false,
    detectedSymptoms: [
      "Firm, warm swelling in right hind quarter",
      "Quarter milk electrical conductivity 6.8 mS/cm",
      "CMT reagent score 2+ (coagulated gel)",
      "Daily yield drop of 18%"
    ],
    riskExplanation:
      "Intramammary bacterial invasion causing ductal occlusion and cellular inflammation. If unaddressed within 24h, risk of permanent quarter atrophy and fibrosis.",
    recommendedActions: [
      "Milk out affected quarter completely into a separate discard pail.",
      "Apply cold water hose hydrotherapy followed by gentle udder massage.",
      "Collect sterile milk vial for microbiological culture and AST.",
      "Dip teats in 0.5% active iodine barrier dip."
    ],
    vetConsultationRecommendation:
      "Veterinary consultation advised for AST-directed intramammary antibiotic infusion. Do not administer over-the-counter infusions without sterility.",
    preventiveActions: [
      "Inspect milking machine claw vacuum levels and liner elasticity.",
      "Ensure clean, dry bedding with daily lime powder dusting in stalls.",
      "Keep cows standing for 30 minutes post-milking by providing fresh fodder.",
      "Regular weekly screening with in-line CMT strips."
    ],
    differentialDiagnoses: [
      { disease: "Subclinical / Clinical Mastitis", probability: 88.5, rationale: "Localized teat induration and conductivity telemetry spikes (>6.5 mS/cm)." },
      { disease: "Udder Edema (Physiological)", probability: 8.9, rationale: "Lactation stage does not coincide with immediate periparturient onset." },
      { disease: "Traumatic Thelitis", probability: 2.6, rationale: "No mechanical lacerations observed on teat sphincter surface." }
    ]
  }
];

export const MOCK_ALERTS = [
  {
    id: "ALT-2026-901",
    timestamp: "10 mins ago",
    severity: "Critical",
    alertType: "Critical Alert",
    category: "Epizootic Early-Warning",
    title: "Clustered LSD Outbreak Warning in Sector 04",
    location: "Anand District, Radius 12km (Surrounding Amul Zone B)",
    description: "ANI-NET spatial anomaly detected 7 high-probability Lumpy Skin cases within a 48h temporal window across 3 neighbouring dairy sheds.",
    affectedTag: "TAG-7719 + 6 Cohorts",
    status: "Active",
    actionRequired: "Enact Ring Quarantine & Vector Fumigation",
    dispatchStatus: "Vet Team Dispatched",
    badgeColor: "rose"
  },
  {
    id: "ALT-2026-902",
    timestamp: "32 mins ago",
    severity: "Critical",
    alertType: "Critical Alert",
    category: "Telemetry Anomaly",
    title: "Acute Hyperthermia Spike in Gir Cattle #8821",
    location: "Shed 04 - Milking Bay A",
    description: "Continuous ruminal bolus telemetry logged core temperature rise to 104.8°F accompanied by 42% decrease in rumination time.",
    affectedTag: "TAG-8821 (Ganga)",
    status: "Active",
    actionRequired: "Clinical Examination & Fluid Therapy",
    dispatchStatus: "Pending On-Site Vet Review",
    badgeColor: "rose"
  },
  {
    id: "ALT-2026-903",
    timestamp: "1 hour ago",
    severity: "High",
    alertType: "Disease-Risk Alert",
    category: "Syndromic Signal",
    title: "Bovine Respiratory Infection Cluster in Pen 08",
    location: "Pen 08 - Small Ruminants Enclosure",
    description: "AI audio cough detector and thermal sensor logged 4 animals with tachypnea and abnormal coughing frequency.",
    affectedTag: "TAG-6119 + 3 Cohorts",
    status: "Active",
    actionRequired: "Auscultation & Cohort Isolation",
    dispatchStatus: "Assigned to Dr. Meenakshi",
    badgeColor: "rose"
  },
  {
    id: "ALT-2026-904",
    timestamp: "2 hours ago",
    severity: "Medium",
    alertType: "Disease-Risk Alert",
    category: "Syndromic Signal",
    title: "Milk Yield Depression & Conductivity Rise in Buffalo #8822",
    location: "Shed 02 - Lactation Unit",
    description: "Early subclinical mastitis signature detected on automated in-line parlor sensors. Somatic cell count threshold breached.",
    affectedTag: "TAG-8822 (Shyamali)",
    status: "Investigating",
    actionRequired: "California Mastitis Test (CMT) Sampling",
    dispatchStatus: "Technician Assigned",
    badgeColor: "amber"
  },
  {
    id: "ALT-2026-905",
    timestamp: "3 hours ago",
    severity: "Medium",
    alertType: "Follow-up Reminder",
    category: "Clinical Care",
    title: "Follow-up Auscultation Due for Calf #2104",
    location: "Shed 04 - Recovery Bay",
    description: "Scheduled 48-hour post-treatment evaluation for acute bronchopneumonia recovery monitoring.",
    affectedTag: "TAG-2104 (Suraj)",
    status: "Scheduled",
    actionRequired: "Verify Lung Sound Clearance & Temperature",
    dispatchStatus: "Scheduled at 11:30 AM",
    badgeColor: "amber"
  },
  {
    id: "ALT-2026-906",
    timestamp: "5 hours ago",
    severity: "Medium",
    alertType: "Vaccination Reminder",
    category: "Preventive Care",
    title: "Brucellosis Booster Due for 42 Heifers",
    location: "Shed 01 & Shed 03",
    description: "Vaccination window expires in 72 hours under National Animal Disease Control Programme (NADCP) guidelines.",
    affectedTag: "Batch #BR-2026-Q1",
    status: "Scheduled",
    actionRequired: "Confirm Cold-Chain Vaccine Stock & Syringes",
    dispatchStatus: "Stock Reserved in Cold Vault #3",
    badgeColor: "amber"
  },
  {
    id: "ALT-2026-907",
    timestamp: "8 hours ago",
    severity: "Low",
    alertType: "Vaccination Reminder",
    category: "NADCP Program",
    title: "PPR Booster Notification for Salem Pastoral Sheep",
    location: "Salem Pastoral Co-op, Tamil Nadu",
    description: "Phase 2 ring vaccination window opens next Monday for 180 registered ewes.",
    affectedTag: "Flock #SL-2024",
    status: "Scheduled",
    actionRequired: "Coordinate Cold Boxes with District Center",
    dispatchStatus: "Notification Logged",
    badgeColor: "sky"
  },
  {
    id: "ALT-2026-908",
    timestamp: "Yesterday",
    severity: "Low",
    alertType: "Preventive Alert",
    category: "Biosecurity",
    title: "Automated Disinfection Footbath Refill Complete",
    location: "Perimeter Gate 1, 2, & Main Milking Parlor",
    description: "Sensor indicates sodium carbonate concentration stabilized at 3.98% at vehicle and personnel entryways.",
    affectedTag: "Bio-Station A-1",
    status: "Resolved",
    actionRequired: "Routine Weekly Sensor Calibration",
    dispatchStatus: "Completed",
    badgeColor: "slate"
  },
  {
    id: "ALT-2026-909",
    timestamp: "Yesterday",
    severity: "Low",
    alertType: "Preventive Alert",
    category: "Biosecurity",
    title: "Fly Mesh Perimeter Inspection Passed",
    location: "Shed 06 - Breeding Enclosure",
    description: "Vector barrier integrity verified by farm superintendent. Zero breaches found in Capripox isolation perimeter.",
    affectedTag: "Barrier #B-06",
    status: "Resolved",
    actionRequired: "Re-inspect in 7 days",
    dispatchStatus: "Completed",
    badgeColor: "slate"
  }
];

export const MOCK_HEALTH_REPORTS = [
  {
    id: "REP-2026-0881",
    animalId: "AN-GJ-2024-0104",
    animalTag: "TAG-8821",
    animalName: "Ganga (Gir Cattle)",
    date: "Oct 06, 2026",
    veterinarian: "Dr. Rajesh Patel, M.V.Sc (Epidemiology)",
    vetReviewStatus: "Signed & Certified",
    diagnosticType: "Multimodal AI + Clinical Examination",
    provisionalDiagnosis: "Foot-and-Mouth Disease (Vesicular Stage 2)",
    severity: "Severe",
    riskLevel: "CRITICAL",
    confidence: 94.6,
    symptoms: [
      "Hypersalivation (ropy drooling)",
      "Mouth mucosal erosions & dental pad ulceration",
      "Coronary band inflammation causing severe lameness",
      "Core body temperature 104.8°F"
    ],
    vitalsSummary: "Temp: 104.8°F | Pulse: 88 bpm | Rumen: 2/5 min | Milk: -35%",
    labResults: {
      wbc: "14,800 /μL (Markedly Elevated)",
      rbc: "6.2 M/μL (Normal)",
      platelets: "290 K/μL (Normal)",
      pcrStatus: "Swab Sample Dispatched to NIHSAD Bhopal",
      fecalParasite: "Negative"
    },
    recommendationSummary:
      "Strict quarantine in Pen 04, isotonic saline oral wash, soft porridge feed diet, antipyrine analgesia. Zero livestock movement permitted.",
    previousHistory:
      "FMD Quadrivalent booster received Oct 12, 2025. Last routine health check on Aug 15, 2026 was completely clear.",
    status: "Under Treatment",
    isContagious: true
  },
  {
    id: "REP-2026-0880",
    animalId: "AN-GJ-2024-0412",
    animalTag: "TAG-7719",
    animalName: "Nandi (Kankrej Bull)",
    date: "Oct 05, 2026",
    veterinarian: "Dr. Ananya Sharma, Ph.D (Infectious Diseases)",
    vetReviewStatus: "Signed & Certified",
    diagnosticType: "Computer Vision Skin Biometrics",
    provisionalDiagnosis: "Lumpy Skin Disease (Capripox Acute Phase)",
    severity: "Critical",
    riskLevel: "HIGH",
    confidence: 91.2,
    symptoms: [
      "Circumscribed 2-5cm cutaneous nodules across neck and perineum",
      "Prescapular lymphadenopathy marked",
      "Core body temperature 105.1°F",
      "Marked depression and anorexia"
    ],
    vitalsSummary: "Temp: 105.1°F | Pulse: 96 bpm | Resp: 38 bpm",
    labResults: {
      wbc: "18,200 /μL (Marked Leukocytosis)",
      skinScraping: "Intracellular viral inclusion bodies noted",
      pcrStatus: "Positive for Capripox DNA (Local Assay)",
      lymphNodes: "Prescapular Lymphadenopathy ++"
    },
    recommendationSummary:
      "Complete isolation under fly netting, vector control sprays, antibiotic prophylaxis for secondary bacterial pyoderma.",
    previousHistory:
      "Anthrax Spore vaccine administered Feb 14, 2025. LSD booster overdue by 6 months.",
    status: "Isolated",
    isContagious: true
  },
  {
    id: "REP-2026-0879",
    animalId: "AN-GJ-2024-0105",
    animalTag: "TAG-8822",
    animalName: "Shyamali (Murrah Buffalo)",
    date: "Oct 04, 2026",
    veterinarian: "Dr. Vikram Rao, B.V.Sc & A.H.",
    vetReviewStatus: "Signed & Certified",
    diagnosticType: "In-line Milk Somatic Cell Analysis",
    provisionalDiagnosis: "Subclinical Mastitis (Right Hind Quarter)",
    severity: "Moderate",
    riskLevel: "MODERATE",
    confidence: 88.5,
    symptoms: [
      "Quarter milk electrical conductivity 6.8 mS/cm",
      "Somatic cell count 620,000 cells/mL",
      "CMT reagent score 2+ (coagulated gel)"
    ],
    vitalsSummary: "Temp: 102.3°F | Pulse: 72 bpm | Milk Cond: 6.8 mS/cm",
    labResults: {
      scc: "620,000 cells/mL (High)",
      californiaMastitisTest: "2+ (Gel Formation)",
      culture: "Staphylococcus aureus presumptive colony count 400 CFU/mL",
      antibioticSensitivity: "Sensitive to Cefquinome, Enrofloxacin"
    },
    recommendationSummary:
      "Intramammary dry-cow infusion following veterinary guidelines, frequent milking out.",
    previousHistory:
      "Calved 4 months ago; peak daily yield was 16.5 L. Brucellosis S19 vaccinated Jan 2026.",
    status: "Treatment Ongoing",
    isContagious: false
  },
  {
    id: "REP-2026-0878",
    animalId: "AN-PB-2024-0210",
    animalTag: "TAG-9014",
    animalName: "Rani (Sahiwal Cattle)",
    date: "Oct 01, 2026",
    veterinarian: "Dr. Harpreet Singh, M.V.Sc (Animal Reproduction)",
    vetReviewStatus: "Signed & Certified",
    diagnosticType: "Routine Bi-Annual Health Audit",
    provisionalDiagnosis: "Clinically Healthy / High Production Status",
    severity: "Normal",
    riskLevel: "LOW",
    confidence: 98.4,
    symptoms: ["No pathological symptoms observed"],
    vitalsSummary: "Temp: 101.2°F | Pulse: 64 bpm | Rumination: 480 min",
    labResults: {
      wbc: "8,100 /μL (Optimal)",
      rbc: "7.0 M/μL (Optimal)",
      milkFat: "4.8% | SNF: 8.9%",
      brucellosisScreening: "Negative (Rose Bengal Plate Test)"
    },
    recommendationSummary:
      "Maintain existing Total Mixed Ration (TMR) feed formulation; booster scheduled for Dec 2026.",
    previousHistory:
      "LSD Neethling Strain vaccinated Nov 2025. Excellent lactation performance.",
    status: "Cleared",
    isContagious: false
  }
];

export const MOCK_VET_CASES = [
  {
    id: "CASE-2026-041",
    animalTag: "TAG-8821",
    animalName: "Ganga",
    species: "Cattle (Gir)",
    location: "Shed 04 - Bay A",
    riskLevel: "CRITICAL",
    aiCondition: "Foot and Mouth Disease (FMD)",
    confidence: 94.6,
    attendingVet: "Dr. Rajesh Patel",
    caseStatus: "Under Clinical Treatment",
    followUpDate: "Tomorrow, Oct 07, 2026 (09:00 AM)",
    vetNotes: "Lesions stage 2 observed on tongue. Analgesia administered. Cohort quarantine strictly enforced.",
    treatments: [
      { medicine: "Flunixin Meglumine 50mg/mL", dosage: "15 mL IV once daily", duration: "3 days", status: "Active", requiresVetApproval: true },
      { medicine: "Povidone Iodine 1% Oral Paint", dosage: "Topical application 2x daily", duration: "5 days", status: "Active", requiresVetApproval: false }
    ]
  },
  {
    id: "CASE-2026-042",
    animalTag: "TAG-7719",
    animalName: "Nandi",
    species: "Cattle (Kankrej)",
    location: "Shed 06 - Enclosure",
    riskLevel: "HIGH",
    aiCondition: "Lumpy Skin Disease (Capripox)",
    confidence: 91.2,
    attendingVet: "Dr. Ananya Sharma",
    caseStatus: "Quarantine Enforced",
    followUpDate: "Oct 08, 2026 (02:00 PM)",
    vetNotes: "Nodules prominent across dewlap. Vector netting installed. Antibiotic cover started.",
    treatments: [
      { medicine: "Meloxicam + Paracetamol Bolus", dosage: "2 boluses orally twice daily", duration: "4 days", status: "Active", requiresVetApproval: true },
      { medicine: "Enrofloxacin 10% Injection", dosage: "20 mL IM once daily", duration: "5 days", status: "Active", requiresVetApproval: true }
    ]
  },
  {
    id: "CASE-2026-043",
    animalTag: "TAG-6119",
    animalName: "Badal",
    species: "Goat (Jamnapari)",
    location: "Pen 08",
    riskLevel: "HIGH",
    aiCondition: "Bovine / Small Ruminant Respiratory Complex",
    confidence: 87.0,
    attendingVet: "Dr. Meenakshi Sundaram",
    caseStatus: "Pending Vet Review",
    followUpDate: "Today, Oct 06, 2026 (04:30 PM)",
    vetNotes: "Nasal catarrh and cough detected. Physical thoracic auscultation scheduled for this afternoon.",
    treatments: [
      { medicine: "Oxytetracycline 20% LA", dosage: "3 mL deep IM single dose", duration: "1 day", status: "Pending Review", requiresVetApproval: true }
    ]
  },
  {
    id: "CASE-2026-044",
    animalTag: "TAG-8822",
    animalName: "Shyamali",
    species: "Buffalo (Murrah)",
    location: "Shed 02",
    riskLevel: "MODERATE",
    aiCondition: "Subclinical Mastitis",
    confidence: 88.5,
    attendingVet: "Dr. Vikram Rao",
    caseStatus: "Under Clinical Treatment",
    followUpDate: "Oct 09, 2026 (10:00 AM)",
    vetNotes: "CMT 2+ right hind quarter. Intramammary infusion completed. Re-test electrical conductivity in 72h.",
    treatments: [
      { medicine: "Cefquinome Sulfate intramammary", dosage: "1 applicator in RH teat", duration: "3 days", status: "Active", requiresVetApproval: true }
    ]
  }
];

export const MOCK_MEDICINES = [
  {
    id: "MED-01",
    name: "Flunixin Meglumine Injection (50 mg/mL)",
    category: "Non-Steroidal Anti-Inflammatory (NSAID) & Analgesic",
    standardDosage: "2.2 mg/kg body weight IV once daily (up to 3 days)",
    indications: "Control of pyrexia in acute respiratory infections, acute mastitis, and musculoskeletal lameness.",
    contraindications: "Severe dehydration, active gastric ulceration, or renal dysfunction.",
    approvalNotice: "SCHEDULE H PRESCRIPTION DRUG: Requires explicit licensed veterinary prescription.",
    requiresVetApproval: true
  },
  {
    id: "MED-02",
    name: "Meloxicam + Paracetamol Bolus (100mg + 1500mg)",
    category: "Antipyretic & Anti-inflammatory",
    standardDosage: "0.5 mg/kg body weight PO once daily with feed",
    indications: "Management of high fever and nodular pain in Lumpy Skin Disease and arthritis.",
    contraindications: "Late pregnancy or concurrent administration with corticosteroids.",
    approvalNotice: "PRESCRIPTION REQUIRED: Requires certified veterinary confirmation.",
    requiresVetApproval: true
  },
  {
    id: "MED-03",
    name: "Cefquinome Sulfate Intramammary Infusion",
    category: "4th Generation Cephalosporin Antibiotic",
    standardDosage: "1 syringe infused into affected quarter every 12 hours for 3 milkings",
    indications: "Clinical and subclinical mastitis caused by Staphylococcus and Streptococcus spp.",
    contraindications: "Hypersensitivity to cephalosporins. Milk withholding period: 96 hours.",
    approvalNotice: "CRITICAL ANTIMICROBIAL: Strict veterinary oversight and AST validation required.",
    requiresVetApproval: true
  },
  {
    id: "MED-04",
    name: "Electrolyte & Rehydration Soluble Powder",
    category: "Supportive Nutritional Therapy",
    standardDosage: "50g dissolved in 2 liters of drinking water twice daily",
    indications: "Supportive recovery in viral infections, fever, and dehydration.",
    contraindications: "None under standard dosage.",
    approvalNotice: "Supportive OTC Formulation. Does not require formal prescription.",
    requiresVetApproval: false
  }
];

export const MOCK_VETS = [
  {
    id: "VET-01",
    name: "Dr. Rajesh Patel",
    qualifications: "M.V.Sc (Epidemiology), NDRI Alumnus",
    designation: "Chief Veterinary Medical Officer",
    institution: "District Veterinary Polyclinic, Anand",
    experience: "16+ years",
    rating: 4.9,
    casesHandled: 1240,
    specialization: "Epizootiology & Large Ruminant Medicine",
    availableToday: true,
    nextAvailableSlot: "Today, 10:30 AM",
    contactPhone: "+91 98250 44102",
    avatar: "https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=300&q=80",
    assignedArea: "Anand & Kheda Agri-Zone"
  },
  {
    id: "VET-02",
    name: "Dr. Ananya Sharma",
    qualifications: "Ph.D (Virology & Veterinary Public Health), IVRI",
    designation: "Zonal Infectious Disease Specialist",
    institution: "State Animal Disease Surveillance Unit",
    experience: "11 years",
    rating: 4.95,
    casesHandled: 980,
    specialization: "Viral Zoonoses, Capripox & Biosecurity",
    availableToday: true,
    nextAvailableSlot: "Today, 02:00 PM",
    contactPhone: "+91 98791 22419",
    avatar: "https://images.unsplash.com/photo-1594824813589-98ff952f447a?auto=format&fit=crop&w=300&q=80",
    assignedArea: "Gujarat Central Surveillance Cluster"
  },
  {
    id: "VET-03",
    name: "Dr. Vikram Rao",
    qualifications: "B.V.Sc & A.H., PG Diploma in Herd Health",
    designation: "Dairy Herd Health Consultant",
    institution: "National Dairy Development Board (NDDB)",
    experience: "8 years",
    rating: 4.8,
    casesHandled: 710,
    specialization: "Mastitis Control & Precision Milking Telemetry",
    availableToday: false,
    nextAvailableSlot: "Tomorrow, 09:00 AM",
    contactPhone: "+91 94270 88201",
    avatar: "https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=300&q=80",
    assignedArea: "Co-operative Dairy Network"
  },
  {
    id: "VET-04",
    name: "Dr. Meenakshi Sundaram",
    qualifications: "M.V.Sc (Pathology), TANUVAS",
    designation: "Small Ruminant & Caprine Specialist",
    institution: "Regional Veterinary Diagnostic Laboratory",
    experience: "13 years",
    rating: 4.85,
    casesHandled: 890,
    specialization: "PPR, Blue Tongue & Enterotoxaemia",
    availableToday: true,
    nextAvailableSlot: "Today, 04:15 PM",
    contactPhone: "+91 94441 55099",
    avatar: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=300&q=80",
    assignedArea: "Peninsular Pastoral Belt"
  }
];

export const MOCK_ANALYTICS_DATA = {
  monthlyPrevalence: [
    { month: "May", lsd: 14, fmd: 8, mastitis: 26, respiratory: 19 },
    { month: "Jun", lsd: 22, fmd: 6, mastitis: 31, respiratory: 23 },
    { month: "Jul", lsd: 48, fmd: 12, mastitis: 35, respiratory: 29 }, // Monsoon outbreak peak
    { month: "Aug", lsd: 64, fmd: 19, mastitis: 38, respiratory: 34 },
    { month: "Sep", lsd: 39, fmd: 14, mastitis: 29, respiratory: 22 },
    { month: "Oct", lsd: 18, fmd: 9, mastitis: 24, respiratory: 16 }
  ],
  speciesDistribution: [
    { species: "Cattle (Bovine)", count: 780, percentage: 54.9, healthy: 710, atRisk: 52, critical: 18 },
    { species: "Buffalo (Bubaline)", count: 420, percentage: 29.6, healthy: 398, atRisk: 21, critical: 1 },
    { species: "Goat (Caprine)", count: 140, percentage: 9.9, healthy: 132, atRisk: 8, critical: 0 },
    { species: "Sheep (Ovine)", count: 80, percentage: 5.6, healthy: 78, atRisk: 2, critical: 0 }
  ],
  riskDistributionSummary: {
    healthy: 1318,
    healthyPercentage: 92.8,
    atRisk: 83,
    atRiskPercentage: 5.8,
    critical: 19,
    criticalPercentage: 1.4
  },
  treatmentOutcomes: [
    { category: "Full Clinical Recovery", count: 218, percentage: 84.5 },
    { category: "Ongoing Supportive Care", count: 28, percentage: 10.9 },
    { category: "Chronic Quota Reduction", count: 8, percentage: 3.1 },
    { category: "Mortality / Severe Epizootic Loss", count: 4, percentage: 1.5 }
  ],
  aiDetectionStats: {
    averageConfidence: 91.4,
    earlyDetectionLeadTimeDays: 3.5,
    falsePositiveRate: "3.2%",
    totalScansConducted: 4890,
    telemetryAnomaliesFlagged: 312
  },
  regionalRiskZones: [
    { district: "Anand (Gujarat)", riskLevel: "Critical (Orange Alert)", activeCases: 38, cattlePopulation: "184,000", quarantineHubs: 3 },
    { district: "Karnal (Haryana)", riskLevel: "Moderate (Yellow Alert)", activeCases: 14, cattlePopulation: "210,000", quarantineHubs: 1 },
    { district: "Ludhiana (Punjab)", riskLevel: "Low (Green Alert)", activeCases: 6, cattlePopulation: "295,000", quarantineHubs: 1 },
    { district: "Pune (Maharashtra)", riskLevel: "Moderate (Yellow Alert)", activeCases: 17, cattlePopulation: "172,000", quarantineHubs: 2 },
    { district: "Salem (Tamil Nadu)", riskLevel: "Low (Green Alert)", activeCases: 4, cattlePopulation: "128,000", quarantineHubs: 0 }
  ],
  earlyWarningLeadTimeDays: [
    { condition: "Lumpy Skin Disease", daysBeforeClinicalSign: 3.4, confidence: 91.2 },
    { condition: "Subclinical Mastitis", daysBeforeClinicalSign: 4.8, confidence: 94.0 },
    { condition: "Foot and Mouth Disease", daysBeforeClinicalSign: 2.1, confidence: 89.6 },
    { condition: "Bovine Respiratory Disease", daysBeforeClinicalSign: 3.9, confidence: 87.5 }
  ],
  vaccinationBreakdown: [
    { disease: "FMD Booster", completed: 96, target: 100 },
    { disease: "LSD Neethling", completed: 92, target: 100 },
    { disease: "Brucellosis S19", completed: 88, target: 100 },
    { disease: "HS / BQ Combined", completed: 97, target: 100 },
    { disease: "PPR (Goat/Sheep)", completed: 94, target: 100 }
  ]
};

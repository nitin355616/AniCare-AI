/**
 * AniCare AI — English Translations (en)
 * Milestone 9D: Farmer Experience, Multilingual & Low-Literacy Localization
 */

export const en = {
  // General & Header
  appTitle: "AniCare AI",
  farmerPortal: "Farmer Portal",
  greeting: "Namaste, Farmer",
  subtitle: "Keep track of your animals' health easily",
  location: "Anand, Gujarat",
  language: "Language",
  english: "English",
  hindi: "हिंदी",
  listen: "Listen",
  speaking: "Speaking...",
  help: "Help & Safety",
  offlineNotice: "You are currently offline. Showing cached information.",
  disclaimer: "AI screening is not a final diagnosis. Please follow veterinary advice.",
  demoBadge: "DEMO DATA",

  // KPI Metrics
  totalAnimals: "My Animals",
  healthy: "Healthy",
  needsAttention: "Needs Attention",
  urgent: "Urgent Attention",

  // Status Labels
  statusHealthy: "Healthy",
  statusAttention: "Needs Attention",
  statusUrgent: "Urgent Attention Needed",
  statusReviewPending: "Doctor Review Pending",
  statusReviewed: "Doctor Examined",
  statusTreatment: "Treatment Active",
  statusFollowUpDue: "Follow-up Checkup Due",

  // Status Explanations
  explanationHealthy: "Your animal looks healthy and active. Continue routine care and clean water.",
  explanationAttention: "AI screening noticed mild unusual signs. A veterinary checkup is recommended.",
  explanationUrgent: "High fever or prominent lesions detected. Contact your veterinary doctor immediately.",

  // Action Steps (What to do now)
  whatToDoNow: "What should I do now?",
  stepIsolate: "Keep the animal in a clean, shaded area away from other cattle if advised.",
  stepClean: "Ensure fresh drinking water and keep the shed clean and dry.",
  stepObserve: "Watch closely for fever, changes in appetite, or new skin spots.",
  stepContactVet: "Contact your assigned veterinary officer for proper medicine.",

  // Contact Veterinary Actions
  contactVet: "Contact Veterinary Doctor",
  requestReview: "Request Doctor Visit",
  requestSent: "Doctor visit requested successfully!",
  doctorAssigned: "Assigned Doctor",
  doctorPhone: "Helpline",
  noDoctorAssigned: "Veterinary doctor will be assigned shortly.",

  // Treatment Plan View
  treatmentPlan: "Approved Treatment Plan",
  treatmentApprovedNotice: "This medicine plan was entered and approved by a qualified veterinary doctor. AI does not prescribe medicine.",
  medicines: "Prescribed Medicines",
  dosage: "Dose & Frequency",
  duration: "Duration",
  instructions: "Doctor's Instructions",
  startDate: "Started On",
  endDate: "Complete By",
  noTreatment: "No active medical treatment recorded for this animal.",

  // Food Safety / Milk Withdrawal
  milkMeatSafety: "Milk & Food Safety Notice",
  withdrawalActive: "DO NOT sell or consume milk from this cow until the safety period ends.",
  withdrawalRemaining: "days remaining in safety period",
  withdrawalNone: "No milk or meat withholding restrictions active.",
  withdrawalVerify: "Consult your veterinary doctor before using milk from this treated cow.",

  // Vaccination Tracking
  vaccination: "Vaccination Record",
  nextVaccination: "Next Due Date",
  lastVaccination: "Last Administered",
  vaccineName: "Vaccine Name",
  targetDisease: "Protects Against",
  vaccinationOverdue: "Vaccination Overdue!",
  vaccinationUpcoming: "Vaccination Upcoming",
  noVaccination: "No vaccination history recorded yet.",

  // Follow-Up Reminders
  followUp: "Follow-up Examination",
  nextCheckup: "Next Scheduled Checkup",
  followUpOverdue: "Checkup is Overdue",
  noFollowUp: "No follow-up checkup currently scheduled.",

  // Outbreak Warning for Farmers
  outbreakWarningTitle: "Local Health Alert in Your Area",
  outbreakWarningText: "Health surveillance has been increased in your village sector. Please monitor your cattle closely and report any skin lumps or fever immediately.",
  outbreakWarningAction: "Protect cattle from flies and mosquitoes, and avoid mixing herds at common water ponds.",

  // Animal Detail Dossier
  animalDossier: "Animal Health Card",
  tag: "Tag Number",
  breed: "Breed",
  age: "Age",
  weight: "Weight",
  lastCheck: "Last Checked",
  close: "Close",

  // Filters & Tabs
  tabAll: "All Animals",
  tabUrgent: "Urgent (Need Doctor)",
  tabAttention: "Need Attention",
  tabHealthy: "Healthy",

  // Empty States
  emptyAnimals: "No animals added yet. Register your first animal to begin health tracking.",
  emptyAlerts: "No active health alerts. Your herd is looking good!",
  emptyTreatment: "No treatment records found for this animal.",

  // Onboarding
  onboardingTitle: "Welcome to AniCare AI",
  onboardingStep1: "Take photos of your cow or buffalo to quickly check for skin lumps and fever signs.",
  onboardingStep2: "If abnormal signs appear, get simple advice and connect with your government veterinary doctor.",
  onboardingStep3: "Track milk withdrawal dates, medicines, and vaccination schedules easily.",
  onboardingDone: "Get Started",
  onboardingSkip: "Skip",

  // Help Center Topics
  helpTitle: "Help & Farmer Safety",
  faq1Q: "Can AI diagnose my animal?",
  faq1A: "No. The AI provides early warnings and visual screening only. Only a certified veterinarian can diagnose and prescribe medicines.",
  faq2Q: "Why is milk withdrawal important?",
  faq2A: "Some injected antibiotics enter milk. Consuming this milk can harm children and adults. Always observe the doctor's withdrawal period.",
  faq3Q: "What should I do if my cow gets skin nodules?",
  faq3A: "Separate the cow in a dry shed, apply mosquito repellent, do not sell the milk, and request an immediate veterinary doctor visit.",
  faq4Q: "Is my personal farm information private?",
  faq4A: "Yes. Your animals and health records are completely private to you and your assigned veterinary doctor.",

  // Milestone 10: Sync & Offline Architecture
  syncSynced: "Synced",
  syncWaiting: "Waiting to sync",
  syncSyncing: "Syncing...",
  syncIssue: "Sync issue",
  syncNow: "Sync Now",
  syncPanelTitle: "Sync & Offline Status",
  lastSynced: "Last synced",
  pendingActions: "Pending Actions",
  failedActions: "Failed Actions",
  conflicts: "Conflicts",
  serverReachable: "Server Reachable",
  serverUnreachable: "Server Unreachable",
  connectionState: "Connection",
  retryFailed: "Retry Failed",
  clearSync: "Clear Synced",
  offlineBannerTitle: "You are currently offline",
  offlineBannerMsg: "You can view previously cached records. New observations are safely preserved on this device and will sync automatically when connection returns.",
  staleDataWarning: "This information was cached earlier and may be outdated. Connect to internet for latest telemetry.",
  offlineObservation: "Record Offline Health Observation",
  offlineObservationPrompt: "Describe animal behavior, feeding, or symptoms observed today:",
  saveOfflineObservation: "Save Observation Offline",
  offlineObservationSaved: "Observation saved on this device. Waiting for internet connection to sync.",
  screeningOfflineNotice: "This photo will be submitted for AI screening once an internet connection is established.",
  conflictClinicalNotice: "This record was updated by a veterinary officer. The latest approved clinical record is preserved."
};

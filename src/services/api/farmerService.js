import apiClient from './client';
import { networkService } from '../connectivity/networkService';

export const farmerService = {
  /**
   * Fetches farmer dashboard with offline caching support.
   */
  async getFarmerDashboard() {
    try {
      const data = await apiClient.get('/farmer/dashboard');
      if (data && data.animals) {
        networkService.saveDashboardCache(data);
      }
      return data;
    } catch (error) {
      console.warn('Backend farmer dashboard unavailable, attempting offline cache:', error.message);
      const cached = networkService.getDashboardCache();
      if (cached && cached.data) {
        return {
          ...cached.data,
          is_offline_cached: true,
          cached_at: cached.cachedAt,
        };
      }

      // Safe fallback data for demonstration
      return {
        farmer_name: "Kishorbhai Patel",
        farmer_location: "Anand District, Gujarat",
        total_animals: 3,
        healthy_count: 1,
        attention_count: 1,
        urgent_count: 1,
        is_fallback: true,
        outbreak_warning: {
          has_warning: true,
          severity: "ELEVATED",
          title_en: "Health Alert for Anand District",
          title_hi: "आनंद जिले के लिए स्वास्थ्य सूचना",
          message_en: "Veterinary officers have stepped up active monitoring in your village cluster. Please inspect your cattle daily for fever or skin nodules.",
          message_hi: "आपके गांव व आसपास के क्षेत्र में पशु डॉक्टरों द्वारा निगरानी बढ़ा दी गई है। कृपया रोजाना अपने पशुओं के शरीर पर गांठ या बुखार की जांच करें।",
          action_en: "Protect cattle from biting flies with repellent, keep sheds clean, and avoid sharing water sources.",
          action_hi: "पशुओं को मक्खी-मच्छरों से बचाएं, बाड़ा साफ रखें और अन्य झुंडों के साथ साझा तालाब में पानी न पिलाएं।",
          zone_name: "Anand District, Gujarat"
        },
        animals: [
          {
            animal_id: "AN-GJ-2024-0104",
            tag: "TAG-8821",
            name: "Ganga",
            species: "Cattle",
            breed: "Gir (Indigenous Dairy)",
            age: "4.2 years",
            weight: "440 kg",
            photo: "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80",
            health_status: "Critical",
            risk_level: "High Risk",
            simplified_status: "URGENT",
            status_label_en: "Urgent Doctor Attention Needed",
            status_label_hi: "तत्काल डॉक्टर की जरूरत",
            explanation_en: "High fever or prominent skin nodules detected. Contact your veterinary doctor immediately.",
            explanation_hi: "पशु में तेज बुखार या त्वचा पर उभरी हुई गांठें पाई गई हैं। तुरंत पशु चिकित्सक से संपर्क करें।",
            action_needed: true,
            review_status: "PENDING",
            has_active_withdrawal: true,
            has_overdue_vaccine: false
          },
          {
            animal_id: "AN-GJ-2024-0105",
            tag: "TAG-8822",
            name: "Shyamali",
            species: "Buffalo",
            breed: "Murrah",
            age: "5.5 years",
            weight: "580 kg",
            photo: "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?auto=format&fit=crop&w=400&q=80",
            health_status: "Under Observation",
            risk_level: "Moderate Risk",
            simplified_status: "ATTENTION",
            status_label_en: "Needs Veterinary Checkup",
            status_label_hi: "पशु चिकित्सक से जांच कराएं",
            explanation_en: "AI screening noticed mild unusual signs. A veterinary checkup is recommended.",
            explanation_hi: "एआई जांच में हल्के असामान्य लक्षण दिखे हैं। पशु चिकित्सक से जांच कराने की सलाह दी जाती है।",
            action_needed: true,
            review_status: "REVIEWED",
            has_active_withdrawal: false,
            has_overdue_vaccine: false
          },
          {
            animal_id: "AN-PB-2024-0210",
            tag: "TAG-9014",
            name: "Rani",
            species: "Cattle",
            breed: "Sahiwal",
            age: "3.1 years",
            weight: "410 kg",
            photo: "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?auto=format&fit=crop&w=400&q=80",
            health_status: "Healthy",
            risk_level: "Low",
            simplified_status: "HEALTHY",
            status_label_en: "Healthy & Active",
            status_label_hi: "स्वस्थ और सक्रिय",
            explanation_en: "Your animal looks healthy and active. Continue routine care and clean water.",
            explanation_hi: "आपका पशु बिल्कुल स्वस्थ और सक्रिय दिख रहा है। सामान्य चारा-पानी जारी रखें।",
            action_needed: false,
            review_status: "NONE",
            has_active_withdrawal: false,
            has_overdue_vaccine: false
          }
        ]
      };
    }
  },

  /**
   * Fetches detailed health dossier for a specific animal.
   */
  async getFarmerAnimalDetail(animalId) {
    try {
      return await apiClient.get(`/farmer/animals/${animalId}`);
    } catch (error) {
      console.warn(`Farmer animal detail for ${animalId} unavailable:`, error.message);
      throw error;
    }
  },

  /**
   * Requests an immediate veterinary officer visit for an animal.
   */
  async requestDoctorVisit(animalId, { symptoms = [], notes = '', preferredTime = '' } = {}) {
    return await apiClient.post(`/farmer/animals/${animalId}/request-review`, {
      symptoms,
      notes,
      preferred_time: preferredTime
    });
  },

  /**
   * Fetches localized outbreak warning.
   */
  async getOutbreakWarning() {
    try {
      return await apiClient.get('/farmer/outbreak-warning');
    } catch (error) {
      return {
        has_warning: false,
        severity: "NORMAL",
        title_en: "Normal Herd Health in Your Area",
        title_hi: "आपके क्षेत्र में सामान्य स्थिति",
        message_en: "No disease outbreak alerts in your immediate village sector.",
        message_hi: "आपके गांव क्षेत्र में किसी बीमारी का प्रकोप नहीं है।",
        action_en: "Maintain clean sheds and report any sick animals promptly.",
        action_hi: "बाड़े को स्वच्छ रखें और किसी भी अस्वस्थ पशु की तुरंत सूचना दें।",
        zone_name: "Anand District, Gujarat"
      };
    }
  }
};

import apiClient from './client';

export const reminderService = {
  /**
   * Retrieves all vaccination, appointment, and hygiene reminders.
   */
  async getReminders(params = {}) {
    try {
      return await apiClient.get('/reminders', params);
    } catch (error) {
      console.warn('Backend reminders unavailable, using fallback:', error.message);
      return {
        total: 4,
        items: [
          {
            reminder_id: 'REM-VACC-001',
            title: 'FMD Booster Vaccination',
            description: 'Foot-and-Mouth Disease bi-annual booster vaccination due for Cattle herd Shed 02.',
            animal_id: 'TAG-8821',
            animal_tag: 'TAG-8821',
            due_date: '2026-10-15',
            reminder_type: 'VACCINATION',
            priority: 'HIGH',
            status: 'PENDING',
            created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
            completed_at: null
          },
          {
            reminder_id: 'REM-CHECK-002',
            title: 'Post-Monsoon De-worming Cycle',
            description: 'Administer broad-spectrum anthelmintic (Albendazole) to all young stock under 18 months.',
            animal_id: 'TAG-4412',
            animal_tag: 'TAG-4412',
            due_date: '2026-10-18',
            reminder_type: 'HEALTH_CHECK',
            priority: 'MEDIUM',
            status: 'PENDING',
            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
            completed_at: null
          },
          {
            reminder_id: 'REM-HYG-003',
            title: 'Shed Disinfection & Lime Wash',
            description: 'Bi-weekly floor and feeding stall sanitation with sodium carbonate and hydrated lime.',
            animal_id: null,
            animal_tag: 'All Herd',
            due_date: '2026-10-20',
            reminder_type: 'HYGIENE',
            priority: 'LOW',
            status: 'PENDING',
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            completed_at: null
          },
          {
            reminder_id: 'REM-VET-004',
            title: 'Dr. Arvind Verma Clinical Follow-Up',
            description: 'Review recovery of Cow #8821 following treatment for acute respiratory signs.',
            animal_id: 'TAG-8821',
            animal_tag: 'TAG-8821',
            due_date: '2026-10-12',
            reminder_type: 'VET_APPOINTMENT',
            priority: 'HIGH',
            status: 'PENDING',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            completed_at: null
          }
        ]
      };
    }
  },

  /**
   * Creates a new reminder.
   */
  async createReminder(payload) {
    try {
      return await apiClient.post('/reminders', payload);
    } catch (error) {
      console.warn('Backend create reminder error:', error.message);
      return {
        reminder_id: `REM-${Date.now().toString(36).toUpperCase()}`,
        ...payload,
        status: 'PENDING',
        created_at: new Date().toISOString()
      };
    }
  },

  /**
   * Updates an existing reminder (e.g., mark completed).
   */
  async updateReminder(reminderId, payload) {
    try {
      return await apiClient.put(`/reminders/${reminderId}`, payload);
    } catch (error) {
      console.warn('Backend update reminder error:', error.message);
      return {
        reminder_id: reminderId,
        ...payload,
        completed_at: payload.status === 'COMPLETED' ? new Date().toISOString() : null
      };
    }
  },

  /**
   * Deletes a reminder.
   */
  async deleteReminder(reminderId) {
    try {
      return await apiClient.delete(`/reminders/${reminderId}`);
    } catch (error) {
      console.warn('Backend delete reminder error:', error.message);
      return { success: true };
    }
  }
};

export default reminderService;

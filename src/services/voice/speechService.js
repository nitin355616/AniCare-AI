/**
 * AniCare AI — Farmer Speech Service (Web Speech API)
 * Milestone 9D: Low-Literacy Voice Guidance
 *
 * Provides text-to-speech for farmers who prefer audio readout
 * of advice, warnings, and status explanations.
 */

class SpeechService {
  constructor() {
    this.synth = typeof window !== 'undefined' && 'speechSynthesis' in window ? window.speechSynthesis : null;
    this.currentUtterance = null;
    this.voices = [];
    if (this.synth) {
      this.loadVoices();
      if (typeof window !== 'undefined' && window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => this.loadVoices();
      }
    }
  }

  isSupported() {
    return Boolean(this.synth && typeof window !== 'undefined' && 'SpeechSynthesisUtterance' in window);
  }

  loadVoices() {
    if (!this.synth) return;
    try {
      this.voices = this.synth.getVoices();
    } catch {
      this.voices = [];
    }
  }

  cleanText(text) {
    if (!text) return '';
    return text
      .replace(/[*_#`~[\]()]/g, '') // remove markdown symbols
      .replace(/https?:\/\/\S+/g, '') // remove URLs
      .replace(/\s+/g, ' ')
      .trim();
  }

  getBestVoice(lang = 'hi') {
    if (!this.voices || this.voices.length === 0) {
      this.loadVoices();
    }
    const targetTag = lang === 'hi' ? 'hi' : 'en';
    const voice = this.voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(targetTag));
    return voice || null;
  }

  speak(text, { lang = 'hi', rate = 0.95, pitch = 1.0, onStart, onEnd, onError } = {}) {
    if (!this.isSupported()) {
      if (onError) onError(new Error('SpeechSynthesis not supported'));
      return false;
    }

    this.stop();

    const cleaned = this.cleanText(text);
    if (!cleaned) return false;

    try {
      const utterance = new SpeechSynthesisUtterance(cleaned);
      utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
      utterance.rate = rate; // slightly slower for low-literacy clarity
      utterance.pitch = pitch;

      const voice = this.getBestVoice(lang);
      if (voice) {
        utterance.voice = voice;
      }

      utterance.onstart = () => {
        if (onStart) onStart();
      };
      utterance.onend = () => {
        this.currentUtterance = null;
        if (onEnd) onEnd();
      };
      utterance.onerror = (e) => {
        this.currentUtterance = null;
        if (onError) onError(e);
      };

      this.currentUtterance = utterance;
      this.synth.speak(utterance);
      return true;
    } catch (err) {
      if (onError) onError(err);
      return false;
    }
  }

  stop() {
    if (!this.synth) return;
    try {
      if (this.synth.speaking || this.synth.pending) {
        this.synth.cancel();
      }
      this.currentUtterance = null;
    } catch {
      // ignore cancel error
    }
  }

  isSpeaking() {
    return Boolean(this.synth && (this.synth.speaking || this.synth.pending));
  }
}

export const speechService = new SpeechService();

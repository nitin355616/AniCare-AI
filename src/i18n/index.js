import React, { createContext, useContext, useState, useCallback } from 'react';
import { en } from './en';
import { hi } from './hi';

const dictionaries = { en, hi };

export const TranslationContext = createContext({
  lang: 'hi',
  setLang: () => {},
  toggleLang: () => {},
  t: (key) => key,
});

export const TranslationProvider = ({ children }) => {
  const [lang, setLangState] = useState(() => {
    try {
      const saved = localStorage.getItem('anicare_lang');
      return saved === 'en' || saved === 'hi' ? saved : 'hi';
    } catch {
      return 'hi';
    }
  });

  const setLang = useCallback((newLang) => {
    if (newLang === 'en' || newLang === 'hi') {
      setLangState(newLang);
      try {
        localStorage.setItem('anicare_lang', newLang);
      } catch (err) {
        console.warn('Could not persist language preference:', err);
      }
    }
  }, []);

  const toggleLang = useCallback(() => {
    setLangState((prev) => {
      const next = prev === 'hi' ? 'en' : 'hi';
      try {
        localStorage.setItem('anicare_lang', next);
      } catch (err) {
        console.warn('Could not persist language preference:', err);
      }
      return next;
    });
  }, []);

  const t = useCallback(
    (key, fallback = '') => {
      const dict = dictionaries[lang] || dictionaries.en;
      if (dict && dict[key] !== undefined) {
        return dict[key];
      }
      // Fallback to English dictionary if key is missing in target language
      if (dictionaries.en && dictionaries.en[key] !== undefined) {
        return dictionaries.en[key];
      }
      return fallback || key;
    },
    [lang]
  );

  return React.createElement(
    TranslationContext.Provider,
    { value: { lang, setLang, toggleLang, t } },
    children
  );
};

export const useTranslation = () => useContext(TranslationContext);

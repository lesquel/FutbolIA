/**
 * FutbolIA - Internationalization Setup
 * Using i18next for multi-language support (ES/EN)
 */
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import es from "./locales/es.json";
import en from "./locales/en.json";

// Initialize i18next
i18n.use(initReactI18next).init({
  resources: {
    es: { translation: es },
    en: { translation: en },
  },
  lng: "es", // Default language
  fallbackLng: "es",
  interpolation: {
    escapeValue: false, // React already escapes
  },
  react: {
    useSuspense: false, // Disable suspense for React Native
  },
});

export default i18n;

// Helper function to change language
export const changeLanguage = (lang: "es" | "en") => {
  i18n.changeLanguage(lang);
};

// Get current language
export const getCurrentLanguage = (): string => {
  return i18n.language;
};

// Export useTranslation hook for components
export { useTranslation } from "react-i18next";

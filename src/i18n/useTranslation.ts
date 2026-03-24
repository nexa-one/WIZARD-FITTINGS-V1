import { useHVACStore } from '../store';
import { en, es, Translations } from './translations';

export function useTranslation(): Translations {
  const language = useHVACStore((s) => s.language);
  return language === 'es' ? es : en;
}

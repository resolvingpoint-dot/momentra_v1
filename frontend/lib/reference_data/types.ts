export type ReferenceItem = {
  code: string;
  label: string;
  icon?: string;
  color?: string;
  sort_order?: number;
  is_active?: boolean;
  taxonomy?: string;
  parent_code?: string;
  children?: ReferenceItem[];
};

export type CurrencyReference = ReferenceItem & {
  symbol: string;
  minor_unit: number;
  locale_hint?: string;
};

export type ReferenceDataBootstrap = {
  reference_data_version: number;
  metadata_version?: number;
  currencies: CurrencyReference[];
  countries: ReferenceItem[];
  locales: ReferenceItem[];
  timezones: ReferenceItem[];
  languages?: ReferenceItem[];
  categories: Record<string, ReferenceItem[]>;
};

export type ReferenceDataOptions = {
  reference_data_version: number;
  data: Record<string, ReferenceItem[] | CurrencyReference[]>;
};

export type MoneyValue = {
  amount_minor: number;
  currency_code: string;
};

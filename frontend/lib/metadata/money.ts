import { formatMinor } from "@/lib/reference_data/money";
import type { CurrencyReference } from "@/lib/reference_data/types";

export type PersonalAccountRecord = {
  id: string;
  account_id: string;
  account_name: string;
  account_type: string;
  account_type_label?: string;
  currency_code: string;
  current_balance?: string;
  current_balance_minor: number;
  opening_balance_minor?: number;
  is_default?: boolean;
  is_primary?: boolean;
  is_archived?: boolean;
  transaction_count?: number;
  created_at?: string | null;
  updated_at?: string | null;
};

export function formatAccountBalance(
  account: Pick<PersonalAccountRecord, "current_balance_minor" | "currency_code">,
  currencies: CurrencyReference[],
  locale: string,
): string {
  const currency =
    currencies.find((c) => c.code === account.currency_code) ?? {
      code: account.currency_code,
      minor_unit: 2,
      symbol: account.currency_code,
    };
  return formatMinor(account.current_balance_minor, currency, locale);
}

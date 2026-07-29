export function profileInitial(
  displayName: string | null | undefined,
  email: string | null | undefined,
): string {
  const fromName = displayName?.trim()?.[0];
  if (fromName) return fromName.toUpperCase();
  const fromEmail = email?.trim()?.[0];
  if (fromEmail) return fromEmail.toUpperCase();
  return "?";
}

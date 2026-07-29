import { AuthGate } from "@/components/auth/AuthGate";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <AuthGate>{children}</AuthGate>;
}

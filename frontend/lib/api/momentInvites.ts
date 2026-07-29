import { requestWithRetry } from "@/lib/api/client";

export type EmailInviteResponse = {
  id: string;
  email: string;
  status: string;
};

export async function sendMomentEmailInvite(
  momentId: string,
  email: string,
): Promise<EmailInviteResponse> {
  return requestWithRetry(`api/v1/moments/${momentId}/email-invites`, {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

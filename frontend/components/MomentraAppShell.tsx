"use client";

import { useEffect, useRef, useState } from "react";
import { MomentraTopBar } from "@/components/MomentraTopBar";
import { InviteQrScanModal } from "@/components/invite/InviteQrScanModal";
import { MomentraContextSwitcher } from "@/components/shell/MomentraContextSwitcher";
import { SettingsSheet } from "@/components/settings/SettingsSheet";
import { OnboardingScreen } from "@/components/onboarding/OnboardingScreen";
import { CompanySwitcher } from "@/components/business/workspace/CompanySwitcher";
import { CompanySettingsSheet } from "@/components/business/workspace/CompanySettingsSheet";
import { CompanyHomeSheet } from "@/components/business/workspace/CompanyHomeSheet";
import { JoinCompanySheet } from "@/components/business/workspace/JoinCompanySheet";
import { Life360Overlay } from "@/components/life360/Life360Overlay";
import { useAuth } from "@/components/auth/AuthProvider";
import {
  useAppContextState,
  useThemeTokens,
} from "@/components/theme/AppContextProvider";
import { MomentraAnalytics } from "@/lib/analytics";
import { acceptInvite } from "@/lib/api/group";
import { acceptBusinessWorkspaceInvite, updateBusinessWorkspace } from "@/lib/api/client";
import {
  openBusinessCreateOverlay,
  openBusinessMomentAndPulse,
} from "@/lib/businessShellEvents";
import { openGroupCreateOverlay, openGroupMomentAndPulse } from "@/lib/groupShellEvents";
import { openPersonalCreateOverlay } from "@/lib/personalShellEvents";
import { isBusinessMomentType } from "@/lib/invite/inviteToken";
import {
  consumeInviteJoinedResult,
  consumePendingCompanyInvite,
  consumePendingInvite,
} from "@/lib/invite/pendingInvite";
import type { AppContext } from "@/lib/appContext";
import {
  clearSwitchError,
  getContextSnapshot,
  subscribeContextStore,
} from "@/stores/contextStore";
import {
  createAndSelectBusinessWorkspace,
  ensureBusinessBootstrap,
  getBusinessWorkspaces,
  getSelectedBusinessWorkspace,
  softRefreshBusinessSession,
  switchBusinessWorkspace,
  useBusinessSessionStore,
} from "@/stores/businessSessionStore";
import { ensureGroupSession } from "@/stores/groupSessionStore";
import { ensurePersonalSession } from "@/stores/personalSessionStore";
import { ensureCircleSession } from "@/stores/circleSessionStore";

const PENDING_COMPANY_SWITCH_KEY = "momentra:pending-company-switch";

function dispatchInviteJoined(detail: {
  moment_id: string;
  moment_name: string;
  moment_type?: string | null;
  already_member?: boolean;
  participant_id?: string | null;
}) {
  window.dispatchEvent(new CustomEvent("momentra:invite-joined", { detail }));
}
type MomentraAppShellProps = {
  children: (context: AppContext) => React.ReactNode;
};

export function MomentraAppShell({ children }: MomentraAppShellProps) {
  const { context, mountedContexts, setContext } = useAppContextState();
  const tokens = useThemeTokens();
  const { user, isLoading, logout, setUser } = useAuth();
  const [showSettings, setShowSettings] = useState(false);
  const [showOnboardingReplay, setShowOnboardingReplay] = useState(false);
  const [showScanInvite, setShowScanInvite] = useState(false);
  const [switchError, setSwitchError] = useState<string | null>(null);
  const [showCompanySwitcher, setShowCompanySwitcher] = useState(false);
  const [showCompanySettings, setShowCompanySettings] = useState(false);
  const [showCompanyHome, setShowCompanyHome] = useState(false);
  const [showJoinCompany, setShowJoinCompany] = useState(false);
  const [showLife360, setShowLife360] = useState(false);
  const canScanInvite = context === "group" || context === "business";
  const pendingInviteHandled = useRef(false);
  const pendingCompanyInviteHandled = useRef(false);
  const businessSession = useBusinessSessionStore();
  const selectedWorkspace = getSelectedBusinessWorkspace();
  const workspaces = getBusinessWorkspaces();
  const isBusiness = context === "business";
  const isGroup = context === "group";
  const isPersonal = context === "personal";
  const isCircle = context === "circle";

  useEffect(() => {
    if (showSettings) {
      void MomentraAnalytics.logScreen("settings");
      void MomentraAnalytics.logCustomEvent("settings_open");
    }
  }, [showSettings]);

  useEffect(() => {
    if (showLife360) {
      void MomentraAnalytics.logScreen("life360");
      void MomentraAnalytics.logCustomEvent("life360_open");
    }
  }, [showLife360]);

  useEffect(() => {
    if (showScanInvite) {
      void MomentraAnalytics.logScreen("invite_scan");
      void MomentraAnalytics.logCustomEvent("invite_scan_open");
    }
  }, [showScanInvite]);

  useEffect(() => {
    if (!isBusiness || !user) return;
    void ensureBusinessBootstrap();
  }, [isBusiness, user]);

  useEffect(() => {
    if (!isGroup || !user) return;
    void ensureGroupSession();
  }, [isGroup, user]);

  useEffect(() => {
    if (!isPersonal || !user) return;
    void ensurePersonalSession();
  }, [isPersonal, user]);

  useEffect(() => {
    if (!isCircle || !user) return;
    void ensureCircleSession();
  }, [isCircle, user]);

  useEffect(() => {
    const openSettings = () => setShowCompanySettings(true);
    window.addEventListener("momentra:business-company-settings", openSettings);
    return () =>
      window.removeEventListener("momentra:business-company-settings", openSettings);
  }, []);

  useEffect(() => {
    if (!user || pendingCompanyInviteHandled.current) return;

    const switchId =
      typeof window !== "undefined"
        ? sessionStorage.getItem(PENDING_COMPANY_SWITCH_KEY)
        : null;
    if (switchId) {
      sessionStorage.removeItem(PENDING_COMPANY_SWITCH_KEY);
      pendingCompanyInviteHandled.current = true;
      setContext("business");
      void switchBusinessWorkspace(switchId).then(() => setShowCompanyHome(true));
      return;
    }

    const companyToken = consumePendingCompanyInvite();
    if (!companyToken) return;
    pendingCompanyInviteHandled.current = true;
    void (async () => {
      try {
        void MomentraAnalytics.logCustomEvent("company_invite_deep_link_open", {
          source: "pending_after_login",
        });
        const ws = await acceptBusinessWorkspaceInvite(companyToken);
        void MomentraAnalytics.logCustomEvent("company_invite_accept_success");
        setContext("business");
        await switchBusinessWorkspace(ws.id);
        setShowCompanyHome(true);
      } catch {
        void MomentraAnalytics.logCustomEvent("company_invite_accept_failed");
        pendingCompanyInviteHandled.current = false;
      }
    })();
  }, [user, setContext]);

  useEffect(() => {
    if (!user || pendingInviteHandled.current) return;

    const stashed = consumeInviteJoinedResult();
    if (stashed) {
      pendingInviteHandled.current = true;
      const biz = isBusinessMomentType(stashed.moment_type);
      setContext(biz ? "business" : "group");
      window.setTimeout(() => {
        if (biz) {
          openBusinessMomentAndPulse(
            stashed.moment_id,
            stashed.moment_type || "TEAM_OPERATIONS",
          );
          dispatchInviteJoined(stashed);
        } else {
          openGroupMomentAndPulse({
            moment_id: stashed.moment_id,
            moment_type: stashed.moment_type,
          });
        }
      }, 0);
      return;
    }

    const token = consumePendingInvite();
    if (!token) return;
    pendingInviteHandled.current = true;
    void (async () => {
      try {
        void MomentraAnalytics.logCustomEvent("invite_deep_link_open", {
          source: "pending_after_login",
        });
        const result = await acceptInvite(token);
        void MomentraAnalytics.logCustomEvent("invite_accept_success", {
          already_member: Boolean(result.already_member),
        });
        const biz = isBusinessMomentType(result.moment_type);
        setContext(biz ? "business" : "group");
        window.setTimeout(() => {
          if (biz) {
            openBusinessMomentAndPulse(
              result.moment_id,
              result.moment_type || "TEAM_OPERATIONS",
            );
            dispatchInviteJoined(result);
          } else {
            openGroupMomentAndPulse({
              moment_id: result.moment_id,
              moment_type: result.moment_type,
            });
          }
        }, 0);
      } catch {
        void MomentraAnalytics.logCustomEvent("invite_accept_failed");
        pendingInviteHandled.current = false;
      }
    })();
  }, [user, setContext]);

  useEffect(() => {
    return subscribeContextStore(() => {
      setSwitchError(getContextSnapshot().switchError);
    });
  }, []);

  useEffect(() => {
    if (!switchError) return;
    const t = window.setTimeout(() => {
      clearSwitchError();
      setSwitchError(null);
    }, 4000);
    return () => window.clearTimeout(t);
  }, [switchError]);

  function handleBusinessCreate() {
    if (!selectedWorkspace) {
      const name = window.prompt("Company name");
      if (!name?.trim()) return;
      void createAndSelectBusinessWorkspace(name.trim()).then(() => {
        openBusinessCreateOverlay();
      });
      return;
    }
    openBusinessCreateOverlay();
  }

  return (
    <div
      data-momentra-context={context}
      className="flex h-dvh min-h-0 flex-1 flex-col overflow-hidden"
      style={{
        background: tokens.colors.background,
        color: tokens.colors.textPrimary,
      }}
    >
      <div className="shrink-0">
        <MomentraTopBar
          user={user}
          businessMode={isBusiness}
          companyName={selectedWorkspace?.name ?? null}
          onCompanySwitcherClick={() => setShowCompanySwitcher(true)}
          showScanInviteButton={canScanInvite}
          onScanInviteClick={() => {
            void MomentraAnalytics.logCustomEvent("invite_scan_open", {
              app_context: context,
              source: "top_bar",
            });
            setShowScanInvite(true);
          }}
          onLife360Click={() => {
            void MomentraAnalytics.logCustomEvent("life360_open", {
              app_context: context,
              source: "top_bar",
            });
            setShowLife360(true);
          }}
          onSettingsClick={() => setShowSettings(true)}
          onNewMomentClick={() => {
            if (context === "personal") {
              void MomentraAnalytics.logCustomEvent("create_open", {
                app_context: context,
                source: "top_bar",
              });
              openPersonalCreateOverlay();
            } else if (context === "group") {
              void MomentraAnalytics.logCustomEvent("create_open", {
                app_context: context,
                source: "top_bar",
              });
              openGroupCreateOverlay();
            } else if (context === "business") {
              void MomentraAnalytics.logCustomEvent("create_open", {
                app_context: context,
                source: "top_bar",
              });
              handleBusinessCreate();
            } else if (context === "circle") {
              // Circle has no create engine — CTAs live on the Circle home empty/updated screens.
            } else {
              alert("Create moment — coming soon");
            }
          }}
        />
        <div className="h-px bg-white/10" />
        <MomentraContextSwitcher />
        <div className="h-px bg-white/10" />
        {switchError ? (
          <div
            role="status"
            className="px-4 py-2 text-center text-xs font-medium"
            style={{
              background: "rgba(180, 40, 40, 0.92)",
              color: "#fff",
            }}
          >
            {switchError}
          </div>
        ) : null}
      </div>

      <main className="relative flex min-h-0 flex-1 flex-col overflow-hidden">
        {(["personal", "group", "business", "circle"] as AppContext[]).map((ctx) =>
          mountedContexts.has(ctx) ? (
            <div
              key={ctx}
              className="absolute inset-0 flex min-h-0 flex-col transition-opacity duration-300"
              style={{
                opacity: context === ctx ? 1 : 0,
                pointerEvents: context === ctx ? "auto" : "none",
              }}
              aria-hidden={context !== ctx}
            >
              {children(ctx)}
            </div>
          ) : null,
        )}
      </main>

      <InviteQrScanModal
        open={showScanInvite}
        onClose={() => setShowScanInvite(false)}
        onJoined={(result) => {
          const biz = isBusinessMomentType(result.moment_type);
          setContext(biz ? "business" : "group");
          window.setTimeout(() => {
            if (biz) {
              openBusinessMomentAndPulse(
                result.moment_id,
                result.moment_type || "TEAM_OPERATIONS",
              );
            }
            dispatchInviteJoined(result);
          }, 50);
        }}
      />

      <CompanySwitcher
        open={isBusiness && showCompanySwitcher}
        onClose={() => setShowCompanySwitcher(false)}
        workspaces={workspaces}
        selectedId={selectedWorkspace?.id ?? businessSession.selectedWorkspaceId}
        onSelect={(id) => {
          void switchBusinessWorkspace(id);
        }}
        onNotifications={() => {
          alert("Company notifications — coming soon");
        }}
        onCompanySettings={() => {
          if (!selectedWorkspace) {
            setShowCompanySwitcher(true);
            return;
          }
          setShowCompanySettings(true);
        }}
        onOpenHome={(id) => {
          void (async () => {
            const current =
              selectedWorkspace?.id ?? businessSession.selectedWorkspaceId;
            if (id !== current) {
              await switchBusinessWorkspace(id);
            }
            setShowCompanyHome(true);
          })();
        }}
        onEditCompany={(id) => {
          void (async () => {
            const current =
              selectedWorkspace?.id ?? businessSession.selectedWorkspaceId;
            if (id !== current) {
              await switchBusinessWorkspace(id);
            }
            setShowCompanySettings(true);
          })();
        }}
        onDeleteCompany={(id) => {
          const ws = workspaces.find((w) => w.id === id);
          if (!ws || (ws.role || "").toUpperCase() !== "OWNER") return;
          if (
            !confirm(
              `Archive ${ws.name}? This hides the company for all members.`,
            )
          ) {
            return;
          }
          void (async () => {
            try {
              await updateBusinessWorkspace(id, { status: "ARCHIVED" });
              await softRefreshBusinessSession(
                selectedWorkspace?.id ?? businessSession.selectedWorkspaceId,
              );
            } catch {
              alert("Could not archive company");
            }
          })();
        }}
        onCreate={() => {
          const name = window.prompt("Company name");
          if (!name?.trim()) return;
          void createAndSelectBusinessWorkspace(name.trim());
        }}
        onJoin={() => setShowJoinCompany(true)}
      />

      <JoinCompanySheet
        open={isBusiness && showJoinCompany}
        onClose={() => setShowJoinCompany(false)}
        onJoined={(workspaceId) => {
          void switchBusinessWorkspace(workspaceId).then(() =>
            setShowCompanyHome(true),
          );
        }}
      />

      <CompanyHomeSheet
        open={isBusiness && showCompanyHome}
        onClose={() => setShowCompanyHome(false)}
        workspace={selectedWorkspace}
        dashboard={businessSession.bootstrap?.dashboard}
        moduleTiles={businessSession.bootstrap?.module_tiles}
        recentMoments={businessSession.bootstrap?.moments ?? []}
        onCreateMoment={() => {
          setShowCompanyHome(false);
          handleBusinessCreate();
        }}
        onInviteMember={() => {
          setShowCompanyHome(false);
          setShowCompanySettings(true);
        }}
        onOpenMoment={(momentId, typeCode) => {
          setShowCompanyHome(false);
          openBusinessMomentAndPulse(momentId, typeCode);
        }}
      />

      <CompanySettingsSheet
        open={isBusiness && showCompanySettings}
        onClose={() => setShowCompanySettings(false)}
        workspace={selectedWorkspace}
        onUpdated={() => {
          void softRefreshBusinessSession(
            selectedWorkspace?.id ?? businessSession.selectedWorkspaceId,
          );
        }}
      />

      <Life360Overlay open={showLife360} onClose={() => setShowLife360(false)} />

      {showSettings && user ? (
        <SettingsSheet
          user={user}
          isLoading={isLoading}
          onClose={() => setShowSettings(false)}
          onSignOut={() => {
            setShowSettings(false);
            logout();
          }}
          onUserUpdated={setUser}
          onViewIntro={() => {
            void MomentraAnalytics.logCustomEvent("onboarding_replay_open");
            setShowSettings(false);
            setShowOnboardingReplay(true);
          }}
        />
      ) : null}

      {showOnboardingReplay ? (
        <OnboardingScreen
          mode="replay"
          onFinished={() => setShowOnboardingReplay(false)}
        />
      ) : null}
    </div>
  );
}

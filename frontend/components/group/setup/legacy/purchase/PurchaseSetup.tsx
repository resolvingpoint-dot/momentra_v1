"use client";

/**
 * @deprecated Quarantined legacy Shared Purchase wizard (GroupSetupShell + step APIs).
 * Production uses SharedPurchaseSetup → GuidedSetupShell (Phase 2B).
 */
import { useState } from "react";
import { GroupSetupShell } from "@/components/group/setup/legacy/shared/GroupSetupShell";
import { PurchaseTypeSelect } from "@/components/group/setup/legacy/purchase/PurchaseTypeSelect";
import { PurchaseBasics } from "@/components/group/setup/legacy/purchase/PurchaseBasics";
import { PurchaseContributors } from "@/components/group/setup/legacy/purchase/PurchaseContributors";
import { PurchaseReview } from "@/components/group/setup/legacy/purchase/PurchaseReview";
import { setupBasics, setupPeople, activateMoment } from "@/lib/api/group";
import type { ProfileOption } from "@/lib/api/group";

type SetupStep = "type" | "basics" | "contributors" | "review";

type PurchaseSetupProps = {
  profiles: ProfileOption[];
  onClose: () => void;
  onComplete: (momentId: string) => void;
};

export function PurchaseSetup({ profiles, onClose, onComplete }: PurchaseSetupProps) {
  const [step, setStep] = useState<SetupStep>("type");
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null);
  const [basicsData, setBasicsData] = useState<any>(null);
  const [contributorsData, setContributorsData] = useState<Array<{ display_name: string; role_code: string; contribution_amount?: number }>>([]);
  const [momentId, setMomentId] = useState<string | null>(null);

  const handleSelectProfile = (profileCode: string) => {
    setSelectedProfile(profileCode);
  };

  const handleContinueType = () => {
    if (selectedProfile) {
      setStep("basics");
    }
  };

  const handleContinueBasics = (data: any) => {
    setBasicsData(data);
    setStep("contributors");
  };

  const handleContinueContributors = (contributors: Array<{ display_name: string; role_code: string; contribution_amount?: number }>) => {
    setContributorsData(contributors);
    setStep("review");
  };

  const handleBack = () => {
    switch (step) {
      case "basics":
        setStep("type");
        break;
      case "contributors":
        setStep("basics");
        break;
      case "review":
        setStep("contributors");
        break;
    }
  };

  const handleActivate = async () => {
    try {
      if (!selectedProfile) return;
      const basicsResult = await setupBasics("SHARED_PURCHASE", {
        moment_name: basicsData?.moment_name || "",
        detail_fields: {
          profile_code: selectedProfile,
          ...basicsData?.detail_fields,
        },
      });
      const newMomentId = basicsResult.moment_id;
      setMomentId(newMomentId);

      if (contributorsData.length > 0) {
        await setupPeople("SHARED_PURCHASE", newMomentId, { members: contributorsData });
      }

      await activateMoment(newMomentId, { activate: true });
      onComplete(newMomentId);
    } catch (error) {
      console.error("Error activating purchase:", error);
    }
  };

  const getStepTitle = () => {
    switch (step) {
      case "type":
        return "Choose Purchase Type";
      case "basics":
        return "Purchase Details";
      case "contributors":
        return "Add Contributors";
      case "review":
        return "Review & Activate";
    }
  };

  const getStepSubtitle = () => {
    switch (step) {
      case "type":
        return "Select the type of shared purchase";
      case "basics":
        return "Tell us about your purchase";
      case "contributors":
        return "Invite people to contribute";
      case "review":
        return "Review before activating";
    }
  };

  const renderStep = () => {
    switch (step) {
      case "type":
        return (
          <PurchaseTypeSelect
            profiles={profiles}
            selectedProfile={selectedProfile}
            onSelectProfile={handleSelectProfile}
            onContinue={handleContinueType}
          />
        );
      case "basics":
        return (
          <PurchaseBasics
            initialData={basicsData}
            onContinue={handleContinueBasics}
            onBack={handleBack}
          />
        );
      case "contributors":
        return (
          <PurchaseContributors
            initialContributors={contributorsData}
            onContinue={handleContinueContributors}
            onBack={handleBack}
          />
        );
      case "review":
        return (
          <PurchaseReview
            data={{
              moment_name: basicsData?.moment_name || "",
              target_amount: basicsData?.detail_fields?.target_amount,
              target_date: basicsData?.detail_fields?.target_date,
              purchase_link: basicsData?.detail_fields?.purchase_link,
              description: basicsData?.detail_fields?.description,
              contributors: contributorsData,
            }}
            onActivate={handleActivate}
            onBack={handleBack}
          />
        );
    }
  };

  return (
    <GroupSetupShell
      step={
        step === "type" ? 1 :
        step === "basics" ? 2 :
        step === "contributors" ? 3 : 4
      }
      totalSteps={4}
      title={getStepTitle()}
      subtitle={getStepSubtitle()}
      onBack={step !== "type" ? handleBack : undefined}
      onClose={onClose}
    >
      {renderStep()}
    </GroupSetupShell>
  );
}
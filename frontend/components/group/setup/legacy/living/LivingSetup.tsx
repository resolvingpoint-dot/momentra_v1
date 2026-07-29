"use client";

/**
 * @deprecated Alternate create-time wizard. Production reopen uses SharedLivingSetup
 * (`GroupLivingSetup.tsx`) on GuidedSetupShell.
 */
import { useState } from "react";
import { GroupSetupShell } from "@/components/group/setup/legacy/shared/GroupSetupShell";
import { LivingTypeSelect } from "@/components/group/setup/legacy/living/LivingTypeSelect";
import { LivingBasics } from "@/components/group/setup/legacy/living/LivingBasics";
import { LivingResidents } from "@/components/group/setup/legacy/living/LivingResidents";
import { LivingReview } from "@/components/group/setup/legacy/living/LivingReview";
import { setupBasics, setupPeople, activateMoment } from "@/lib/api/group";
import type { ProfileOption } from "@/lib/api/group";

type SetupStep = "type" | "basics" | "residents" | "review";

type LivingSetupProps = {
  profiles: ProfileOption[];
  onClose: () => void;
  onComplete: (momentId: string) => void;
};

export function LivingSetup({ profiles, onClose, onComplete }: LivingSetupProps) {
  const [step, setStep] = useState<SetupStep>("type");
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null);
  const [basicsData, setBasicsData] = useState<any>(null);
  const [residentsData, setResidentsData] = useState<Array<{ display_name: string; role_code: string; resident_type?: string }>>([]);
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
    setStep("residents");
  };

  const handleContinueResidents = (residents: Array<{ display_name: string; role_code: string; resident_type?: string }>) => {
    setResidentsData(residents);
    setStep("review");
  };

  const handleBack = () => {
    switch (step) {
      case "basics":
        setStep("type");
        break;
      case "residents":
        setStep("basics");
        break;
      case "review":
        setStep("residents");
        break;
    }
  };

  const handleActivate = async () => {
    try {
      if (!selectedProfile) return;
      const basicsResult = await setupBasics("SHARED_LIVING", {
        moment_name: basicsData?.moment_name || "",
        detail_fields: {
          profile_code: selectedProfile,
          ...basicsData?.detail_fields,
        },
      });
      const newMomentId = basicsResult.moment_id;
      setMomentId(newMomentId);

      if (residentsData.length > 0) {
        await setupPeople("SHARED_LIVING", newMomentId, { members: residentsData });
      }

      await activateMoment(newMomentId, { activate: true });
      onComplete(newMomentId);
    } catch (error) {
      console.error("Error activating living arrangement:", error);
    }
  };

  const getStepTitle = () => {
    switch (step) {
      case "type":
        return "Choose Living Type";
      case "basics":
        return "Living Details";
      case "residents":
        return "Add Residents";
      case "review":
        return "Review & Activate";
    }
  };

  const getStepSubtitle = () => {
    switch (step) {
      case "type":
        return "Select the type of shared living arrangement";
      case "basics":
        return "Tell us about your living arrangement";
      case "residents":
        return "Invite residents to join";
      case "review":
        return "Review before activating";
    }
  };

  const renderStep = () => {
    switch (step) {
      case "type":
        return (
          <LivingTypeSelect
            profiles={profiles}
            selectedProfile={selectedProfile}
            onSelectProfile={handleSelectProfile}
            onContinue={handleContinueType}
          />
        );
      case "basics":
        return (
          <LivingBasics
            initialData={basicsData}
            onContinue={handleContinueBasics}
            onBack={handleBack}
          />
        );
      case "residents":
        return (
          <LivingResidents
            initialResidents={residentsData}
            onContinue={handleContinueResidents}
            onBack={handleBack}
          />
        );
      case "review":
        return (
          <LivingReview
            data={{
              moment_name: basicsData?.moment_name || "",
              address: basicsData?.detail_fields?.address,
              move_in_date: basicsData?.detail_fields?.move_in_date,
              description: basicsData?.detail_fields?.description,
              residents: residentsData,
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
        step === "residents" ? 3 : 4
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
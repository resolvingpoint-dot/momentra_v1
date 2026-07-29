/**
 * @deprecated Quarantined legacy Shared Experience wizard (GroupSetupShell).
 * Production uses SharedExperienceSetup → GuidedSetupShell (Phase 2A).
 */
"use client";

/**
 * @deprecated Quarantined legacy Shared Experience wizard (GroupSetupShell).
 * Production uses SharedExperienceSetup → GuidedSetupShell (Phase 2A).
 * Alternate create-time path only — do not wire from Group home.
 */
import { useState } from "react";
import { GroupSetupShell } from "@/components/group/setup/legacy/shared/GroupSetupShell";
import { ExperienceTypeSelect } from "@/components/group/setup/legacy/experience/ExperienceTypeSelect";
import { ExperienceBasics } from "@/components/group/setup/legacy/experience/ExperienceBasics";
import { ExperiencePeople } from "@/components/group/setup/legacy/experience/ExperiencePeople";
import { ExperienceReview } from "@/components/group/setup/legacy/experience/ExperienceReview";
import { setupBasics, setupPeople, activateMoment } from "@/lib/api/group";
import type { ProfileOption } from "@/lib/api/group";

type SetupStep = "type" | "basics" | "people" | "review";

type ExperienceSetupProps = {
  profiles: ProfileOption[];
  onClose: () => void;
  onComplete: (momentId: string) => void;
};

export function ExperienceSetup({ profiles, onClose, onComplete }: ExperienceSetupProps) {
  const [step, setStep] = useState<SetupStep>("type");
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null);
  const [basicsData, setBasicsData] = useState<any>(null);
  const [peopleData, setPeopleData] = useState<Array<{ display_name: string; role_code: string }>>([]);
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
    setStep("people");
  };

  const handleContinuePeople = (members: Array<{ display_name: string; role_code: string }>) => {
    setPeopleData(members);
    setStep("review");
  };

  const handleBack = () => {
    switch (step) {
      case "basics":
        setStep("type");
        break;
      case "people":
        setStep("basics");
        break;
      case "review":
        setStep("people");
        break;
    }
  };

  const handleActivate = async () => {
    try {
      if (!selectedProfile) return;
      const basicsResult = await setupBasics("SHARED_EXPERIENCE", {
        moment_name: basicsData?.moment_name || "",
        detail_fields: {
          profile_code: selectedProfile,
          ...basicsData?.detail_fields,
        },
      });
      const newMomentId = basicsResult.moment_id;
      setMomentId(newMomentId);

      if (peopleData.length > 0) {
        await setupPeople("SHARED_EXPERIENCE", newMomentId, { members: peopleData });
      }

      await activateMoment(newMomentId, { activate: true });
      onComplete(newMomentId);
    } catch (error) {
      console.error("Error activating experience:", error);
    }
  };

  const getStepTitle = () => {
    switch (step) {
      case "type":
        return "Choose Experience Type";
      case "basics":
        return "Experience Details";
      case "people":
        return "Add People";
      case "review":
        return "Review & Activate";
    }
  };

  const getStepSubtitle = () => {
    switch (step) {
      case "type":
        return "Select the type of shared experience";
      case "basics":
        return "Tell us about your experience";
      case "people":
        return "Invite people to join";
      case "review":
        return "Review before activating";
    }
  };

  const renderStep = () => {
    switch (step) {
      case "type":
        return (
          <ExperienceTypeSelect
            profiles={profiles}
            selectedProfile={selectedProfile}
            onSelectProfile={handleSelectProfile}
            onContinue={handleContinueType}
          />
        );
      case "basics":
        return (
          <ExperienceBasics
            initialData={basicsData}
            onContinue={handleContinueBasics}
            onBack={handleBack}
          />
        );
      case "people":
        return (
          <ExperiencePeople
            initialMembers={peopleData}
            onContinue={handleContinuePeople}
            onBack={handleBack}
          />
        );
      case "review":
        return (
          <ExperienceReview
            data={{
              moment_name: basicsData?.moment_name || "",
              location: basicsData?.detail_fields?.location,
              start_date: basicsData?.detail_fields?.start_date,
              end_date: basicsData?.detail_fields?.end_date,
              description: basicsData?.detail_fields?.description,
              members: peopleData,
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
        step === "people" ? 3 : 4
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

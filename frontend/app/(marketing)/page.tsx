import Hero from "@/components/marketing/sections/Hero";
import OneRealMoment from "@/components/marketing/sections/OneRealMoment";
import LifeJourney from "@/components/marketing/sections/LifeJourney";
import WhatIsAMoment from "@/components/marketing/sections/WhatIsAMoment";
import ScatteredToMomentra from "@/components/marketing/sections/ScatteredToMomentra";
import WorldsTabs from "@/components/marketing/sections/WorldsTabs";
import Intelligence from "@/components/marketing/sections/Intelligence";
import SharedArchitecture from "@/components/marketing/sections/SharedArchitecture";
import Philosophy from "@/components/marketing/sections/Philosophy";
import Flywheel from "@/components/marketing/sections/Flywheel";
import BookBridge from "@/components/marketing/sections/BookBridge";
import FinalCTA from "@/components/marketing/sections/FinalCTA";

export default function MarketingHome() {
  return (
    <main className="relative">
      <Hero />
      <OneRealMoment />
      <LifeJourney />
      <WhatIsAMoment />
      <ScatteredToMomentra />
      <WorldsTabs />
      <Intelligence />
      <SharedArchitecture />
      <Philosophy />
      <Flywheel />
      <BookBridge />
      <FinalCTA />
    </main>
  );
}

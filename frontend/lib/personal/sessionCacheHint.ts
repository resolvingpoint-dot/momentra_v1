import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import {
  memoryHasTypePayload,
  momentsHasTypePayload,
  pulseHasTypePayload,
} from "@/components/personal/shared/personalMomentRouting";
import type {
  PersonalMemoryResponse,
  PersonalMomentsHomeResponse,
  PersonalPulseResponse,
  TemplateMemoryResponse,
  TemplateMomentsResponse,
} from "@/lib/api/personal";
import {
  loadMemoryFromDisk,
  loadMomentsFromDisk,
  loadPulseFromDisk,
  loadTemplateMemoryFromDisk,
  loadTemplateMomentsFromDisk,
} from "@/stores/personalSessionStore";

export function hasTypeSessionCacheHint(
  typeCode: PersonalMomentTypeCode,
  sources: {
    pulse?: PersonalPulseResponse | null;
    moments?: PersonalMomentsHomeResponse | null;
    memory?: PersonalMemoryResponse | null;
    templateMoments?: TemplateMomentsResponse | null;
    templateMemory?: TemplateMemoryResponse | null;
  } = {},
): boolean {
  const pulse = sources.pulse ?? loadPulseFromDisk(typeCode);
  if (pulse && pulseHasTypePayload(pulse, typeCode)) return true;

  const moments = sources.moments ?? loadMomentsFromDisk(typeCode);
  if (moments && momentsHasTypePayload(moments, typeCode)) return true;

  const memory = sources.memory ?? loadMemoryFromDisk(typeCode);
  if (memory && memoryHasTypePayload(memory, typeCode)) return true;

  const templateMoments = sources.templateMoments ?? loadTemplateMomentsFromDisk(typeCode);
  if (templateMoments?.moment_projection) return true;

  const templateMemory = sources.templateMemory ?? loadTemplateMemoryFromDisk(typeCode);
  if (templateMemory?.memory_projection) return true;

  return false;
}

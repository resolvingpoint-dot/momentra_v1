"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Camera, Loader2, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { acceptInvite } from "@/lib/api/group";
import { extractInviteToken } from "@/lib/invite/inviteToken";
import type { InviteAcceptResult } from "@/lib/api/group";

type InviteQrScanModalProps = {
  open: boolean;
  onClose: () => void;
  onJoined: (result: InviteAcceptResult) => void;
};

type BarcodeDetectorLike = {
  detect: (source: ImageBitmapSource) => Promise<Array<{ rawValue?: string }>>;
};

function getBarcodeDetector(): BarcodeDetectorLike | null {
  if (typeof window === "undefined") return null;
  const Ctor = (window as unknown as { BarcodeDetector?: new (opts: { formats: string[] }) => BarcodeDetectorLike })
    .BarcodeDetector;
  if (!Ctor) return null;
  try {
    return new Ctor({ formats: ["qr_code"] });
  } catch {
    return null;
  }
}

export function InviteQrScanModal({ open, onClose, onJoined }: InviteQrScanModalProps) {
  const { colors } = useThemeTokens();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const scanningRef = useRef(false);
  const [paste, setPaste] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraSkipped, setCameraSkipped] = useState(false);

  const stopCamera = useCallback(() => {
    scanningRef.current = false;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraReady(false);
  }, []);

  const joinWithRaw = useCallback(
    async (raw: string) => {
      const token = extractInviteToken(raw);
      if (!token) {
        setError("Could not read an invite from that code or link.");
        return;
      }
      setBusy(true);
      setError(null);
      setStatus("Joining…");
      try {
        const result = await acceptInvite(token);
        setStatus(
          result.already_member
            ? `Already a member of ${result.moment_name}`
            : `Joined ${result.moment_name}`,
        );
        onJoined(result);
        window.setTimeout(() => onClose(), 600);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not accept invite");
        setStatus(null);
        scanningRef.current = true;
      } finally {
        setBusy(false);
      }
    },
    [onClose, onJoined],
  );

  useEffect(() => {
    if (!open) {
      stopCamera();
      setPaste("");
      setError(null);
      setStatus(null);
      setCameraSkipped(false);
      return;
    }

    let cancelled = false;
    const detector = getBarcodeDetector();

    async function start() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCameraSkipped(true);
        setStatus("Camera not available in this browser — paste an invite link below.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        const video = videoRef.current;
        if (!video) return;
        video.srcObject = stream;
        await video.play();
        setCameraReady(true);

        if (!detector) {
          setStatus(
            "Live QR decode needs Chrome/Edge. Camera is on — or paste an invite link below.",
          );
          return;
        }

        setStatus("Point at an invite QR code");
        scanningRef.current = true;

        const tick = async () => {
          if (!scanningRef.current || cancelled || busy) {
            if (scanningRef.current && !cancelled) requestAnimationFrame(() => void tick());
            return;
          }
          try {
            if (video.readyState >= 2) {
              const codes = await detector.detect(video);
              const raw = codes[0]?.rawValue;
              if (raw) {
                scanningRef.current = false;
                stopCamera();
                await joinWithRaw(raw);
                return;
              }
            }
          } catch {
            /* keep scanning */
          }
          if (scanningRef.current && !cancelled) {
            requestAnimationFrame(() => void tick());
          }
        };
        requestAnimationFrame(() => void tick());
      } catch {
        setCameraSkipped(true);
        setStatus("Camera unavailable — paste an invite link below.");
      }
    }

    void start();
    return () => {
      cancelled = true;
      stopCamera();
    };
  }, [open, stopCamera, joinWithRaw, busy]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[90] flex items-end justify-center bg-black/55 p-4 sm:items-center"
      role="dialog"
      aria-modal
      aria-labelledby="invite-scan-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-3xl p-5 shadow-xl"
        style={{ background: colors.surface, color: colors.textPrimary }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-center justify-between gap-2">
          <h3 id="invite-scan-title" className="text-lg font-semibold">
            Scan to join
          </h3>
          <button
            type="button"
            aria-label="Close"
            className="rounded-full p-2"
            style={{ background: colors.surfaceContainer }}
            onClick={onClose}
          >
            <X className="size-4" />
          </button>
        </div>
        <p className="mb-3 text-sm" style={{ color: colors.textSecondary }}>
          Scan a Group or Business invite QR, or paste the invite link.
        </p>

        <div
          className="relative mb-3 overflow-hidden rounded-2xl"
          style={{ background: "#111", aspectRatio: "3 / 4", maxHeight: 320 }}
        >
          <video
            ref={videoRef}
            className="h-full w-full object-cover"
            playsInline
            muted
            autoPlay
          />
          {!cameraReady ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white/80">
              <Camera className="size-8 opacity-70" />
              <span className="text-xs px-4 text-center">
                {cameraSkipped ? "Camera unavailable" : "Starting camera…"}
              </span>
            </div>
          ) : null}
        </div>

        {status ? (
          <p className="mb-2 text-sm" style={{ color: colors.textSecondary }}>
            {status}
          </p>
        ) : null}
        {error ? (
          <p className="mb-2 text-sm" style={{ color: colors.error }}>
            {error}
          </p>
        ) : null}

        <label className="mb-1 block text-xs font-medium" style={{ color: colors.textSecondary }}>
          Invite link or code
        </label>
        <div className="flex gap-2">
          <input
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            placeholder="momentra://invite/…"
            className="min-w-0 flex-1 rounded-xl px-3 py-2.5 text-sm outline-none"
            style={{ background: colors.surfaceContainer, color: colors.textPrimary }}
          />
          <button
            type="button"
            disabled={busy || !paste.trim()}
            className="inline-flex items-center gap-1 rounded-xl px-3 py-2.5 text-sm font-semibold disabled:opacity-50"
            style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            onClick={() => void joinWithRaw(paste)}
          >
            {busy ? <Loader2 className="size-4 animate-spin" /> : null}
            Join
          </button>
        </div>
      </div>
    </div>
  );
}

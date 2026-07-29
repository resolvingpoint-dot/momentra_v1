"use client";

import { useEffect, useMemo, useState } from "react";

type AvatarPhotoEditorProps = {
  file: File;
  isUploading: boolean;
  uploadError: string | null;
  onCancel: () => void;
  onConfirm: (rotationDegrees: number) => void;
};

export function AvatarPhotoEditor({
  file,
  isUploading,
  uploadError,
  onCancel,
  onConfirm,
}: AvatarPhotoEditorProps) {
  const [rotationDegrees, setRotationDegrees] = useState(0);
  const previewUrl = useMemo(() => URL.createObjectURL(file), [file]);

  useEffect(() => {
    return () => URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  function rotateLeft() {
    setRotationDegrees((d) => (d - 90 + 360) % 360);
  }

  function rotateRight() {
    setRotationDegrees((d) => (d + 90) % 360);
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center bg-black/50 sm:items-center">
      <div className="max-h-[90vh] w-full max-w-sm overflow-y-auto rounded-t-2xl bg-white p-6 text-indigo-900 sm:rounded-2xl">
        <h2 className="text-lg font-semibold">Edit photo</h2>
        <p className="mt-1 text-sm text-indigo-700/80">
          Photo is optimized automatically (square, up to 2 MB)
        </p>

        <div className="mt-6 flex flex-col items-center gap-4">
          <div className="size-40 overflow-hidden rounded-full bg-indigo-50">
            <img
              src={previewUrl}
              alt="Avatar preview"
              className="size-full object-cover"
              style={{ transform: `rotate(${rotationDegrees}deg)` }}
            />
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              className="rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-800 disabled:opacity-60"
              disabled={isUploading}
              onClick={rotateLeft}
              aria-label="Rotate left"
            >
              ↺ Rotate left
            </button>
            <button
              type="button"
              className="rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-800 disabled:opacity-60"
              disabled={isUploading}
              onClick={rotateRight}
              aria-label="Rotate right"
            >
              Rotate right ↻
            </button>
          </div>

          {uploadError ? <p className="text-sm text-red-600">{uploadError}</p> : null}

          <button
            type="button"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            disabled={isUploading}
            onClick={() => onConfirm(rotationDegrees)}
          >
            {isUploading ? "Uploading…" : "Use photo"}
          </button>
          <button
            type="button"
            className="btn-ghost w-full"
            disabled={isUploading}
            onClick={onCancel}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

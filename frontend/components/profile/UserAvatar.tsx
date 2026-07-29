"use client";

import { useEffect, useState } from "react";
import { profileInitial } from "@/lib/profileInitials";
import { brandTokens } from "@/lib/brandTokens";

type UserAvatarProps = {
  photoUrl?: string | null;
  displayName?: string | null;
  email?: string | null;
  size?: number;
  className?: string;
  onClick?: () => void;
};

export function UserAvatar({
  photoUrl,
  displayName,
  email,
  size = 40,
  className = "",
  onClick,
}: UserAvatarProps) {
  const [imageFailed, setImageFailed] = useState(false);
  const initial = profileInitial(displayName, email);
  const showImage = Boolean(photoUrl) && !imageFailed;

  useEffect(() => {
    setImageFailed(false);
  }, [photoUrl]);

  const content = showImage ? (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      key={photoUrl ?? "no-photo"}
      src={photoUrl!}
      alt=""
      className="h-full w-full object-cover"
      onError={() => setImageFailed(true)}
    />
  ) : (
    <span
      className="flex h-full w-full items-center justify-center font-semibold text-white"
      style={{ fontSize: Math.round(size * 0.38) }}
    >
      {initial}
    </span>
  );

  const sharedClass = `shrink-0 overflow-hidden rounded-full border border-white/20 ${className}`;

  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        aria-label="Account settings"
        className={`${sharedClass} bg-white/10`}
        style={{ width: size, height: size }}
      >
        {content}
      </button>
    );
  }

  return (
    <div
      className={sharedClass}
      style={{
        width: size,
        height: size,
        background: showImage ? undefined : brandTokens.indigo500,
      }}
      aria-hidden={!onClick}
    >
      {content}
    </div>
  );
}

import { useEffect, useState } from "react";
import { Icon } from "./Icon";

interface Props { src: string; fallback?: string; alt: string; className?: string; ratio?: string; priority?: boolean; category?: string }

/** Image with skeleton while loading, a fallback image if the source fails, and an icon if both fail.
 *  The fixed aspect ratio reserves space, so nothing jumps when the image arrives. */
export default function ProductImage({ src, fallback, alt, className = "", ratio = "4 / 3", priority, category }: Props) {
  const [cur, setCur] = useState(src);
  const [state, setState] = useState<"loading" | "ok" | "failed">("loading");
  useEffect(() => { setCur(src); setState("loading"); }, [src]);
  const onError = () => {
    if (fallback && cur !== fallback) { setCur(fallback); setState("loading"); } else setState("failed");
  };
  return (
    <div className={`relative overflow-hidden ${className}`} style={{ aspectRatio: ratio }}>
      {state === "loading" && <div className="skeleton absolute inset-0" aria-hidden="true" />}
      {state === "failed" ? (
        <div role="img" aria-label={alt} className="absolute inset-0 flex items-center justify-center bg-slate-100 text-slate-400">
          <Icon name={category === "Laptop" ? "Laptop" : "Smartphone"} className="h-1/3 w-1/3" />
        </div>
      ) : (
        <img src={cur} alt={alt} width={400} height={300} loading={priority ? "eager" : "lazy"} decoding="async"
          onLoad={() => setState("ok")} onError={onError}
          className={`h-full w-full object-contain transition-opacity duration-300 ${state === "ok" ? "opacity-100" : "opacity-0"}`} />
      )}
    </div>
  );
}

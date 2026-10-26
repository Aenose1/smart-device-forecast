import { useState, type ReactNode } from "react";
import { ApiError, downloadFile } from "../api";

/** Looks like the original link/button but downloads through fetch, so the anonymous visitor id / admin key headers are sent. */
export default function DownloadLink({ path, className, children }: { path: string; className?: string; children: ReactNode }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const go = async () => {
    setBusy(true); setErr("");
    try { await downloadFile(path); } catch (e) { setErr(e instanceof ApiError ? e.message : "Download failed. Please try again."); } finally { setBusy(false); }
  };
  return (
    <>
      <button type="button" className={className} onClick={go} disabled={busy} aria-busy={busy}>{children}</button>
      {err && <span role="alert" className="ml-2 text-xs text-red-700">{err}</span>}
    </>
  );
}

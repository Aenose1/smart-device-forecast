import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { adminKey, api } from "../api";
import { Icon } from "./Icon";
import { ErrorBox, Notice, Spinner } from "./ui";

type Status = { mode: "key" | "open" | "disabled"; authorized: boolean };

/** Guards the Administration pages. Normal visitors never see this: it is not a user login, only a key check for the
 *  operations that change datasets, models and devices. The key is checked by the server on every admin request. */
export default function AdminGate({ children }: { children: ReactNode }) {
  const [st, setSt] = useState<Status | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [key, setKey] = useState(""), [rejected, setRejected] = useState(false), [busy, setBusy] = useState(false);

  const check = () => api.admin.status().then((s) => { setSt(s); return s; }).catch((e) => { setError(e); return null; });
  useEffect(() => { void check(); }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault(); setBusy(true); setRejected(false);
    adminKey.set(key.trim());
    const s = await check();
    if (s && !s.authorized) { adminKey.clear(); setRejected(true); }
    setBusy(false);
  };

  if (error) return <ErrorBox error={error} />;
  if (!st) return <Spinner />;
  if (st.authorized) {
    return (
      <>
        {st.mode === "open" && <div className="mb-4"><Notice>Demo mode: administration is open without a key. This is only allowed on a local computer, never on a public server.</Notice></div>}
        {st.mode === "key" && (
          <div className="mb-4 flex justify-end"><button className="btn" onClick={() => { adminKey.clear(); setSt({ ...st, authorized: false }); }}><Icon name="Lock" className="h-4 w-4" />Lock administration</button></div>
        )}
        {children}
      </>
    );
  }
  if (st.mode === "disabled") {
    return (
      <div className="mx-auto max-w-xl"><Notice>
        Administration is turned off on this server because no administrator key is configured. Everything else on the site works normally.
        The site owner can enable it by setting <code>ADMIN_API_KEY</code> on the backend.
      </Notice></div>
    );
  }
  return (
    <form onSubmit={submit} className="card mx-auto max-w-md space-y-4 p-6">
      <h1 className="text-xl font-semibold"><Icon name="Lock" className="mr-2 inline h-5 w-5 text-indigo-600" />Administration</h1>
      <p className="text-sm text-muted">These pages change datasets, models and devices, so they need the administrator key set on the server. Regular features do not need it.</p>
      {rejected && <div role="alert" className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">That key was not accepted.</div>}
      <div><label className="label" htmlFor="adminkey">Administrator key</label>
        <input id="adminkey" name="adminkey" className="input" type="password" autoComplete="off" required value={key} onChange={(e) => setKey(e.target.value)} /></div>
      <button type="submit" className="btn btn-primary w-full" disabled={busy}>{busy ? "Checking…" : "Unlock administration"}</button>
    </form>
  );
}

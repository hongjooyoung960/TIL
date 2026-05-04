const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

/** Full URL for an API path. Uses `VITE_API_URL` when set (production build); otherwise relative URLs (dev + Vite proxy). */
export function apiUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const p = path.startsWith("/") ? path : `/${path}`;
  return API_BASE ? `${API_BASE}${p}` : p;
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail))
      return data.detail.map((d: { msg?: string }) => d.msg ?? "").join("; ");
    return JSON.stringify(data);
  } catch {
    return res.statusText;
  }
}

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

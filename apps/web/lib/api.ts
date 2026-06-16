// Thin client for the FastAPI backend. The frontend only ever needs the API URL — never the
// Anthropic key, database URL, or AWS credentials (those live exclusively in apps/api).

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // non-JSON error body; fall back to statusText
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export type Health = { status: string; service: string };
export type Ping = { message: string };

export const fetchHealth = () => getJSON<Health>("/health");
export const fetchPing = () => getJSON<Ping>("/ping");

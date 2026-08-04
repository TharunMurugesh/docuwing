const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const api = async <T>(path: string, init: RequestInit = {}): Promise<T> => {
  const token = typeof window === "undefined" ? "" : localStorage.getItem("token") || "";
  const response = await fetch(`${base}/v1${path}`, { ...init, headers: { Authorization: token ? `Bearer ${token}` : "", ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...init.headers } });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
};

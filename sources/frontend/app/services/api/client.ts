import { ApiError } from "./errors";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8800";

export interface ApiFetchOptions {
  url: string;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD";
  params?: Record<string, unknown>;
  data?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  responseType?: "json" | "blob" | "text";
}

function buildUrl(path: string, params?: Record<string, unknown>): string {
  const url = path.startsWith("http") ? new URL(path) : new URL(path, BASE_URL);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined || value === null) continue;
      if (Array.isArray(value)) {
        for (const item of value) url.searchParams.append(key, stringifyParam(item));
      } else {
        url.searchParams.set(key, stringifyParam(value));
      }
    }
  }
  return url.toString();
}

function stringifyParam(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean" || typeof value === "bigint") {
    return String(value);
  }
  return JSON.stringify(value);
}

function isFormData(body: unknown): body is FormData {
  return typeof FormData !== "undefined" && body instanceof FormData;
}

function isUrlSearchParams(body: unknown): body is URLSearchParams {
  return typeof URLSearchParams !== "undefined" && body instanceof URLSearchParams;
}

export async function apiFetch<T>(options: ApiFetchOptions): Promise<T> {
  const { url, method, params, data, headers, signal, responseType = "json" } = options;
  const finalUrl = buildUrl(url, params);

  const isFormLike = isFormData(data) || isUrlSearchParams(data);
  const init: RequestInit = {
    method,
    credentials: "include",
    signal,
    headers: {
      Accept: "application/json",
      ...(data !== undefined && !isFormLike ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
  };

  if (data !== undefined) {
    init.body = isFormLike ? (data as BodyInit) : JSON.stringify(data);
  }

  let response: Response;
  try {
    response = await fetch(finalUrl, init);
  } catch {
    throw new ApiError({
      type: "UNKNOWN",
      on: "UNKNOWN",
      title: "Network error",
      detail: "Could not reach the server. Check your connection.",
      status: 0,
    });
  }

  if (!response.ok) {
    throw await ApiError.fromResponse(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (responseType === "blob") return (await response.blob()) as unknown as T;
  if (responseType === "text") return (await response.text()) as unknown as T;
  return (await response.json()) as T;
}

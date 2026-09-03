/**
 * Real API client for the VerifyNow FastAPI backend.
 *
 * No mock data, no local scoring, no fabricated results: every value shown
 * to the user comes directly from what the backend returns.
 */

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://localhost:8000";

export type BackendContentType = "text" | "url" | "document" | "image" | "video_url";
export type RequestStatus = "pending" | "processing" | "completed" | "failed";
export type Verdict = "VERIFIED" | "FALSE" | "MISLEADING" | "UNCERTAIN";
export type EvidenceStance = "supports" | "refutes" | "context";

export interface EvidenceItem {
  claim: string;
  stance: EvidenceStance;
  source_name: string;
  source_url: string;
  published_date: string | null;
  excerpt: string | null;
}

export interface WebsiteMetadata {
  domain: string | null;
  site_name: string | null;
  about: string | null;
  founding_or_launch_date: string | null;
  founder_or_organization: string | null;
  company_info: string | null;
  claims_made_by_site: string[];
  independently_verified_claims: string[];
}

export interface AIGeneratedSignal {
  likely_ai_generated: boolean | null;
  note: string | null;
}

export interface VerificationResult {
  request_id: string;
  content_type: BackendContentType;
  status: RequestStatus;
  input_summary: string;
  verdict: Verdict | null;
  confidence: number | null;
  reasoning: string | null;
  content_published_date: string | null;
  website_metadata: WebsiteMetadata | null;
  ai_generated_signal: AIGeneratedSignal | null;
  evidence: EvidenceItem[];
  limitations: string | null;
  error_message: string | null;
  from_cache: boolean;
  created_at: string;
  updated_at: string;
}

export interface HistoryItem {
  request_id: string;
  content_type: BackendContentType;
  status: RequestStatus;
  input_summary: string;
  verdict: Verdict | null;
  confidence: number | null;
  created_at: string;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
    return JSON.stringify(body?.detail ?? body);
  } catch {
    return res.statusText || `Request failed with status ${res.status}`;
  }
}

export interface SubmitVerificationInput {
  contentType: BackendContentType;
  text?: string;
  file?: File;
}

export async function submitVerification(
  input: SubmitVerificationInput
): Promise<{ request_id: string; status: RequestStatus; from_cache: boolean }> {
  const form = new FormData();
  form.append("content_type", input.contentType);
  if (input.text) form.append("text", input.text);
  if (input.file) form.append("file", input.file);

  const res = await fetch(`${API_BASE_URL}/api/verify`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new ApiError(res.status, await parseErrorDetail(res));
  }
  return res.json();
}

export async function getVerificationResult(requestId: string): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE_URL}/api/verify/${requestId}`);
  if (!res.ok) {
    throw new ApiError(res.status, await parseErrorDetail(res));
  }
  return res.json();
}

export async function getHistory(limit = 20): Promise<HistoryItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/history?limit=${limit}`);
  if (!res.ok) {
    throw new ApiError(res.status, await parseErrorDetail(res));
  }
  return res.json();
}

/**
 * Submits content for verification, then polls until the backend reports a
 * terminal status (completed/failed). Calls onStatusChange as the real
 * status transitions so the UI can reflect actual backend progress rather
 * than a simulated timer.
 */
export async function verifyAndAwaitResult(
  input: SubmitVerificationInput,
  onStatusChange?: (status: RequestStatus) => void,
  options: { pollIntervalMs?: number; timeoutMs?: number } = {}
): Promise<VerificationResult> {
  const pollIntervalMs = options.pollIntervalMs ?? 1500;
  const timeoutMs = options.timeoutMs ?? 120_000;

  const { request_id } = await submitVerification(input);
  onStatusChange?.("pending");

  const start = Date.now();
  for (;;) {
    const result = await getVerificationResult(request_id);
    onStatusChange?.(result.status);

    if (result.status === "completed" || result.status === "failed") {
      return result;
    }
    if (Date.now() - start > timeoutMs) {
      throw new ApiError(408, "Verification is taking longer than expected. Please try again.");
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
}

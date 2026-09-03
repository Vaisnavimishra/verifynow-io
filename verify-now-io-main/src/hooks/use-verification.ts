import { useState, useCallback } from "react";
import {
  verifyAndAwaitResult,
  ApiError,
  type VerificationResult,
  type RequestStatus,
} from "@/lib/api";
import { resolveContentType } from "@/lib/verifyMode";
import type { VerifyAnalyzeData } from "@/components/verify/VerifyInput";
import { useToast } from "@/hooks/use-toast";

export type UiStatus = "idle" | "submitting" | RequestStatus;

export function statusToProgress(status: UiStatus): number {
  switch (status) {
    case "idle":
      return 0;
    case "submitting":
      return 10;
    case "pending":
      return 30;
    case "processing":
      return 70;
    case "completed":
    case "failed":
      return 100;
    default:
      return 0;
  }
}

export function statusLabel(status: UiStatus): string {
  switch (status) {
    case "submitting":
      return "Submitting content...";
    case "pending":
      return "Queued for verification...";
    case "processing":
      return "Researching real sources...";
    case "completed":
      return "Verification complete";
    case "failed":
      return "Verification failed";
    default:
      return "";
  }
}

export function useVerification() {
  const [status, setStatus] = useState<UiStatus>("idle");
  const [result, setResult] = useState<VerificationResult | null>(null);
  const { toast } = useToast();

  const isAnalyzing = status === "submitting" || status === "pending" || status === "processing";

  const analyze = useCallback(
    async (data: VerifyAnalyzeData) => {
      setResult(null);
      setStatus("submitting");

      try {
        const contentType = resolveContentType(data.type, data.file);
        const finalResult = await verifyAndAwaitResult(
          {
            contentType,
            text: data.file ? undefined : data.content,
            file: data.file,
          },
          (backendStatus) => setStatus(backendStatus)
        );
        setStatus(finalResult.status);
        setResult(finalResult);
      } catch (err) {
        setStatus("idle");
        const message =
          err instanceof ApiError
            ? err.message
            : "Something went wrong while verifying this content. Please try again.";
        toast({ description: message, variant: "destructive" });
      }
    },
    [toast]
  );

  const reset = useCallback(() => {
    setResult(null);
    setStatus("idle");
  }, []);

  return { status, isAnalyzing, result, analyze, reset };
}

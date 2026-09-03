import type { BackendContentType } from "@/lib/api";
import type { VerifyMode } from "@/components/verify/VerifyInput";
import { isImageFile } from "@/components/verify/VerifyInput";

/**
 * Maps a UI tab (video/document/chat/link) plus an optional uploaded file to
 * the backend's content_type. Document uploads are routed to the backend's
 * "image" pipeline (vision-based claim extraction) when the file is an
 * image, and "document" (text extraction) otherwise — this is the only
 * branching; nothing here decides a verdict.
 */
export function resolveContentType(mode: VerifyMode, file?: File): BackendContentType {
  switch (mode) {
    case "chat":
      return "text";
    case "link":
      return "url";
    case "video":
      return "video_url";
    case "document":
      return file && isImageFile(file) ? "image" : "document";
    default:
      return "text";
  }
}

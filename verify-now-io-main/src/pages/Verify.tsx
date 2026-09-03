import { useParams, Navigate } from "react-router-dom";
import VerifyInput, { type VerifyMode } from "@/components/verify/VerifyInput";
import ProgressBar from "@/components/verify/ProgressBar";
import ResultCard from "@/components/verify/ResultCard";
import { Card, CardContent } from "@/components/ui/card";
import { Video, FileText, MessageSquare, Link2 } from "lucide-react";
import { useVerification, statusToProgress, statusLabel } from "@/hooks/use-verification";

const Verify = () => {
  const { type } = useParams<{ type: VerifyMode }>();
  const { status, isAnalyzing, result, analyze, reset } = useVerification();

  // Redirect to default verify page if no type specified
  if (!type) {
    return <Navigate to="/verify/video" replace />;
  }

  // Validate type parameter
  const validTypes: VerifyMode[] = ["video", "document", "chat", "link"];
  if (!validTypes.includes(type)) {
    return <Navigate to="/verify/video" replace />;
  }

  const progressValue = statusToProgress(status);
  const progressSteps = [
    { label: "Submitted", completed: progressValue > 10, active: progressValue <= 10 && progressValue > 0 },
    { label: "Queued", completed: progressValue > 30, active: progressValue > 10 && progressValue <= 30 },
    { label: "Researching real sources", completed: progressValue > 70, active: progressValue > 30 && progressValue <= 70 },
    { label: "Finalizing result", completed: progressValue >= 100, active: progressValue > 70 && progressValue < 100 },
  ];

  const getTypeConfig = (type: VerifyMode) => {
    const configs = {
      video: {
        icon: Video,
        title: "Video Verification",
        description: "Paste a video URL to check its metadata and claims against real sources",
      },
      document: {
        icon: FileText,
        title: "Document Verification",
        description: "Upload a document or image to check its claims against real sources",
      },
      chat: {
        icon: MessageSquare,
        title: "Chat/Text Verification",
        description: "Check chat messages and text content against real, retrieved evidence",
      },
      link: {
        icon: Link2,
        title: "Website Link Verification",
        description: "Check a website's claims, metadata, and identity against independent sources",
      },
    };

    return configs[type];
  };

  const config = getTypeConfig(type);
  const Icon = config.icon;

  return (
    <div className="min-h-screen bg-gradient-hero py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-3 bg-primary/10 rounded-xl">
              <Icon className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold text-foreground">{config.title}</h1>
          </div>
          <p className="text-foreground-secondary text-lg max-w-2xl mx-auto">
            {config.description}
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {/* Input Form */}
          <VerifyInput mode={type} onAnalyze={analyze} isLoading={isAnalyzing} />

          {/* Progress Indicator */}
          {isAnalyzing && (
            <ProgressBar
              steps={progressSteps}
              progress={progressValue}
              currentStep={statusLabel(status)}
            />
          )}

          {/* Results */}
          {result && <ResultCard result={result} onRerun={reset} />}

          {/* Tips Card */}
          {!isAnalyzing && !result && (
            <Card className="bg-surface/80 border-border">
              <CardContent className="p-6">
                <h3 className="font-semibold text-foreground mb-3">Tips for Better Results</h3>
                <ul className="space-y-2 text-sm text-foreground-secondary">
                  {type === "video" && (
                    <>
                      <li>• Only video URLs are supported — full video file analysis is not implemented yet</li>
                      <li>• Public, well-known video pages return more useful metadata</li>
                      <li>• If the underlying claim is also stated in text, try the Chat/Text check too</li>
                    </>
                  )}
                  {type === "document" && (
                    <>
                      <li>• PDF, DOCX, TXT, and common image formats are supported</li>
                      <li>• Scanned documents without embedded text may fail to extract</li>
                      <li>• Images are analyzed for their visible claim, not pixel-level tampering</li>
                    </>
                  )}
                  {type === "chat" && (
                    <>
                      <li>• Include enough context for a specific, checkable claim</li>
                      <li>• Vague or opinion-based text will return UNCERTAIN, not a guess</li>
                      <li>• Longer, specific claims are easier to verify against real sources</li>
                    </>
                  )}
                  {type === "link" && (
                    <>
                      <li>• Full URLs work better than shortened links</li>
                      <li>• We distinguish what a site claims about itself from what's independently verified</li>
                      <li>• Sites without independently verifiable history will return UNCERTAIN for those claims</li>
                    </>
                  )}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Verify;

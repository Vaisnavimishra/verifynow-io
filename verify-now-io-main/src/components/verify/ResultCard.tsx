import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ShieldCheck,
  ShieldX,
  AlertTriangle,
  HelpCircle,
  Share2,
  RotateCcw,
  Clock,
  CheckCircle2,
  XCircle,
  Info,
  ExternalLink,
  Globe,
  Sparkles,
  AlertOctagon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { VerificationResult } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface ResultCardProps {
  result: VerificationResult;
  onRerun?: () => void;
  className?: string;
}

const VERDICT_CONFIG: Record<
  string,
  {
    icon: typeof ShieldCheck;
    bgColor: string;
    borderColor: string;
    textColor: string;
    label: string;
  }
> = {
  VERIFIED: {
    icon: ShieldCheck,
    bgColor: "bg-success/10",
    borderColor: "border-success/20",
    textColor: "text-success",
    label: "Verified",
  },
  FALSE: {
    icon: ShieldX,
    bgColor: "bg-destructive/10",
    borderColor: "border-destructive/20",
    textColor: "text-destructive",
    label: "False",
  },
  MISLEADING: {
    icon: AlertTriangle,
    bgColor: "bg-warning/10",
    borderColor: "border-warning/20",
    textColor: "text-warning",
    label: "Misleading",
  },
  UNCERTAIN: {
    icon: HelpCircle,
    bgColor: "bg-muted/30",
    borderColor: "border-muted",
    textColor: "text-muted-foreground",
    label: "Uncertain",
  },
};

const STANCE_ICON: Record<string, typeof CheckCircle2> = {
  supports: CheckCircle2,
  refutes: XCircle,
  context: Info,
};

const STANCE_COLOR: Record<string, string> = {
  supports: "text-success",
  refutes: "text-destructive",
  context: "text-muted-foreground",
};

const ResultCard = ({ result, onRerun, className }: ResultCardProps) => {
  const { toast } = useToast();

  if (result.status === "failed") {
    return (
      <Card className={cn("bg-surface border-border shadow-elevated", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <AlertOctagon className="h-5 w-5 text-destructive" />
            Verification Failed
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-foreground-secondary text-sm">
            {result.error_message ||
              "The verification pipeline encountered an unexpected error."}
          </p>
          {onRerun && (
            <Button onClick={onRerun} variant="outline" className="w-full">
              <RotateCcw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  const verdict = result.verdict ?? "UNCERTAIN";
  const config = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG.UNCERTAIN;
  const VerdictIcon = config.icon;

  const handleShare = async () => {
    const summary = [
      `Verdict: ${config.label}`,
      result.confidence !== null ? `Confidence: ${result.confidence}%` : "Confidence: not stated",
      `Source: ${result.input_summary}`,
    ].join("\n");
    try {
      await navigator.clipboard.writeText(summary);
      toast({ description: "Result summary copied to clipboard." });
    } catch {
      toast({ description: "Could not copy to clipboard.", variant: "destructive" });
    }
  };

  return (
    <Card className={cn("bg-surface border-border shadow-elevated", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-foreground">Verification Result</CardTitle>
          <div className="flex items-center space-x-2 text-sm text-foreground-secondary">
            <Clock className="h-4 w-4" />
            <span>{new Date(result.created_at).toLocaleString()}</span>
            {result.from_cache && (
              <Badge variant="secondary" className="ml-1">
                cached
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Verdict */}
        <div className={cn("rounded-2xl p-6 border", config.bgColor, config.borderColor)}>
          <div className="flex items-center justify-center space-x-3">
            <VerdictIcon className={cn("h-8 w-8", config.textColor)} />
            <div className="text-center">
              <div className={cn("text-2xl font-bold", config.textColor)}>{config.label}</div>
              <div className="text-sm font-medium mt-1 text-foreground-secondary">
                {result.confidence !== null
                  ? `${result.confidence}% confidence`
                  : "Confidence not stated — insufficient evidence for a numeric score"}
              </div>
            </div>
          </div>
        </div>

        {/* Reasoning */}
        {result.reasoning && (
          <div>
            <h4 className="font-semibold text-foreground mb-2">Why</h4>
            <p className="text-sm text-foreground-secondary">{result.reasoning}</p>
          </div>
        )}

        {/* Content metadata */}
        {result.content_published_date && (
          <div className="text-sm text-foreground-secondary">
            <span className="font-medium text-foreground">Originally published: </span>
            {result.content_published_date}
          </div>
        )}

        {/* Website intelligence */}
        {result.website_metadata && (
          <div className="rounded-xl border border-border p-4 space-y-3">
            <h4 className="font-semibold text-foreground flex items-center gap-2">
              <Globe className="h-4 w-4 text-primary" />
              Website Intelligence
            </h4>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm">
              {result.website_metadata.domain && (
                <div>
                  <dt className="text-foreground-secondary">Domain</dt>
                  <dd className="text-foreground">{result.website_metadata.domain}</dd>
                </div>
              )}
              {result.website_metadata.site_name && (
                <div>
                  <dt className="text-foreground-secondary">Site name</dt>
                  <dd className="text-foreground">{result.website_metadata.site_name}</dd>
                </div>
              )}
              {result.website_metadata.founding_or_launch_date && (
                <div>
                  <dt className="text-foreground-secondary">Founded / launched</dt>
                  <dd className="text-foreground">
                    {result.website_metadata.founding_or_launch_date}
                  </dd>
                </div>
              )}
              {result.website_metadata.founder_or_organization && (
                <div>
                  <dt className="text-foreground-secondary">Founder / organization</dt>
                  <dd className="text-foreground">
                    {result.website_metadata.founder_or_organization}
                  </dd>
                </div>
              )}
            </dl>
            {result.website_metadata.about && (
              <p className="text-sm text-foreground-secondary">
                <span className="font-medium text-foreground">About: </span>
                {result.website_metadata.about}
              </p>
            )}
            {result.website_metadata.company_info && (
              <p className="text-sm text-foreground-secondary">
                <span className="font-medium text-foreground">Company info: </span>
                {result.website_metadata.company_info}
              </p>
            )}
            {result.website_metadata.claims_made_by_site.length > 0 && (
              <div className="text-sm">
                <p className="font-medium text-foreground mb-1">Claims made by the website:</p>
                <ul className="space-y-1">
                  {result.website_metadata.claims_made_by_site.map((claim, i) => {
                    const verified =
                      result.website_metadata!.independently_verified_claims.includes(claim);
                    return (
                      <li key={i} className="flex items-start gap-2 text-foreground-secondary">
                        {verified ? (
                          <CheckCircle2 className="h-3.5 w-3.5 text-success mt-0.5 shrink-0" />
                        ) : (
                          <HelpCircle className="h-3.5 w-3.5 text-muted-foreground mt-0.5 shrink-0" />
                        )}
                        <span>
                          &quot;{claim}&quot; —{" "}
                          <span className={verified ? "text-success" : "text-muted-foreground"}>
                            {verified ? "independently verified" : "website says, unverified"}
                          </span>
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Evidence / sources */}
        {result.evidence.length > 0 && (
          <div>
            <h4 className="font-semibold text-foreground mb-3">Evidence & Sources</h4>
            <div className="space-y-3">
              {result.evidence.map((item, index) => {
                const StanceIcon = STANCE_ICON[item.stance] ?? Info;
                return (
                  <div
                    key={index}
                    className="flex items-start space-x-2 text-sm border-b border-border last:border-0 pb-3 last:pb-0"
                  >
                    <div className="mt-1">
                      <StanceIcon className={cn("h-3.5 w-3.5", STANCE_COLOR[item.stance])} />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-foreground">{item.claim}</p>
                      {item.excerpt && (
                        <p className="text-foreground-secondary italic">{item.excerpt}</p>
                      )}
                      <div className="flex flex-wrap items-center gap-x-2 text-xs text-foreground-secondary">
                        <a
                          href={item.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          {item.source_name}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                        {item.published_date && <span>· {item.published_date}</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* AI-generated style signal (explicitly not factual evidence) */}
        {result.ai_generated_signal && result.ai_generated_signal.note && (
          <div className="flex items-start gap-2 text-xs text-foreground-secondary bg-muted/30 p-3 rounded-lg border border-border">
            <Sparkles className="h-3.5 w-3.5 mt-0.5 shrink-0" />
            <span>{result.ai_generated_signal.note}</span>
          </div>
        )}

        {/* Limitations */}
        {result.limitations && (
          <div className="text-xs text-foreground-secondary bg-muted/50 p-3 rounded-lg border border-border">
            <strong>Limitations:</strong> {result.limitations}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-border">
          <Button
            onClick={onRerun}
            variant="outline"
            className="flex-1 bg-background hover:bg-muted border-border"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Re-run Analysis
          </Button>
          <Button
            onClick={handleShare}
            variant="outline"
            className="flex-1 bg-background hover:bg-muted border-border"
          >
            <Share2 className="h-4 w-4 mr-2" />
            Copy Summary
          </Button>
        </div>

        <div className="text-xs text-foreground-secondary bg-muted/50 p-3 rounded-lg border border-border">
          <strong>Disclaimer:</strong> This assessment is generated from real, retrieved
          sources where available. Verify critical decisions with multiple independent
          sources.
        </div>
      </CardContent>
    </Card>
  );
};

export default ResultCard;

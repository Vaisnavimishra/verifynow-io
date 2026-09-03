import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

interface ProgressStep {
  label: string;
  completed: boolean;
  active: boolean;
}

interface ProgressBarProps {
  steps: ProgressStep[];
  progress: number;
  currentStep?: string;
}

const ProgressBar = ({ steps, progress, currentStep }: ProgressBarProps) => {
  return (
    <Card className="bg-surface border-border shadow-card">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span className="text-foreground font-medium">
              {currentStep || "Analyzing..."}
            </span>
          </div>
          
          <Progress value={progress} className="h-2" />
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`flex items-center space-x-2 ${
                  step.completed
                    ? "text-success"
                    : step.active
                    ? "text-primary"
                    : "text-foreground-secondary"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    step.completed
                      ? "bg-success"
                      : step.active
                      ? "bg-primary animate-pulse"
                      : "bg-muted"
                  }`}
                />
                <span>{step.label}</span>
              </div>
            ))}
          </div>
          
          <div className="text-center text-xs text-foreground-secondary">
            {progress.toFixed(0)}% complete
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProgressBar;
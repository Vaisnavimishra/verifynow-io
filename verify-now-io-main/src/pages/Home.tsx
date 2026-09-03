import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Video, FileText, MessageSquare, Link2, ArrowRight, Shield, Zap, Eye } from "lucide-react";
import VerifyInput from "@/components/verify/VerifyInput";
import ProgressBar from "@/components/verify/ProgressBar";
import ResultCard from "@/components/verify/ResultCard";
import { useVerification, statusToProgress, statusLabel } from "@/hooks/use-verification";

const Home = () => {
  const { status, isAnalyzing, result, analyze, reset } = useVerification();

  const progressValue = statusToProgress(status);
  const progressSteps = [
    { label: "Submitted", completed: progressValue > 10, active: progressValue <= 10 && progressValue > 0 },
    { label: "Queued", completed: progressValue > 30, active: progressValue > 10 && progressValue <= 30 },
    { label: "Researching real sources", completed: progressValue > 70, active: progressValue > 30 && progressValue <= 70 },
    { label: "Finalizing result", completed: progressValue >= 100, active: progressValue > 70 && progressValue < 100 },
  ];

  const features = [
    {
      icon: Video,
      title: "Video Check",
      description: "Real-time frame analysis, watermark detection, and deepfake identification",
      link: "/verify/video",
    },
    {
      icon: FileText,
      title: "Document Check",
      description: "Metadata analysis, OCR verification, and manipulation detection",
      link: "/verify/document",
    },
    {
      icon: MessageSquare,
      title: "Chat/Text Check",
      description: "Linguistic pattern analysis, style anomaly detection, and source verification",
      link: "/verify/chat",
    },
    {
      icon: Link2,
      title: "Link Check",
      description: "Domain reputation, SSL verification, and phishing detection",
      link: "/verify/link",
    },
  ];

  const howItWorks = [
    {
      icon: Eye,
      title: "Upload or Paste",
      description: "Submit your content through our secure interface",
    },
    {
      icon: Zap,
      title: "AI Analysis",
      description: "Advanced algorithms scan for authenticity markers",
    },
    {
      icon: Shield,
      title: "Get Results",
      description: "Receive detailed verdict with confidence score",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-8">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground">
              Detect Fake.{" "}
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                Trust What's Real.
              </span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-foreground-secondary max-w-3xl mx-auto">
              Instant verification for videos, documents, chats, and website links—powered by AI.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                asChild
                size="lg"
                className="bg-gradient-primary hover:bg-primary-hover text-primary-foreground font-semibold px-8 py-3 text-lg shadow-glow"
              >
                <Link to="/verify">Start Verifying</Link>
              </Button>
              
              <Button 
                asChild
                variant="outline"
                size="lg"
                className="border-border bg-surface hover:bg-muted text-foreground font-medium px-8 py-3 text-lg"
              >
                <Link to="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Verify Widget */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground mb-4">Try It Now</h2>
            <p className="text-foreground-secondary">Quick verification in seconds</p>
          </div>
          
          <div className="space-y-6">
            <VerifyInput onAnalyze={analyze} isLoading={isAnalyzing} />

            {isAnalyzing && (
              <ProgressBar
                steps={progressSteps}
                progress={progressValue}
                currentStep={statusLabel(status)}
              />
            )}

            {result && <ResultCard result={result} onRerun={reset} />}
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">Verification Types</h2>
            <p className="text-foreground-secondary">Comprehensive analysis across multiple content types</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="bg-surface border-border shadow-card hover:shadow-elevated transition-all duration-300 group">
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <CardTitle className="text-foreground">{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <p className="text-foreground-secondary mb-4">{feature.description}</p>
                    <Button 
                      asChild
                      variant="ghost"
                      className="w-full justify-between text-primary hover:text-primary-hover hover:bg-primary/10"
                    >
                      <Link to={feature.link}>
                        Try Now
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-surface/50">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">How It Works</h2>
            <p className="text-foreground-secondary">Simple, fast, and reliable verification in three steps</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorks.map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={index} className="text-center space-y-4">
                  <div className="mx-auto w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-glow">
                    <Icon className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground">{step.title}</h3>
                  <p className="text-foreground-secondary">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Trust & Safety */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-4xl">
          <Card className="bg-surface border-border shadow-card">
            <CardContent className="p-8 text-center">
              <Shield className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-foreground mb-4">Trust & Safety</h3>
              <p className="text-foreground-secondary mb-6">
                Our AI provides quick triage to help you identify potentially suspicious content. 
                While our analysis is sophisticated, it's important to understand the limitations 
                and verify with multiple sources for critical decisions.
              </p>
              <div className="bg-warning/10 border border-warning/20 rounded-lg p-4">
                <p className="text-sm text-foreground-secondary">
                  <strong>Important:</strong> This tool is not a definitive legal assessment. 
                  Results should be used as one factor in your decision-making process.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default Home;
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Target, Eye, Users, AlertTriangle, CheckCircle2 } from "lucide-react";

const About = () => {
  const reasons = [
    {
      icon: Target,
      title: "Fight Misinformation",
      description: "Help users quickly identify potentially false or manipulated content before it spreads.",
    },
    {
      icon: Shield,
      title: "Protect from Scams", 
      description: "Detect phishing attempts, fake documents, and fraudulent communications.",
    },
    {
      icon: Eye,
      title: "Promote Transparency",
      description: "Provide clear, understandable analysis with confidence scores and evidence.",
    },
  ];

  const methodology = [
    {
      title: "Metadata Analysis",
      description: "Examine file properties, creation timestamps, and modification history for inconsistencies.",
    },
    {
      title: "Pattern Recognition",
      description: "Use machine learning to identify signatures of manipulation, generation, or deception.",
    },
    {
      title: "Cross-Reference Verification",
      description: "Compare against known databases and reputation systems for additional context.",
    },
    {
      title: "Statistical Modeling",
      description: "Apply linguistic and visual analysis to detect anomalies in content patterns.",
    },
  ];

  const limitations = [
    "Results are probabilistic, not definitive proof",
    "New manipulation techniques may not be detected",
    "Analysis quality depends on input content quality",
    "Context and human judgment remain essential",
    "Not suitable for legal or critical decision-making alone",
  ];

  return (
    <div className="min-h-screen bg-gradient-hero py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">About Fake Detection</h1>
          <p className="text-xl text-foreground-secondary max-w-2xl mx-auto">
            Empowering users to make informed decisions about digital content authenticity
          </p>
        </div>

        <div className="space-y-8">
          {/* Mission */}
          <Card className="bg-surface border-border shadow-card">
            <CardHeader>
              <CardTitle className="text-foreground text-2xl">Our Mission</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-foreground-secondary text-lg leading-relaxed">
                In an era of sophisticated digital manipulation and widespread misinformation, 
                we believe everyone deserves tools to verify content authenticity. Our platform 
                provides quick, accessible analysis to help users make informed decisions about 
                the digital content they encounter.
              </p>
            </CardContent>
          </Card>

          {/* Why We Built This */}
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-6">Why We Built This</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {reasons.map((reason, index) => {
                const Icon = reason.icon;
                return (
                  <Card key={index} className="bg-surface border-border shadow-card">
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <Icon className="h-6 w-6 text-primary" />
                        </div>
                        <CardTitle className="text-foreground">{reason.title}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-foreground-secondary">{reason.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* How It Helps */}
          <Card className="bg-surface border-border shadow-card">
            <CardHeader>
              <CardTitle className="text-foreground text-2xl">How It Helps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-foreground mb-2">For Individuals</h4>
                  <ul className="space-y-2 text-foreground-secondary">
                    <li>• Verify suspicious social media content</li>
                    <li>• Check documents before important decisions</li>
                    <li>• Identify potential phishing attempts</li>
                    <li>• Validate news and information sources</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground mb-2">For Organizations</h4>
                  <ul className="space-y-2 text-foreground-secondary">
                    <li>• Content moderation and fact-checking</li>
                    <li>• Document verification workflows</li>
                    <li>• Security threat assessment</li>
                    <li>• Brand protection initiatives</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Methodology */}
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-6">Our Methodology</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {methodology.map((method, index) => (
                <Card key={index} className="bg-surface border-border shadow-card">
                  <CardContent className="p-6">
                    <h4 className="font-semibold text-foreground mb-2">{method.title}</h4>
                    <p className="text-foreground-secondary text-sm">{method.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Ethical Considerations & Limitations */}
          <Card className="bg-surface border-border shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground text-2xl">
                <AlertTriangle className="h-6 w-6 text-warning" />
                <span>Important Limitations</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-foreground-secondary">
                While our AI analysis is sophisticated, it's crucial to understand its limitations:
              </p>
              <ul className="space-y-2">
                {limitations.map((limitation, index) => (
                  <li key={index} className="flex items-start space-x-2 text-foreground-secondary">
                    <AlertTriangle className="h-4 w-4 text-warning mt-0.5 flex-shrink-0" />
                    <span>{limitation}</span>
                  </li>
                ))}
              </ul>
              <div className="bg-warning/10 border border-warning/20 rounded-lg p-4 mt-6">
                <p className="text-foreground text-sm">
                  <strong>Remember:</strong> This tool provides analysis to help inform your decisions, 
                  but should not be the sole factor in critical situations. Always verify important 
                  information through multiple sources and consult experts when needed.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Best Practices */}
          <Card className="bg-surface border-border shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground text-2xl">
                <CheckCircle2 className="h-6 w-6 text-success" />
                <span>Best Practices</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-foreground-secondary">
                    Use results as one factor in a comprehensive verification process
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-foreground-secondary">
                    Cross-reference findings with multiple sources and tools
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-foreground-secondary">
                    Consider context, source credibility, and expert opinions
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-foreground-secondary">
                    Stay updated on evolving manipulation techniques and detection methods
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Contact */}
          <Card className="bg-surface border-border shadow-card">
            <CardHeader>
              <CardTitle className="text-foreground text-2xl">Contact & Feedback</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-foreground-secondary mb-4">
                We're constantly improving our detection capabilities and user experience. 
                Your feedback helps us build a better tool for everyone.
              </p>
              <div className="space-y-2 text-foreground-secondary">
                <p>• Report false positives or missed detections</p>
                <p>• Suggest new features or improvements</p>
                <p>• Share your use cases and experiences</p>
                <p>• Request enterprise or API access</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default About;
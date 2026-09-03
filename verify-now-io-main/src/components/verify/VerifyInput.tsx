import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link2, MessageSquare, FileText, Video } from "lucide-react";

export type VerifyMode = "video" | "document" | "chat" | "link";

export interface VerifyAnalyzeData {
  type: VerifyMode;
  content: string;
  file?: File;
}

interface VerifyInputProps {
  mode?: VerifyMode;
  onAnalyze: (data: VerifyAnalyzeData) => void;
  isLoading?: boolean;
}

const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"];

export function isImageFile(file: File): boolean {
  const lower = file.name.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext)) || file.type.startsWith("image/");
}

const VerifyInput = ({ mode, onAnalyze, isLoading = false }: VerifyInputProps) => {
  const [activeTab, setActiveTab] = useState<VerifyMode>(mode || "chat");
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (type: VerifyMode) => (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && !file) return;

    onAnalyze({
      type,
      content: file ? file.name : input,
      file: file ?? undefined,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setInput("");
    }
  };

  const modeConfig: Record<
    VerifyMode,
    {
      icon: typeof Video;
      title: string;
      description: string;
      placeholder: string;
      acceptedFiles: string;
      inputType: "url" | "file" | "text";
    }
  > = {
    video: {
      icon: Video,
      title: "Video Verification",
      description:
        "Paste a video URL (YouTube, Vimeo, or a direct link). Full video file analysis is not yet supported — only the page/video metadata is checked.",
      placeholder: "Paste a video URL...",
      acceptedFiles: "",
      inputType: "url",
    },
    document: {
      icon: FileText,
      title: "Document Verification",
      description:
        "Upload a PDF, DOCX, TXT document, or an image. Text is extracted and checked against real sources.",
      placeholder: "Upload document or image...",
      acceptedFiles: ".pdf,.docx,.txt,.md,.jpg,.jpeg,.png,.gif,.webp",
      inputType: "file",
    },
    chat: {
      icon: MessageSquare,
      title: "Chat/Text Verification",
      description: "Paste chat messages or text content to check its claims against real sources.",
      placeholder: "Paste your chat or text content here...",
      acceptedFiles: "",
      inputType: "text",
    },
    link: {
      icon: Link2,
      title: "Website Link Verification",
      description: "Enter a website URL to check its claims and metadata against real sources.",
      placeholder: "https://example.com",
      acceptedFiles: "",
      inputType: "url",
    },
  };

  const renderInput = (type: VerifyMode) => {
    const config = modeConfig[type];
    const Icon = config.icon;

    return (
      <Card className="bg-surface border-border shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-foreground">
            <Icon className="h-5 w-5 text-primary" />
            <span>{config.title}</span>
          </CardTitle>
          <p className="text-sm text-foreground-secondary">{config.description}</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(type)} className="space-y-4">
            {config.inputType === "file" && (
              <div>
                <Label htmlFor={`file-${type}`} className="text-foreground">
                  Upload File
                </Label>
                <Input
                  id={`file-${type}`}
                  type="file"
                  accept={config.acceptedFiles}
                  onChange={handleFileChange}
                  className="mt-1 bg-background border-border text-foreground"
                />
                {file && (
                  <p className="mt-1 text-xs text-foreground-secondary">Selected: {file.name}</p>
                )}
              </div>
            )}

            {config.inputType === "text" && (
              <div>
                <Label htmlFor={`text-${type}`} className="text-foreground">
                  Text Content
                </Label>
                <Textarea
                  id={`text-${type}`}
                  placeholder={config.placeholder}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={6}
                  className="mt-1 bg-background border-border text-foreground resize-none"
                />
              </div>
            )}

            {config.inputType === "url" && (
              <div>
                <Label htmlFor={`url-${type}`} className="text-foreground">
                  {type === "video" ? "Video URL" : "Website URL"}
                </Label>
                <Input
                  id={`url-${type}`}
                  type="url"
                  placeholder={config.placeholder}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="mt-1 bg-background border-border text-foreground"
                />
              </div>
            )}

            <Button
              type="submit"
              disabled={(!input.trim() && !file) || isLoading}
              className="w-full bg-gradient-primary hover:bg-primary-hover text-primary-foreground font-medium"
            >
              {isLoading ? "Verifying..." : "Start Verification"}
            </Button>
          </form>
        </CardContent>
      </Card>
    );
  };

  if (mode) {
    return renderInput(mode);
  }

  return (
    <Tabs value={activeTab} onValueChange={(value) => { setInput(""); setFile(null); setActiveTab(value as VerifyMode); }}>
      <TabsList className="grid w-full grid-cols-4 bg-surface border-border">
        <TabsTrigger value="video" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">Video</TabsTrigger>
        <TabsTrigger value="document" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">Document</TabsTrigger>
        <TabsTrigger value="chat" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">Chat</TabsTrigger>
        <TabsTrigger value="link" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">Link</TabsTrigger>
      </TabsList>

      <TabsContent value="video">{renderInput("video")}</TabsContent>
      <TabsContent value="document">{renderInput("document")}</TabsContent>
      <TabsContent value="chat">{renderInput("chat")}</TabsContent>
      <TabsContent value="link">{renderInput("link")}</TabsContent>
    </Tabs>
  );
};

export default VerifyInput;

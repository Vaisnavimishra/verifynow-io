import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Shield, ChevronDown, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const verifyMenuItems = [
    { label: "Video", path: "/verify/video" },
    { label: "Document", path: "/verify/document" },
    { label: "Chat", path: "/verify/chat" },
    { label: "Link", path: "/verify/link" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Shield className="h-8 w-8 text-primary" />
            <span className="font-bold text-xl text-foreground">Fake Detection</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                isActive("/") ? "text-primary" : "text-foreground"
              )}
            >
              Home
            </Link>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  className={cn(
                    "flex items-center space-x-1 text-sm font-medium",
                    location.pathname.startsWith("/verify") ? "text-primary" : "text-foreground"
                  )}
                >
                  <span>Verify</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-40 bg-surface border-border">
                {verifyMenuItems.map((item) => (
                  <DropdownMenuItem key={item.path} asChild>
                    <Link 
                      to={item.path}
                      className={cn(
                        "w-full cursor-pointer",
                        isActive(item.path) && "text-primary"
                      )}
                    >
                      {item.label}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <Link
              to="/about"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                isActive("/about") ? "text-primary" : "text-foreground"
              )}
            >
              About
            </Link>

            <ThemeToggle />
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="h-9 w-9 p-0"
            >
              {isMobileMenuOpen ? (
                <X className="h-4 w-4" />
              ) : (
                <Menu className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border py-4 space-y-4">
            <Link
              to="/"
              className={cn(
                "block text-sm font-medium transition-colors hover:text-primary",
                isActive("/") ? "text-primary" : "text-foreground"
              )}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Home
            </Link>
            
            <div className="space-y-2">
              <div className="text-sm font-medium text-foreground">Verify</div>
              <div className="pl-4 space-y-2">
                {verifyMenuItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      "block text-sm transition-colors hover:text-primary",
                      isActive(item.path) ? "text-primary" : "text-foreground-secondary"
                    )}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>

            <Link
              to="/about"
              className={cn(
                "block text-sm font-medium transition-colors hover:text-primary",
                isActive("/about") ? "text-primary" : "text-foreground"
              )}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              About
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
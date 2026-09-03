import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-hero px-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-foreground mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-foreground mb-4">Page Not Found</h2>
        <p className="text-foreground-secondary mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="space-y-4">
          <Button asChild className="bg-gradient-primary hover:bg-primary-hover text-primary-foreground">
            <Link to="/">Return Home</Link>
          </Button>
          <Button asChild variant="outline" className="border-border hover:bg-muted">
            <Link to="/verify">Try Verification</Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;

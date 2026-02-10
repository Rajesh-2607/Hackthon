import { Link } from "react-router-dom";
import { Shield, Menu, X, LogOut } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated, logout, user } = useAuth();

  const navLinks = [
    { label: "Dashboard", href: "/" },
    { label: "Detection", href: "/detection" },
    { label: "Reports", href: "/reports" },
    { label: "Settings", href: "/settings" },
  ];

  const authLinks = isAuthenticated 
    ? [] 
    : [
        { label: "Login", href: "/login" },
        { label: "Sign Up", href: "/signup" },
      ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="glass border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
                <div className="relative bg-background px-3 py-2 rounded-lg flex items-center gap-2">
                  <Shield className="w-5 h-5 text-neon-cyan" />
                  <span className="font-bold text-lg bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
                    Secure Sphere
                  </span>
                </div>
              </div>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="text-sm font-medium text-foreground/70 hover:text-neon-cyan transition-colors duration-300 relative group"
                >
                  {link.label}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-cyan to-neon-blue group-hover:w-full transition-all duration-300"></span>
                </Link>
              ))}
              
              {/* Auth Links */}
              {authLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="text-sm font-medium text-foreground/70 hover:text-neon-cyan transition-colors duration-300 relative group"
                >
                  {link.label}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-neon-cyan to-neon-blue group-hover:w-full transition-all duration-300"></span>
                </Link>
              ))}
              
              {/* Logout Button */}
              {isAuthenticated && (
                <div className="flex items-center gap-4">
                  <span className="text-sm text-foreground/60">Welcome, {user?.full_name}</span>
                  <button
                    onClick={() => logout()}
                    className="flex items-center gap-2 text-sm font-medium text-foreground/70 hover:text-red-400 transition-colors duration-300"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 flex flex-col gap-3">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="text-sm font-medium text-foreground/70 hover:text-neon-cyan px-3 py-2 rounded-lg hover:bg-white/5 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              
              {/* Auth Links */}
              {authLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="text-sm font-medium text-foreground/70 hover:text-neon-cyan px-3 py-2 rounded-lg hover:bg-white/5 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              
              {/* Mobile Logout */}
              {isAuthenticated && (
                <div className="px-3 py-2 border-t border-white/10 mt-2 pt-3">
                  <p className="text-xs text-foreground/60 mb-2">Welcome, {user?.full_name}</p>
                  <button
                    onClick={async () => {
                      await logout();
                      setMobileMenuOpen(false);
                    }}
                    className="flex items-center gap-2 text-sm font-medium text-foreground/70 hover:text-red-400 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative">{children}</main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-background/50 backdrop-blur-sm py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <Shield className="w-4 h-4 text-neon-cyan" />
                Secure Sphere
              </h3>
              <p className="text-sm text-foreground/50">
                Advanced fake account detection for social media security.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-3">Product</h4>
              <ul className="space-y-2 text-sm text-foreground/50 hover:text-foreground/70">
                <li>
                  <Link to="/detection" className="hover:text-neon-cyan transition-colors">
                    Detection
                  </Link>
                </li>
                <li>
                  <Link to="/reports" className="hover:text-neon-cyan transition-colors">
                    Reports
                  </Link>
                </li>
                <li>
                  <Link to="/" className="hover:text-neon-cyan transition-colors">
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-3">Company</h4>
              <ul className="space-y-2 text-sm text-foreground/50 hover:text-foreground/70">
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-3">Legal</h4>
              <ul className="space-y-2 text-sm text-foreground/50 hover:text-foreground/70">
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    Terms
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-neon-cyan transition-colors">
                    Security
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-foreground/50">
              © 2024 Secure Sphere. All rights reserved.
            </p>
            <div className="flex gap-6">
              <a href="#" className="text-foreground/50 hover:text-neon-cyan transition-colors">
                Twitter
              </a>
              <a href="#" className="text-foreground/50 hover:text-neon-cyan transition-colors">
                LinkedIn
              </a>
              <a href="#" className="text-foreground/50 hover:text-neon-cyan transition-colors">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

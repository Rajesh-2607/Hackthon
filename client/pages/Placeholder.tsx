import Layout from "@/components/Layout";
import { AlertCircle, ArrowRight } from "lucide-react";

interface PlaceholderProps {
  title: string;
  description?: string;
}

export default function Placeholder({ title, description }: PlaceholderProps) {
  return (
    <Layout>
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="mb-6 inline-block">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-purple rounded-lg blur opacity-50"></div>
              <div className="relative bg-background p-4 rounded-lg">
                <AlertCircle className="w-12 h-12 text-neon-cyan mx-auto" />
              </div>
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-4 bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
            {title}
          </h1>
          <p className="text-foreground/60 mb-8">
            {description || "This page is coming soon. Ask me in the chat to build out this feature!"}
          </p>
          <div className="glass p-6 rounded-xl border border-white/20 mb-8">
            <p className="text-sm text-foreground/70">
              💡 Tip: Tell me what you'd like this page to do, and I'll build it out for you with the same modern cybersecurity aesthetic.
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <a
              href="/"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-neon-cyan to-neon-blue text-background font-semibold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all duration-300 hover:translate-y-[-2px]"
            >
              Back to Dashboard
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </Layout>
  );
}

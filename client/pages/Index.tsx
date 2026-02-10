import Layout from "@/components/Layout";
import { Shield, Zap, BarChart3, Users, ArrowRight, Lock, Eye, Radar } from "lucide-react";
import { Link } from "react-router-dom";

export default function Index() {
  return (
    <Layout>
      <div className="min-h-[calc(100vh-120px)]">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 px-4 sm:px-6 lg:px-8">
          {/* Animated background elements */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-20 left-10 w-96 h-96 bg-gradient-to-br from-neon-cyan/20 to-transparent rounded-full blur-3xl"></div>
            <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-tl from-neon-purple/20 to-transparent rounded-full blur-3xl"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-r from-neon-blue/10 via-transparent to-neon-cyan/10 rounded-full blur-3xl"></div>
          </div>

          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-12">
              {/* Badge */}
              <div className="inline-block glass px-4 py-2 rounded-full mb-6 border border-white/20">
                <p className="text-sm font-medium flex items-center gap-2">
                  <span className="w-2 h-2 bg-neon-cyan rounded-full animate-pulse"></span>
                  Advanced AI Detection Engine
                </p>
              </div>

              {/* Main Heading */}
              <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                <span className="block mb-2">Detect Fake Accounts</span>
                <span className="bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
                  Protect Your Platform
                </span>
              </h1>

              {/* Subheading */}
              <p className="text-lg md:text-xl text-foreground/60 max-w-3xl mx-auto mb-10 leading-relaxed">
                Secure Sphere uses advanced machine learning to identify fake social media accounts, bots, and fraudulent profiles in real-time. Protect your platform and users with enterprise-grade security.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/detection"
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-neon-cyan to-neon-blue text-background font-semibold rounded-lg hover:shadow-xl hover:shadow-cyan-500/50 transition-all duration-300 hover:translate-y-[-4px] group"
                >
                  Start Analysis
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>

              </div>
            </div>

            {/* Hero Card with Stats */}
            <div className="mt-16 glass p-8 border border-white/20 rounded-2xl overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan/5 via-transparent to-neon-purple/5 pointer-events-none"></div>
              <div className="relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                  <div>
                    <div className="text-4xl font-bold bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent mb-2">
                      99.7%
                    </div>
                    <p className="text-foreground/60">Accuracy Rate</p>
                  </div>
                  <div>
                    <div className="text-4xl font-bold bg-gradient-to-r from-neon-blue to-neon-purple bg-clip-text text-transparent mb-2">
                      1.2M+
                    </div>
                    <p className="text-foreground/60">Accounts Analyzed</p>
                  </div>
                  <div>
                    <div className="text-4xl font-bold bg-gradient-to-r from-neon-purple to-neon-cyan bg-clip-text text-transparent mb-2">
                      &lt;100ms
                    </div>
                    <p className="text-foreground/60">Response Time</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-4xl font-bold mb-4 text-center">
              Powerful Features
            </h2>
            <p className="text-lg text-foreground/60 max-w-2xl mx-auto text-center mb-16">
              Everything you need to identify and prevent fake accounts on social media platforms.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  icon: Radar,
                  title: "Real-time Detection",
                  description: "Instant analysis of social media accounts with advanced pattern recognition algorithms.",
                  color: "from-neon-cyan to-neon-blue",
                },
                {
                  icon: Lock,
                  title: "Enterprise Security",
                  description: "Bank-grade encryption and security protocols protecting your sensitive data.",
                  color: "from-neon-blue to-neon-purple",
                },
                {
                  icon: BarChart3,
                  title: "Detailed Analytics",
                  description: "Comprehensive reports with visual insights into account behavior and risk factors.",
                  color: "from-neon-purple to-neon-cyan",
                },
                {
                  icon: Eye,
                  title: "Behavioral Analysis",
                  description: "Deep learning models analyze posting patterns, engagement, and interaction anomalies.",
                  color: "from-neon-cyan to-neon-purple",
                },
                {
                  icon: Zap,
                  title: "Lightning Fast",
                  description: "Process thousands of accounts simultaneously with optimized performance.",
                  color: "from-neon-blue to-neon-cyan",
                },
                {
                  icon: Shield,
                  title: "24/7 Monitoring",
                  description: "Continuous tracking and alerts for suspicious account activities.",
                  color: "from-neon-purple to-neon-blue",
                },
              ].map((feature, idx) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={idx}
                    className="glass p-6 border border-white/20 rounded-xl hover:border-white/40 transition-all duration-300 hover:translate-y-[-8px] group"
                  >
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} p-3 mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-foreground/60">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-4xl font-bold mb-4 text-center">
              How It Works
            </h2>
            <p className="text-lg text-foreground/60 max-w-2xl mx-auto text-center mb-16">
              Our intelligent detection system analyzes multiple factors to identify fraudulent accounts.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                {
                  step: "01",
                  title: "Submit Account",
                  description: "Enter the social media handle or profile URL",
                },
                {
                  step: "02",
                  title: "Data Collection",
                  description: "System gathers public profile and activity data",
                },
                {
                  step: "03",
                  title: "AI Analysis",
                  description: "Machine learning models analyze patterns and behavior",
                },
                {
                  step: "04",
                  title: "Get Report",
                  description: "Receive detailed risk assessment and recommendations",
                },
              ].map((item, idx) => (
                <div key={idx} className="relative">
                  {idx < 3 && (
                    <div className="hidden md:block absolute top-12 -right-3 w-6 border-t-2 border-dashed border-white/20"></div>
                  )}
                  <div className="glass p-6 border border-white/20 rounded-xl text-center">
                    <div className="inline-block w-12 h-12 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue text-background font-bold text-lg mb-4 flex items-center justify-center">
                      {item.step}
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-foreground/60">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Target Users */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-4xl font-bold mb-4 text-center">
              Built for Security Teams
            </h2>
            <p className="text-lg text-foreground/60 max-w-2xl mx-auto text-center mb-16">
              Trusted by cyber security analysts, social media moderators, and enterprises worldwide.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: Shield,
                  title: "Security Analysts",
                  description:
                    "Monitor threats and identify coordinated fake account networks with advanced forensics.",
                },
                {
                  icon: Users,
                  title: "Social Media Moderators",
                  description:
                    "Quickly identify and report fraudulent profiles affecting community safety.",
                },
                {
                  icon: BarChart3,
                  title: "Organizations",
                  description:
                    "Protect brand reputation and ensure data integrity across social platforms.",
                },
              ].map((user, idx) => {
                const Icon = user.icon;
                return (
                  <div
                    key={idx}
                    className="glass p-8 border border-white/20 rounded-xl hover:border-neon-cyan/50 transition-all duration-300 hover:translate-y-[-8px] text-center"
                  >
                    <div className="relative inline-block mb-6">
                      <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-purple rounded-lg blur opacity-50"></div>
                      <div className="relative bg-background p-4 rounded-lg">
                        <Icon className="w-8 h-8 text-neon-cyan" />
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{user.title}</h3>
                    <p className="text-foreground/60 mb-6">{user.description}</p>
                    <a
                      href="#"
                      className="inline-flex items-center gap-2 text-neon-cyan hover:text-neon-blue transition-colors duration-300 font-medium"
                    >
                      Learn more
                      <ArrowRight className="w-4 h-4" />
                    </a>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}

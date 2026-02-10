import Layout from "@/components/Layout";
import { Search, CheckCircle, AlertTriangle, Target, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";

export default function Detection() {
  const [searchInput, setSearchInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);

  // Fetch recent analyses when component mounts
  useEffect(() => {
    fetchRecentAnalyses();
  }, []);

  const fetchRecentAnalyses = async () => {
    try {
      const baseUrl = import.meta.env.VITE_PUBLIC_BASE_URL || 'http://10.90.109.82:8000/';
      const response = await fetch(`${baseUrl}recent-analyze`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch recent analyses');
      }
      
      const data = await response.json();
      setRecentAnalyses(data.analyses || []);
    } catch (error) {
      console.error('Error fetching recent analyses:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!searchInput.trim()) {
      alert('Please enter a social media handle or URL');
      return;
    }

    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_PUBLIC_BASE_URL || 'http://10.90.109.82:8000/';
      const response = await fetch(`${baseUrl}analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: searchInput.trim() }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      console.log('Analysis result:', result);
      
      // Store the analysis result for display
      setAnalysisResult(result);
      
      // Fetch updated recent analyses after successful analysis
      await fetchRecentAnalyses();
      
    } catch (error) {
      console.error('Error during analysis:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to get risk level color
  const getRiskColor = (riskLevel) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'text-red-400';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-neon-cyan';
      default:
        return 'text-foreground/60';
    }
  };

  // Helper function to get risk background color
  const getRiskBgColor = (riskLevel) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'bg-red-900/20';
      case 'medium':
        return 'bg-yellow-900/20';
      case 'low':
        return 'bg-cyan-900/20';
      default:
        return 'bg-gray-900/20';
    }
  };

  return (
    <Layout>
      <div className="min-h-[calc(100vh-120px)]">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            {/* Animated background elements */}
            <div className="absolute top-10 right-0 w-96 h-96 bg-gradient-to-bl from-neon-cyan/20 to-transparent rounded-full blur-3xl -z-10"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-neon-purple/20 to-transparent rounded-full blur-3xl -z-10"></div>

            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
                Account Detection Engine
              </h1>
              <p className="text-lg text-foreground/60 max-w-2xl mx-auto">
                Analyze social media accounts for bot activity, fake profiles, and fraudulent behavior using advanced AI detection.
              </p>
            </div>

            {/* Search Interface */}
            <div className="max-w-2xl mx-auto mb-12">
              {/* Single Analysis Container */}
              <div className="glass p-8 border border-white/20 rounded-xl">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neon-cyan w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Enter social media handle or URL..."
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="w-full bg-white/5 border border-white/20 rounded-lg pl-12 pr-6 py-4 text-foreground placeholder-foreground/40 focus:outline-none focus:border-neon-cyan focus:bg-white/10 transition-all duration-300"
                  />
                </div>
                <button 
                  onClick={handleAnalyze}
                  disabled={isLoading || !searchInput.trim()}
                  className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-neon-cyan to-neon-blue text-background font-semibold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all duration-300 hover:translate-y-[-2px] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Analyzing...' : 'Analyze Account'}
                </button>
              </div>
              
              {/* Analysis Results */}
              {analysisResult && (
                <div className="mt-8 glass p-8 border border-white/20 rounded-xl">
                  <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                    <Target className="w-6 h-6 text-neon-cyan" />
                    Analysis Results
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    {/* Prediction & Risk Score */}
                    <div className="space-y-4">
                      <div className={`p-4 rounded-lg ${getRiskBgColor(analysisResult.confidence)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-foreground/80">Prediction</span>
                          {analysisResult.prediction === "Real Account" ? (
                            <CheckCircle className={`w-5 h-5 ${getRiskColor(analysisResult.confidence)}`} />
                          ) : (
                            <AlertTriangle className={`w-5 h-5 ${getRiskColor(analysisResult.confidence)}`} />
                          )}
                        </div>
                        <p className={`text-lg font-semibold ${getRiskColor(analysisResult.confidence)}`}>
                          {analysisResult.prediction}
                        </p>
                      </div>
                      
                      <div className="p-4 glass border border-white/10 rounded-lg">
                        <p className="text-sm text-foreground/60 mb-2">Risk Score</p>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 bg-white/10 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-500 ${
                                analysisResult.risk_score > 0.7 ? 'bg-red-400' :
                                analysisResult.risk_score > 0.4 ? 'bg-yellow-400' : 'bg-neon-cyan'
                              }`}
                              style={{ width: `${Math.round(analysisResult.risk_score * 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-lg font-bold text-foreground">
                            {Math.round(analysisResult.risk_score * 100)}%
                          </span>
                        </div>
                      </div>
                      
                      <div className="p-4 glass border border-white/10 rounded-lg">
                        <p className="text-sm text-foreground/60 mb-2">Confidence Level</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          analysisResult.confidence.toLowerCase() === 'high' ? 'bg-red-900/20 text-red-400' :
                          analysisResult.confidence.toLowerCase() === 'medium' ? 'bg-yellow-900/20 text-yellow-400' :
                          'bg-cyan-900/20 text-neon-cyan'
                        }`}>
                          {analysisResult.confidence}
                        </span>
                      </div>
                    </div>
                    
                    {/* Risk Factors & Analysis */}
                    <div className="space-y-4">
                      {/* Risk Factors */}
                      <div className="p-4 glass border border-white/10 rounded-lg">
                        <p className="text-sm text-foreground/60 mb-3">Risk Factors</p>
                        {analysisResult.risk_factors && analysisResult.risk_factors.length > 0 ? (
                          <ul className="space-y-2">
                            {analysisResult.risk_factors.map((factor, index) => (
                              <li key={index} className="flex items-start gap-2 text-sm">
                                <span className="text-yellow-400 mt-1">•</span>
                                <span className="text-foreground/80">{factor}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-foreground/50 text-sm">No specific risk factors identified</p>
                        )}
                      </div>
                      
                      {/* Flagged Words */}
                      <div className="p-4 glass border border-white/10 rounded-lg">
                        <p className="text-sm text-foreground/60 mb-3">Flagged Content</p>
                        {analysisResult.flagged_words && analysisResult.flagged_words.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {analysisResult.flagged_words.map((word, index) => (
                              <span key={index} className="px-2 py-1 bg-red-900/20 text-red-400 text-xs rounded">
                                {word}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-foreground/50 text-sm">No flagged content detected</p>
                        )}
                      </div>
                      
                      {/* Gemini Analysis */}
                      {analysisResult.gemini_analysis && (
                        <div className="p-4 glass border border-white/10 rounded-lg">
                          <p className="text-sm text-foreground/60 mb-3">AI Analysis</p>
                          <div className="text-sm text-foreground/70 max-h-32 overflow-y-auto">
                            {analysisResult.gemini_analysis.includes('error') || analysisResult.gemini_analysis.includes('failed') ? (
                              <p className="text-yellow-400">⚠️ AI Analysis temporarily unavailable</p>
                            ) : (
                              <p>{analysisResult.gemini_analysis}</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex justify-center">
                    <button 
                      onClick={() => setAnalysisResult(null)}
                      className="px-6 py-2 glass border border-white/20 text-foreground/70 hover:text-neon-cyan hover:border-white/40 rounded-lg transition-all duration-300"
                    >
                      Clear Results
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Recent Analyses */}
        <section className="py-16 px-4 sm:px-6 lg:px-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
              <Target className="w-6 h-6 text-neon-cyan" />
              Recent Analyses
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {recentAnalyses.length > 0 ? (
                recentAnalyses.map((analysis) => {
                  const riskColor = getRiskColor(analysis.risk_level);
                  const riskBgColor = getRiskBgColor(analysis.risk_level);
                  const confidenceScore = Math.round(analysis.risk_score * 100);
                  
                  return (
                    <div
                      key={analysis.id}
                      className="glass p-6 border border-white/20 rounded-xl hover:border-white/40 transition-all duration-300 hover:translate-y-[-4px] hover:shadow-lg group cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-lg mb-1">@{analysis.username}</h3>
                          <p className="text-sm text-foreground/50">Social Media</p>
                        </div>
                        <span className={`text-2xl font-bold group-hover:scale-110 transition-transform duration-300 ${riskColor}`}>
                          {confidenceScore}%
                        </span>
                      </div>

                      <div className={`p-3 rounded-lg mb-4 ${riskBgColor}`}>
                        <div className="flex items-center gap-2 mb-2">
                          {analysis.risk_level.toLowerCase() === "low" ? (
                            <CheckCircle className={`w-4 h-4 ${riskColor}`} />
                          ) : (
                            <AlertTriangle className={`w-4 h-4 ${riskColor}`} />
                          )}
                          <span className="font-medium">{analysis.risk_level} Risk</span>
                        </div>
                        <p className="text-sm text-foreground/70">{analysis.prediction}</p>
                      </div>

                      <p className="text-xs text-foreground/40">{analysis.time_ago}</p>
                    </div>
                  );
                })
              ) : (
                <div className="col-span-full text-center text-foreground/50 py-8">
                  <p>No recent analyses found. Start analyzing accounts to see results here.</p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
              <TrendingUp className="w-6 h-6 text-neon-cyan" />
              Detection Statistics
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { label: "Accounts Analyzed", value: "12,847", icon: "📊" },
                { label: "Fake Accounts Detected", value: "3,241", icon: "🚨" },
                { label: "Avg. Confidence", value: "94.2%", icon: "🎯" },
                { label: "Detection Rate", value: "99.7%", icon: "✓" },
              ].map((stat, idx) => (
                <div
                  key={idx}
                  className="glass p-6 border border-white/20 rounded-xl hover:border-neon-cyan/50 transition-all duration-300 hover:translate-y-[-4px] text-center"
                >
                  <div className="text-4xl mb-3">{stat.icon}</div>
                  <p className="text-sm text-foreground/60 mb-2">{stat.label}</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}

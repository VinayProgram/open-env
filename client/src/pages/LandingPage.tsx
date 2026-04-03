import { Link } from '@tanstack/react-router';
import { Button } from '../components/ui/button';
import { 
  Package, 
  Clock, 
  MessageCircle, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Zap,
  Shield,
  BarChart3
} from 'lucide-react';

export default function LandingPage() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="fixed w-full top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition">
              <Package className="w-8 h-8 text-blue-500" />
              <span className="text-xl font-bold text-white">PortFlow</span>
            </Link>
            <div className="hidden md:flex gap-8 items-center">
              <button onClick={() => scrollToSection('features')} className="text-slate-300 hover:text-white transition cursor-pointer">Features</button>
              <button onClick={() => scrollToSection('how-it-works')} className="text-slate-300 hover:text-white transition cursor-pointer">How It Works</button>
              <button onClick={() => scrollToSection('dashboard')} className="text-slate-300 hover:text-white transition cursor-pointer">Dashboard</button>
              <Button className="bg-blue-600 hover:bg-blue-700">Get Started</Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-10 right-10 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl"></div>
        </div>

        <div className="relative max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
                Manage Port <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">Delivery Complaints</span> Effortlessly
              </h1>
              <p className="text-xl text-slate-300 mb-8">
                Real-time complaint tracking, AI-powered customer service, and intelligent resolution system for port and logistics operations.
              </p>
              <div className="flex gap-4">
                <Button className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6 gap-2">
                  Start Free Trial <ArrowRight className="w-5 h-5" />
                </Button>
                <Button variant="outline" className="border-slate-600 text-black hover:bg-slate-700 text-lg px-8 py-6">
                  Watch Demo
                </Button>
              </div>
              <p className="text-slate-400 mt-6 text-sm">✓ No credit card required • ✓ 30-day free access • ✓ 24/7 Support</p>
            </div>
            
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl p-8 border border-slate-700/50 backdrop-blur">
                <div className="space-y-4">
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300 text-sm">Delivery #PRT-2024-001</span>
                      <span className="text-orange-400 text-xs font-semibold px-2 py-1 bg-orange-500/20 rounded">LATE</span>
                    </div>
                    <p className="text-white text-sm mb-3">Container delayed by 8 hours</p>
                    <div className="w-full bg-slate-700/50 rounded-full h-2 mb-2">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full" style={{width: '65%'}}></div>
                    </div>
                    <p className="text-slate-400 text-xs">Support ticket #SUP-89234 • Assigned to AI Agent</p>
                  </div>
                  
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                    <div className="flex items-center gap-2 mb-3">
                      <MessageCircle className="w-4 h-4 text-blue-400" />
                      <span className="text-slate-300 text-sm">AI Assistant Response</span>
                    </div>
                    <p className="text-slate-200 text-sm italic">
                      "We've identified the cause of the delay. Compensation of $500 is being processed..."
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/30 text-center">
                      <p className="text-blue-400 font-bold text-lg">94%</p>
                      <p className="text-slate-400 text-xs">Resolution Rate</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/30 text-center">
                      <p className="text-green-400 font-bold text-lg">2.5h</p>
                      <p className="text-slate-400 text-xs">Avg Response</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/30 text-center">
                      <p className="text-purple-400 font-bold text-lg">4.8★</p>
                      <p className="text-slate-400 text-xs">Satisfaction</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/50 border-y border-slate-700/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-xl text-slate-400">Everything you need to manage delivery complaints</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-blue-500/50 transition-all group">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-blue-500/30 transition">
                <Clock className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Real-Time Tracking</h3>
              <p className="text-slate-300">
                Monitor delivery status in real-time with instant updates and notifications for delays or issues.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-purple-500/50 transition-all group">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-purple-500/30 transition">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">AI-Powered Support</h3>
              <p className="text-slate-300">
                Intelligent assistant provides instant responses, analyzes complaints, and suggests resolutions.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-green-500/50 transition-all group">
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-green-500/30 transition">
                <TrendingUp className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Analytics & Insights</h3>
              <p className="text-slate-300">
                Comprehensive dashboards showing complaint trends, resolution rates, and customer satisfaction metrics.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-yellow-500/50 transition-all group">
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-yellow-500/30 transition">
                <MessageCircle className="w-6 h-6 text-yellow-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Multi-Channel Chat</h3>
              <p className="text-slate-300">
                Support customers across multiple channels with seamless conversation history and context.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-red-500/50 transition-all group">
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-red-500/30 transition">
                <AlertCircle className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Smart Escalation</h3>
              <p className="text-slate-300">
                Automatic escalation of complex issues to human agents based on severity and complexity.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-700/50 rounded-xl p-8 hover:border-indigo-500/50 transition-all group">
              <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:bg-indigo-500/30 transition">
                <Shield className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Enterprise Security</h3>
              <p className="text-slate-300">
                Bank-level encryption, role-based access control, and compliance with industry standards.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-xl text-slate-400">Three simple steps to resolve complaints faster</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-xl p-8 border border-blue-500/30 mb-8">
                <div className="text-4xl font-bold text-blue-400 mb-4">1</div>
                <h3 className="text-2xl font-bold text-white mb-4">Report Issue</h3>
                <p className="text-slate-300 mb-4">
                  Customer reports a late delivery or complaint through the portal or chat interface.
                </p>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                    Easy complaint submission
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                    Attach documents/photos
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
                    Instant confirmation
                  </li>
                </ul>
              </div>
              {/* Arrow */}
              <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                  <ArrowRight className="w-5 h-5 text-slate-300" />
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl p-8 border border-purple-500/30 mb-8">
                <div className="text-4xl font-bold text-purple-400 mb-4">2</div>
                <h3 className="text-2xl font-bold text-white mb-4">AI Analysis</h3>
                <p className="text-slate-300 mb-4">
                  Our AI system analyzes the complaint, validates claims, and proposes solutions.
                </p>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-400 flex-shrink-0" />
                    Intelligent categorization
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-400 flex-shrink-0" />
                    Root cause analysis
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-400 flex-shrink-0" />
                    Compensation calculation
                  </li>
                </ul>
              </div>
              {/* Arrow */}
              <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                  <ArrowRight className="w-5 h-5 text-slate-300" />
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative">
              <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-xl p-8 border border-green-500/30 mb-8">
                <div className="text-4xl font-bold text-green-400 mb-4">3</div>
                <h3 className="text-2xl font-bold text-white mb-4">Quick Resolution</h3>
                <p className="text-slate-300 mb-4">
                  Issue is resolved through compensation, service credits, or escalation to human agents.
                </p>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    Automated compensation
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    Customer satisfaction survey
                  </li>
                  <li className="flex gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    Follow-up support
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview Section */}
      <section id="dashboard" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/50 border-y border-slate-700/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Advanced Dashboard</h2>
            <p className="text-xl text-slate-400">Complete visibility into your complaint management system</p>
          </div>

          <div className="bg-gradient-to-br from-slate-700/30 to-slate-800/30 border border-slate-700/50 rounded-2xl p-8 overflow-hidden">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                <p className="text-slate-400 text-sm mb-1">Total Complaints</p>
                <p className="text-3xl font-bold text-white">2,847</p>
                <p className="text-green-400 text-xs mt-2">↑ 12% this month</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                <p className="text-slate-400 text-sm mb-1">Resolved</p>
                <p className="text-3xl font-bold text-white">2,677</p>
                <p className="text-green-400 text-xs mt-2">94% resolution rate</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                <p className="text-slate-400 text-sm mb-1">Avg Resolution Time</p>
                <p className="text-3xl font-bold text-white">2.5h</p>
                <p className="text-green-400 text-xs mt-2">↓ -23% vs last month</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/30">
                <p className="text-slate-400 text-sm mb-1">Customer Satisfaction</p>
                <p className="text-3xl font-bold text-white">4.8★</p>
                <p className="text-green-400 text-xs mt-2">↑ 0.3 points</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Chart placeholder */}
              <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  Complaints Over Time
                </h3>
                <div className="h-40 flex items-end gap-2 justify-around">
                  {[40, 65, 45, 70, 55, 80, 75, 90, 85].map((height, i) => (
                    <div key={i} className="flex-1 bg-gradient-to-t from-blue-500 to-blue-400 rounded-t" style={{height: `${height}%`}}></div>
                  ))}
                </div>
              </div>

              {/* Recent complaints */}
              <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-4">Recent Complaints</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded">
                    <div>
                      <p className="text-white text-sm font-medium">#DEL-089234</p>
                      <p className="text-slate-400 text-xs">Late delivery - 8 hours</p>
                    </div>
                    <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded">Resolved</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded">
                    <div>
                      <p className="text-white text-sm font-medium">#DEL-089233</p>
                      <p className="text-slate-400 text-xs">Damaged container</p>
                    </div>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded">In Progress</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded">
                    <div>
                      <p className="text-white text-sm font-medium">#DEL-089232</p>
                      <p className="text-slate-400 text-xs">Wrong consignee</p>
                    </div>
                    <span className="px-2 py-1 bg-yellow-500/20 text-yellow-300 text-xs rounded">Escalated</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Complaint Management?
          </h2>
          <p className="text-xl text-slate-300 mb-10">
            Join thousands of port operators who trust PortFlow to manage their delivery complaints efficiently and effectively.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6 gap-2">
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Button>
            <Button variant="outline" className="border-slate-600 text-dark hover:bg-slate-700 text-lg px-8 py-6">
              Contact Sales
            </Button>
          </div>
          <p className="text-slate-400 mt-8 text-sm">
            Enterprise plans available • Dedicated support • Custom integrations
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900/50 border-t border-slate-700/50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <Link to="/" className="flex items-center gap-2 mb-4 hover:opacity-80 transition w-fit">
                <Package className="w-6 h-6 text-blue-500" />
                <span className="font-bold text-white">PortFlow</span>
              </Link>
              <p className="text-slate-400 text-sm">
                Advanced complaint management system for port and logistics operations.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><button onClick={() => scrollToSection('features')} className="hover:text-white transition cursor-pointer">Features</button></li>
                <li><span className="hover:text-white transition">Pricing</span></li>
                <li><span className="hover:text-white transition">Security</span></li>
                <li><span className="hover:text-white transition">Documentation</span></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><span className="hover:text-white transition">About</span></li>
                <li><span className="hover:text-white transition">Blog</span></li>
                <li><span className="hover:text-white transition">Careers</span></li>
                <li><span className="hover:text-white transition">Contact</span></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><span className="hover:text-white transition">Privacy</span></li>
                <li><span className="hover:text-white transition">Terms</span></li>
                <li><span className="hover:text-white transition">Compliance</span></li>
                <li><span className="hover:text-white transition">Sitemap</span></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-700/50 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center text-slate-400 text-sm">
              <p>&copy; 2024 PortFlow. All rights reserved.</p>
              <div className="flex gap-6 mt-4 md:mt-0">
                <span className="hover:text-white transition cursor-pointer">Twitter</span>
                <span className="hover:text-white transition cursor-pointer">LinkedIn</span>
                <span className="hover:text-white transition cursor-pointer">GitHub</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

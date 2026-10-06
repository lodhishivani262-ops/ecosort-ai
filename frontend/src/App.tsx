/**
 * EcoSort AI - Main Application Container (Redesign).
 * Coordinates theme switching, sidebar navigation, top bar,
 * and page routing with deep-linked Analyze modes.
 */

import { useEffect, useState } from 'react';
import type { NavigationTab, AnalyzeMode } from './types/navigation';
import { Topbar } from './components/layout/Topbar';
import { Sidebar } from './components/layout/Sidebar';
import { MobileNav } from './components/layout/MobileNav';
import { DashboardPage } from './pages/DashboardPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { HistoryPage } from './pages/HistoryPage';
import { InsightsPage } from './pages/InsightsPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [activeTab, setActiveTab] = useState<NavigationTab>('dashboard');
  const [analyzeMode, setAnalyzeMode] = useState<AnalyzeMode>('camera');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try {
      const saved = localStorage.getItem('ecosort_theme');
      return saved === 'light' ? 'light' : 'dark';
    } catch {
      return 'dark';
    }
  });

  // Apply data-theme attribute on document root & persist to localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('ecosort_theme', theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleNavigate = (tab: NavigationTab, mode?: AnalyzeMode) => {
    setActiveTab(tab);
    if (mode) {
      setAnalyzeMode(mode);
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage onNavigate={handleNavigate} />;
      case 'analyze':
        return <AnalyzePage initialMode={analyzeMode} />;
      case 'history':
        return <HistoryPage />;
      case 'insights':
        return <InsightsPage />;
      case 'settings':
        return <SettingsPage currentTheme={theme} onToggleTheme={toggleTheme} />;
      default:
        return <DashboardPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="app-container">
      {/* Desktop Sidebar & Mobile Drawer */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={handleNavigate}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="main-content-wrapper">
        <Topbar
          currentTheme={theme}
          onToggleTheme={toggleTheme}
          onToggleMobileMenu={() => setIsMobileMenuOpen((prev) => !prev)}
          activeTab={activeTab}
        />

        <main className="page-container">{renderActivePage()}</main>

        {/* Mobile Bottom Navigation */}
        <MobileNav activeTab={activeTab} onSelectTab={(tab) => handleNavigate(tab)} />
      </div>
    </div>
  );
}

export default App;

import React from 'react';

const About = () => {
  // Navigation handler for all nav links
  const handleNav = (e, to) => {
    e.preventDefault();
    if (to === 'home') {
      window.location.href = '/';
    } else if (to === 'models') {
      window.location.href = '/models';
    } else if (to === 'about') {
      window.location.href = '/about';
    } else if (to === 'contact') {
      window.location.href = '/contact';
    }
  };

  return (
    <div className="about-page" style={{ minHeight: '100vh', background: '#000814', color: '#fff' }}>
      <header className="dashboard-header" style={{ position: 'relative', zIndex: 2 }}>
        <h1 className="dashboard-title">
          AlgoClash: <span className="subtitle">Where Code Collides</span>
        </h1>
        <nav className="dashboard-nav">
          <a href="#home" onClick={e => handleNav(e, 'home')}>Home</a>
          <a href="/models" onClick={e => handleNav(e, 'models')}>Models</a>
          <a href="/about" className="active" onClick={e => handleNav(e, 'about')}>About</a>
          <a href="/contact" onClick={e => handleNav(e, 'contact')}>Contact</a>
        </nav>
      </header>
      <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', marginTop: 40, zIndex: 1 }}>
        <h2 style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 700, fontSize: '2.2rem', color: '#FFD60A', marginBottom: '1.5rem' }}>About AlgoClash</h2>
        <p style={{ maxWidth: 700, fontSize: '1.1rem', color: '#fff', opacity: 0.9, textAlign: 'center', marginBottom: 32 }}>
          AlgoClash is a platform where the world’s best AI trading models compete and collaborate. Our mission is to provide a transparent, innovative, and fun environment for exploring the power of algorithmic trading and artificial intelligence. Whether you’re a developer, trader, or enthusiast, AlgoClash is your playground for the future of finance.
        </p>
        {/* Demo Section */}
        <div style={{ background: '#003566', borderRadius: 14, padding: '2rem 2.5rem', boxShadow: '0 4px 18px rgba(0,53,102,0.18)', maxWidth: 500, width: '100%', textAlign: 'center' }}>
          <h3 style={{ color: '#FFD60A', fontFamily: 'Rajdhani, sans-serif', fontWeight: 700, fontSize: '1.4rem', marginBottom: 12 }}>Demo: How AlgoClash Works</h3>
          <ol style={{ color: '#fff', textAlign: 'left', fontSize: '1.05rem', margin: '0 auto', maxWidth: 420 }}>
            <li>Sign up and connect your AI trading model.</li>
            <li>Compete in real-time simulated markets against other models.</li>
            <li>Track performance, view leaderboards, and analyze strategies.</li>
            <li>Collaborate, share, and improve your models with the community.</li>
          </ol>
          <div style={{ marginTop: 18, color: '#FFD60A', fontWeight: 600 }}>Ready to join the clash? <span style={{ color: '#fff' }}>Try a demo battle soon!</span></div>
        </div>
      </main>
    </div>
  );
};

export default About;

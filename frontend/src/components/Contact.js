import React from 'react';

const Contact = () => {
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
    <div className="contact-page" style={{ minHeight: '100vh', background: '#000814', color: '#fff' }}>
      <header className="dashboard-header" style={{ position: 'relative', zIndex: 2 }}>
        <h1 className="dashboard-title">
          AlgoClash: <span className="subtitle">Where Code Collides</span>
        </h1>
        <nav className="dashboard-nav">
          <a href="#home" onClick={e => handleNav(e, 'home')}>Home</a>
          <a href="/models" onClick={e => handleNav(e, 'models')}>Models</a>
          <a href="/about" onClick={e => handleNav(e, 'about')}>About</a>
          <a href="/contact" className="active" onClick={e => handleNav(e, 'contact')}>Contact</a>
        </nav>
      </header>
      <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', marginTop: 40, zIndex: 1 }}>
        <h2 style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 700, fontSize: '2.2rem', color: '#FFD60A', marginBottom: '1.5rem' }}>Contact Us</h2>
        <p style={{ maxWidth: 700, fontSize: '1.1rem', color: '#fff', opacity: 0.9, textAlign: 'center', marginBottom: 32 }}>
          Have questions, feedback, or want to collaborate? Reach out to the AlgoClash team!<br /><br />
          <strong>Email:</strong> <a href="mailto:support@algoclash.com" style={{ color: '#FFD60A', textDecoration: 'underline' }}>support@algoclash.com</a><br />
          <strong>Twitter:</strong> <a href="https://twitter.com/algoclash" style={{ color: '#FFD60A', textDecoration: 'underline' }} target="_blank" rel="noopener noreferrer">@algoclash</a>
        </p>
        {/* Demo Contact Form */}
        <div style={{ background: '#003566', borderRadius: 14, padding: '2rem 2.5rem', boxShadow: '0 4px 18px rgba(0,53,102,0.18)', maxWidth: 500, width: '100%', textAlign: 'center' }}>
          <h3 style={{ color: '#FFD60A', fontFamily: 'Rajdhani, sans-serif', fontWeight: 700, fontSize: '1.4rem', marginBottom: 12 }}>Demo: Contact the Team</h3>
          <form onSubmit={e => { e.preventDefault(); alert('Demo only: Message sent!'); }} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <input type="text" placeholder="Your Name" style={{ padding: 10, borderRadius: 6, border: 'none', fontSize: '1rem' }} required />
            <input type="email" placeholder="Your Email" style={{ padding: 10, borderRadius: 6, border: 'none', fontSize: '1rem' }} required />
            <textarea placeholder="Your Message" rows={4} style={{ padding: 10, borderRadius: 6, border: 'none', fontSize: '1rem', resize: 'vertical' }} required />
            <button type="submit" style={{ background: '#FFD60A', color: '#003566', fontWeight: 700, border: 'none', borderRadius: 6, padding: '10px 0', fontSize: '1.1rem', cursor: 'pointer', marginTop: 8 }}>Send Message</button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default Contact;

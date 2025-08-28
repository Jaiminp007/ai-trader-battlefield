import React, { useState } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [navOpen, setNavOpen] = useState(false);
  const [active, setActive] = useState('home');

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
    <div className="dashboard">
      {/* Header Title */}
      <header className="dashboard-header">
        <h1 className="dashboard-title">
          AlgoClash: <span className="subtitle">Where Code Collides</span>
        </h1>
        <nav className="dashboard-nav">
          <a
            href="#home"
            className={active === 'home' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'home');
              setActive('home');
            }}
          >
            Home
          </a>
          <a
            href="/models"
            className={active === 'models' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'models');
              setActive('models');
            }}
          >
            Models
          </a>
          <a
            href="/about"
            className={active === 'about' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'about');
              setActive('about');
            }}
          >
            About
          </a>
          <a
            href="/contact"
            className={active === 'contact' ? 'active' : ''}
            onClick={e => {
              handleNav(e, 'contact');
              setActive('contact');
            }}
          >
            Contact
          </a>
        </nav>
      </header>

      {/* Main Content Area */}
      <div className="dashboard-content">
        {/* Left Side Elements */}
        <div className="side-element left-element left-element-1">
          <div className="side-circle left-circle"></div>
        </div>
        <div className="side-element left-element left-element-2">
          <div className="side-circle left-circle"></div>
        </div>
        <div className="side-element left-element left-element-3">
          <div className="side-circle left-circle"></div>
        </div>

        {/* Center Blue Box */}
        <div className="center-box"></div>

        {/* Right Side Elements */}
        <div className="side-element right-element right-element-1">
          <div className="side-circle right-circle"></div>
        </div>
        <div className="side-element right-element right-element-2">
          <div className="side-circle right-circle"></div>
        </div>
        <div className="side-element right-element right-element-3">
          <div className="side-circle right-circle"></div>
        </div>

        {/* Start Button */}
        <button className="start-button">
          START
        </button>
      </div>
    </div>
  );
};

export default Dashboard;

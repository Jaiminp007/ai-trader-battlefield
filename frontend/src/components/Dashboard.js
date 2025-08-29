import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import CustomDropdown from './CustomDropdown'; // Import the new component

const Dashboard = () => {
  const [navOpen, setNavOpen] = useState(false);
  const [active, setActive] = useState('home');
  const [agents, setAgents] = useState({});
  const [selectedAgents, setSelectedAgents] = useState({
    'left-1': null,
    'left-2': null,
    'left-3': null,
    'right-1': null,
    'right-2': null,
    'right-3': null,
  });

  useEffect(() => {
    fetch('/api/ai_agents')
      .then(response => response.json())
      .then(data => setAgents(data))
      .catch(error => console.error('Error fetching agents:', error));
  }, []);

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

  const handleAgentSelect = (id, agent) => {
    setSelectedAgents(prev => ({ ...prev, [id]: agent }));
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
        {[1, 2, 3].map(i => (
          <React.Fragment key={i}>
            <div className={`side-element left-element left-element-${i}`}>
              <div className="side-circle left-circle">
                <CustomDropdown 
                  agents={agents} 
                  selected={selectedAgents[`left-${i}`]} 
                  onSelect={(agent) => handleAgentSelect(`left-${i}`, agent)}
                />
              </div>
            </div>
            <div className={`side-element right-element right-element-${i}`}>
              <div className="side-circle right-circle">
                <CustomDropdown 
                  agents={agents} 
                  selected={selectedAgents[`right-${i}`]} 
                  onSelect={(agent) => handleAgentSelect(`right-${i}`, agent)}
                />
              </div>
            </div>
          </React.Fragment>
        ))}

        {/* Center Blue Box */}
        <div className="center-box"></div>

        {/* Start Button */}
        <button className="start-button">
          START
        </button>
      </div>
    </div>
  );
};

export default Dashboard;

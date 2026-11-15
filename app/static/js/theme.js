// Theme and UI interaction controller
document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Toggle
  const themeBtn = document.getElementById('theme-toggle-btn');
  const htmlRoot = document.documentElement;

  // Retrieve saved theme or prefer dark
  const savedTheme = localStorage.getItem('omni_theme') || 'dark';
  htmlRoot.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const currentTheme = htmlRoot.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      htmlRoot.setAttribute('data-theme', newTheme);
      localStorage.setItem('omni_theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeBtn) return;
    themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    themeBtn.setAttribute('title', theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme');
  }

  // 2. Consent Banner Management
  const consentBanner = document.getElementById('consent-banner');
  const acceptConsentBtn = document.getElementById('accept-consent-btn');
  const rejectConsentBtn = document.getElementById('reject-consent-btn');

  if (consentBanner) {
    const hasConsented = localStorage.getItem('omni_gdpr_consent');
    if (!hasConsented) {
      consentBanner.style.display = 'flex';
    } else {
      consentBanner.style.display = 'none';
    }

    if (acceptConsentBtn) {
      acceptConsentBtn.addEventListener('click', () => {
        localStorage.setItem('omni_gdpr_consent', 'accepted');
        consentBanner.style.display = 'none';
        // Enable ads if loaded
        if (window.adsbygoogle) {
          try { (adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
        }
      });
    }

    if (rejectConsentBtn) {
      rejectConsentBtn.addEventListener('click', () => {
        localStorage.setItem('omni_gdpr_consent', 'rejected');
        consentBanner.style.display = 'none';
      });
    }
  }

  // 3. Country / Language switchers
  const countrySelect = document.getElementById('country-switcher');
  if (countrySelect) {
    countrySelect.addEventListener('change', (e) => {
      const parts = window.location.pathname.split('/').filter(Boolean);
      const newCountry = e.target.value;
      const currentLang = parts[1] || 'en';
      const currentSlug = parts[2] || '';
      if (currentSlug) {
        window.location.href = `/${newCountry}/${currentLang}/${currentSlug}/`;
      } else {
        window.location.href = `/${newCountry}/${currentLang}/`;
      }
    });
  }

  const langSelect = document.getElementById('lang-switcher');
  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      const parts = window.location.pathname.split('/').filter(Boolean);
      const currentCountry = parts[0] || 'fi';
      const newLang = e.target.value;
      const currentSlug = parts[2] || '';
      if (currentSlug) {
        window.location.href = `/${currentCountry}/${newLang}/${currentSlug}/`;
      } else {
        window.location.href = `/${currentCountry}/${newLang}/`;
      }
    });
  }
});

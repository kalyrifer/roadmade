import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button, Card, Input } from '../components/ui';
import styles from './HomePage.module.css';

function HomePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [date, setDate] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/trips?from_city=${encodeURIComponent(from)}&to_city=${encodeURIComponent(to)}&date=${date}`);
  };

  return (
    <div className={styles.container}>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.title}>{t('home.title')}</h1>
          <p className={styles.subtitle}>{t('home.subtitle')}</p>
          
          {/* Search Form */}
          <Card className={styles.searchCard}>
            <form onSubmit={handleSearch} className={styles.searchForm}>
              <div className={styles.searchInputs}>
                <div className={styles.inputGroup}>
                  <Input
                    type="text"
                    placeholder={t('home.fromPlaceholder')}
                    value={from}
                    onChange={(e) => setFrom(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.inputGroup}>
                  <Input
                    type="text"
                    placeholder={t('home.toPlaceholder')}
                    value={to}
                    onChange={(e) => setTo(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.inputGroup}>
                  <Input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                  />
                </div>
              </div>
              <Button type="submit" variant="primary" size="lg" className={styles.searchButton}>
                {t('home.search')}
              </Button>
            </form>
          </Card>
        </div>
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <div className={styles.featuresGrid}>
          <Card className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <h3>{t('home.feature1Title')}</h3>
            <p>{t('home.feature1Desc')}</p>
          </Card>
          <Card className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <h3>{t('home.feature2Title')}</h3>
            <p>{t('home.feature2Desc')}</p>
          </Card>
          <Card className={styles.featureCard}>
            <div className={styles.featureIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
                <line x1="1" y1="10" x2="23" y2="10"/>
              </svg>
            </div>
            <h3>{t('home.feature3Title')}</h3>
            <p>{t('home.feature3Desc')}</p>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.cta}>
        <h2>{t('home.ctaTitle')}</h2>
        <p>{t('home.ctaDesc')}</p>
        <div className={styles.ctaButtons}>
          <Button variant="primary" size="lg" onClick={() => navigate('/trips/new')}>
            {t('home.offerRide')}
          </Button>
          <Button variant="outline" size="lg" onClick={() => navigate('/trips')}>
            {t('home.findRide')}
          </Button>
        </div>
      </section>
    </div>
  );
}

export default HomePage;

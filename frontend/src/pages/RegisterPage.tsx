import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { Button, Input, Card } from '../components/ui';
import { authApi } from '../services/api/auth';
import styles from './LoginPage.module.css';

interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
  phone?: string;
}

export default function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterForm>();
  const password = watch('password');

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      navigate('/');
    },
    onError: (err: Error) => {
      setError(err.message || t('errors.registerFailed'));
    },
  });

  const onSubmit = (data: RegisterForm) => {
    setError('');
    const { confirmPassword, ...registerData } = data;
    // Send data matching backend UserRegisterRequest schema
    const apiData = {
      email: registerData.email,
      password: registerData.password,
      name: registerData.name,
    };
    registerMutation.mutate(apiData);
  };

  return (
    <div className={styles.container}>
      <Card className={styles.card}>
        <h1 className={styles.title}>{t('auth.register')}</h1>
        <p className={styles.subtitle}>{t('auth.registerSubtitle')}</p>

        <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <Input
            label={t('auth.name')}
            type="text"
            placeholder={t('auth.namePlaceholder')}
            {...register('name', { required: t('errors.required') })}
            error={errors.name?.message}
          />

          <Input
            label={t('auth.email')}
            type="email"
            placeholder={t('auth.emailPlaceholder')}
            {...register('email', { 
              required: t('errors.required'),
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: t('errors.invalidEmail')
              }
            })}
            error={errors.email?.message}
          />

          <Input
            label={t('auth.phone')}
            type="tel"
            placeholder={t('auth.phonePlaceholder')}
            {...register('phone')}
          />

          <Input
            label={t('auth.password')}
            type="password"
            placeholder={t('auth.passwordPlaceholder')}
            {...register('password', { 
              required: t('errors.required'),
              minLength: {
                value: 6,
                message: t('errors.passwordMinLength')
              }
            })}
            error={errors.password?.message}
          />

          <Input
            label={t('auth.confirmPassword')}
            type="password"
            placeholder={t('auth.confirmPasswordPlaceholder')}
            {...register('confirmPassword', { 
              required: t('errors.required'),
              validate: (value) => 
                value === password || t('errors.passwordMismatch')
            })}
            error={errors.confirmPassword?.message}
          />

          <Button 
            type="submit" 
            variant="primary" 
            loading={registerMutation.isPending}
            className={styles.submitButton}
          >
            {t('auth.register')}
          </Button>
        </form>

        <p className={styles.footer}>
          {t('auth.hasAccount')}{' '}
          <Link to="/login" className={styles.link}>
            {t('auth.login')}
          </Link>
        </p>
      </Card>
    </div>
  );
}

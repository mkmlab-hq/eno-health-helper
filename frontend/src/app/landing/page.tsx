import React from 'react';
import Header from '@/components/landing/Header';
import Hero from '@/components/landing/Hero';
import Features from '@/components/landing/Features';
import Products from '@/components/landing/Products';
import Footer from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <div className="bg-slate-950">
      <Header />
      <main>
        <Hero />
        <Features />
        <Products />
      </main>
      <Footer />
    </div>
  );
}

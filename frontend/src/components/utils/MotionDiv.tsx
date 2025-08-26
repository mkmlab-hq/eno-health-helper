'use client';

import React from 'react';

type Props = React.HTMLAttributes<HTMLDivElement> & {
  children: React.ReactNode;
};

export function MotionDiv({ children, className, ...rest }: Props) {
  return (
    <div
      className={`transition-all duration-700 ease-out opacity-0 translate-y-8 will-change-transform [animation:fadeUp_0.8s_ease-out_forwards] ${className || ''}`}
      {...rest}
    >
      {children}
      <style jsx>{`
        @keyframes fadeUp {
          0% { opacity: 0; transform: translateY(30px); }
          100% { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}


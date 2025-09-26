import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const spinnerVariants = cva(
  'animate-spin',
  {
    variants: {
      size: {
        sm: 'h-4 w-4',
        default: 'h-6 w-6',
        lg: 'h-8 w-8',
        xl: 'h-12 w-12',
        '2xl': 'h-16 w-16',
      },
      spinnerColor: {
        default: 'text-eno-600',
        white: 'text-white',
        gray: 'text-gray-600',
        red: 'text-red-600',
        green: 'text-green-600',
        blue: 'text-blue-600',
      },
    },
    defaultVariants: {
      size: 'default',
      spinnerColor: 'default',
    },
  }
);

export interface SpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  label?: string;
}

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size, spinnerColor, label = 'Loading...', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex flex-col items-center justify-center', className)}
        role="status"
        aria-label={label}
        {...props}
      >
        <svg
          className={cn(spinnerVariants({ size, spinnerColor }))}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        {label && (
          <span className="sr-only">{label}</span>
        )}
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

// 특정 용도별 Spinner 컴포넌트들
export const PageSpinner = () => (
  <div className="min-h-screen flex items-center justify-center">
    <Spinner size="2xl" />
  </div>
);

export const ButtonSpinner = () => (
  <Spinner size="sm" spinnerColor="white" />
);

export const CardSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <Spinner size="lg" />
  </div>
);

export { Spinner, spinnerVariants };

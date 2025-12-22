import Image from 'next/image';
import Link from 'next/link';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  linkTo?: string;
  variant?: 'image' | 'text';
}

const sizeMap = {
  sm: 'text-2xl',
  md: 'text-3xl',
  lg: 'text-5xl',
  xl: 'text-6xl'
};

export default function Logo({ size = 'md', className = '', linkTo = '/', variant = 'text' }: LogoProps) {
  const logo = variant === 'image' ? (
    <img 
      src="/images/Next Logo.png" 
      alt="NextCI - Career Intelligence" 
      className={`h-auto w-auto ${className}`}
      style={{ height: size === 'sm' ? '40px' : size === 'md' ? '60px' : '100px' }}
    />
  ) : (
    <span className={`font-serif font-bold tracking-tight text-premium-accent ${sizeMap[size]} ${className}`}>
      NextCI
    </span>
  );

  if (linkTo) {
    return (
      <Link href={linkTo} className="inline-block hover:opacity-90 transition-opacity">
        {logo}
      </Link>
    );
  }

  return logo;
}

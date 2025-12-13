import Image from 'next/image';
import Link from 'next/link';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  linkTo?: string;
}

const sizeMap = {
  sm: 'h-8 md:h-10',     // Reduced for cleaner navbar
  md: 'h-14 md:h-16',    // Medium size
  lg: 'h-20 md:h-24',    // Large for landing page
  xl: 'h-24 md:h-28'     // Extra large
};

export default function Logo({ size = 'md', className = '', linkTo = '/' }: LogoProps) {
  const logo = (
    <img
      src="/images/Next Logo.png"
      alt="NEXT - Career Intelligence"
      className={`${sizeMap[size]} w-auto ${className}`}
    />
  );

  if (linkTo) {
    return (
      <Link href={linkTo} className="inline-block">
        {logo}
      </Link>
    );
  }

  return logo;
}

import Image from 'next/image';
import Link from 'next/link';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  linkTo?: string;
}

const sizeConfig = {
  sm: { height: 32, width: 108, className: 'h-8 md:h-10' },   // Reduced for cleaner navbar
  md: { height: 56, width: 189, className: 'h-14 md:h-16' },  // Medium size
  lg: { height: 80, width: 270, className: 'h-20 md:h-24' },  // Large for landing page
  xl: { height: 96, width: 324, className: 'h-24 md:h-28' }   // Extra large
};

export default function Logo({ size = 'md', className = '', linkTo = '/' }: LogoProps) {
  const config = sizeConfig[size];

  const logo = (
    <Image
      src="/images/Next Logo.png"
      alt="NEXT - Career Intelligence"
      width={config.width}
      height={config.height}
      className={`w-auto ${config.className} ${className}`}
      priority={size === 'lg' || size === 'xl'} // Priority loading for large hero logos
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

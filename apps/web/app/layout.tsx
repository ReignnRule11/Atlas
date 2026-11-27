import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Atlas — Professional Economy Infrastructure', description: 'Turn professional capability into economic opportunity.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }

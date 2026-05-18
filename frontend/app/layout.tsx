import type { Metadata } from "next";
import { JetBrains_Mono, Geist } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PARASITE EVOLVED",
  description: "Biological-inspired AI parasite that infiltrates codebases and reveals lethal attack paths.",
};

import { PersonalityProvider } from '@/lib/PersonalityContext';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("dark", "font-sans", geist.variable)}>
      <body className={`${jetbrainsMono.className} bg-void text-text-primary antialiased min-h-screen flex flex-col`}>
        <PersonalityProvider>
          {children}
        </PersonalityProvider>
      </body>
    </html>
  );
}

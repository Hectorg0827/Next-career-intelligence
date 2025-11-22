'use client';

import SkillGraph from '@/components/coach/SkillGraph';

export default function SkillsPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <SkillGraph />
            </div>
        </div>
    );
}

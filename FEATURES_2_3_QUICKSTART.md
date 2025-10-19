# 🚀 Quick Start: Features 2 & 3

## Feature 2: Career Roadmaps (5 minutes)

### 1. Test the API

```bash
curl -X POST http://localhost:8000/api/roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "skills": ["Python", "JavaScript", "React"],
    "years_experience": 3,
    "location": "Remote"
  }' | jq '.career_roadmap.3_year.primary_path.target_role'
```

**Expected output:** A target role for 3 years from now

### 2. Use in Your App

```tsx
import { CareerRoadmapTimeline } from '@/components/CareerRoadmap';

export default async function RoadmapPage() {
  // Fetch roadmap data
  const response = await fetch('/api/roadmap', {
    method: 'POST',
    body: JSON.stringify({
      job_title: "Data Analyst",
      skills: ["Python", "SQL"],
      years_experience: 2
    })
  });
  
  const data = await response.json();
  
  return (
    <CareerRoadmapTimeline 
      roadmap={data.career_roadmap}
      currentRole={data.job_title}
    />
  );
}
```

---

## Feature 3: Explainable AI (2 minutes)

### 1. Import Component

```tsx
import { ExplanationPanel, WhyIcon } from '@/components/ExplainableAI';
```

### 2. Add "Why?" Buttons

```tsx
// Option 1: Compact button
<ExplanationPanel 
  explanation="This skill is in high demand because..."
  variant="button"
/>

// Option 2: Always visible
<ExplanationPanel 
  explanation="We recommend this path because..."
  variant="inline"
/>

// Option 3: Full-width accordion
<ExplanationPanel 
  title="Why this recommendation?"
  explanation="Based on your profile..."
  variant="accordion"
/>

// Option 4: Inline tooltip icon
<span>
  Machine Learning
  <WhyIcon explanation="ML jobs grew 45% in 2024" />
</span>
```

---

## Integration Example

### Add Both Features to Analysis Results

```tsx
import { CareerRoadmapTimeline } from '@/components/CareerRoadmap';
import { ExplanationPanel } from '@/components/ExplainableAI';

export default function AnalysisPage({ data }) {
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [roadmap, setRoadmap] = useState(null);

  const loadRoadmap = async () => {
    const res = await fetch('/api/roadmap', { /* ... */ });
    const data = await res.json();
    setRoadmap(data.career_roadmap);
    setShowRoadmap(true);
  };

  return (
    <div className="space-y-8">
      {/* Risk Analysis */}
      <div>
        <h2>AI Displacement Risk: {data.risk_level}</h2>
        <ExplanationPanel 
          explanation={data.risk_reasoning}
          variant="accordion"
        />
      </div>

      {/* Career Roadmap */}
      <button onClick={loadRoadmap}>
        🗺️ Generate Career Roadmap
      </button>
      
      {showRoadmap && roadmap && (
        <CareerRoadmapTimeline 
          roadmap={roadmap}
          currentRole={data.job_title}
        />
      )}
    </div>
  );
}
```

---

## Customization

### Change Roadmap Colors

Edit `CareerRoadmapTimeline.tsx`:

```tsx
const timelineConfig = {
  '3_year': {
    color: 'from-green-500 to-emerald-600',  // Change these
    bgColor: 'from-green-50 to-emerald-50',  // And these
    // ...
  }
};
```

### Customize Explanation Style

Edit `ExplanationPanel.tsx`:

```tsx
// Change gradient colors
className="bg-gradient-to-r from-blue-50 to-purple-50"
// Change to your brand colors:
className="bg-gradient-to-r from-yourColor1 to-yourColor2"
```

---

## Success Checklist

- [ ] API endpoint `/api/roadmap` returns data
- [ ] CareerRoadmapTimeline renders without errors
- [ ] Timeline selector switches between 3/5/10 years
- [ ] Alternative paths toggle works
- [ ] ExplanationPanel "Why?" buttons expand
- [ ] WhyIcon tooltips appear on hover
- [ ] Animations are smooth (60fps)
- [ ] Mobile responsive

---

**🎉 You've successfully integrated Features 2 & 3! 🎉**

**Week 1 Complete:** 3/3 features done (Skill Inference, Career Roadmaps, Explainable AI)

**Next:** Features 5 & 6 (Visual Career Maps, Benchmarking Dashboard)

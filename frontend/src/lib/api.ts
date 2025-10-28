// API client functions for the Next Career Intelligence frontend
// This module wraps calls to the backend FastAPI endpoints defined in the backend/app/api/analyze.py file.

interface AnalyzeCareerInput {
  job_title: string;
  skills: string[];
  location: string;
  years_experience?: number;
}

interface RoadmapInput extends AnalyzeCareerInput {
  timeline: string;
}

/**
 * Analyze a career's AI displacement risk and compatibility.
 * Sends a POST request to the backend /api/analyze endpoint.
 */
export async function analyzeCareer(input: AnalyzeCareerInput) {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/api/analyze`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    throw new Error(`Failed to analyze career: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

/**
 * Generate a multi-year career roadmap.
 * Sends a POST request to the backend /api/roadmap endpoint.
 */
export async function generateCareerRoadmap(input: RoadmapInput) {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/api/roadmap`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    throw new Error(`Failed to generate roadmap: ${res.status} ${await res.text()}`);
  }
  return res.json();
}


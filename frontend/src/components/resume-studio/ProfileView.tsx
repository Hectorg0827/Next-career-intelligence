'use client';

import React, { useState } from 'react';
import { CareerProfile, formatDate, calculateDuration } from '@/types/resume';

interface ProfileViewProps {
  profile: CareerProfile;
  onEdit?: (section: string) => void;
  editable?: boolean;
}

export default function ProfileView({ profile, onEdit, editable = true }: ProfileViewProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['personal', 'skills', 'experience'])
  );

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const { profile_data } = profile;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8 rounded-lg">
        <h1 className="text-3xl font-bold mb-2">{profile_data.personal_info.full_name}</h1>
        <p className="text-blue-100 mb-4">{profile_data.personal_info.email}</p>
        {profile_data.summary && (
          <p className="text-blue-50 max-w-3xl">{profile_data.summary}</p>
        )}
        <div className="flex flex-wrap gap-4 mt-4 text-sm">
          {profile_data.personal_info.phone && (
            <span className="flex items-center gap-2">
              📱 {profile_data.personal_info.phone}
            </span>
          )}
          {profile_data.personal_info.location_city && (
            <span className="flex items-center gap-2">
              📍 {profile_data.personal_info.location_city}, {profile_data.personal_info.location_state}
            </span>
          )}
          {profile_data.personal_info.linkedin_url && (
            <a href={profile_data.personal_info.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:underline">
              💼 LinkedIn
            </a>
          )}
          {profile_data.personal_info.github_url && (
            <a href={profile_data.personal_info.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:underline">
              🐙 GitHub
            </a>
          )}
        </div>
      </div>

      {/* Skills Section */}
      <Section
        title="Skills"
        icon="🧠"
        isExpanded={expandedSections.has('skills')}
        onToggle={() => toggleSection('skills')}
        onEdit={() => onEdit?.('skills')}
        editable={editable}
      >
        <div className="space-y-4">
          {profile_data.skills.hard.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Technical Skills</h4>
              <div className="flex flex-wrap gap-2">
                {profile_data.skills.hard.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {profile_data.skills.soft.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Soft Skills</h4>
              <div className="flex flex-wrap gap-2">
                {profile_data.skills.soft.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </Section>

      {/* Work Experience Section */}
      <Section
        title="Work Experience"
        icon="💼"
        isExpanded={expandedSections.has('experience')}
        onToggle={() => toggleSection('experience')}
        onEdit={() => onEdit?.('work_history')}
        editable={editable}
        count={profile_data.work_history.length}
      >
        <div className="space-y-6">
          {profile_data.work_history.map((work, idx) => (
            <div key={idx} className="border-l-4 border-blue-600 pl-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{work.title}</h4>
                  <p className="text-gray-700">{work.company}</p>
                </div>
                {work.is_current && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                    Current
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-3">
                {formatDate(work.start_date)} - {formatDate(work.end_date)} • {calculateDuration(work.start_date, work.end_date)}
              </p>
              {work.description && (
                <p className="text-gray-700 mb-3">{work.description}</p>
              )}
              {work.achievements && work.achievements.length > 0 && (
                <ul className="space-y-2">
                  {work.achievements.map((achievement, aIdx) => (
                    <li key={aIdx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-blue-600 mt-1">•</span>
                      <span>{achievement}</span>
                    </li>
                  ))}
                </ul>
              )}
              {work.tech_stack && work.tech_stack.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {work.tech_stack.map((tech, tIdx) => (
                    <span key={tIdx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {tech}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </Section>

      {/* Education Section */}
      {profile_data.education.length > 0 && (
        <Section
          title="Education"
          icon="🎓"
          isExpanded={expandedSections.has('education')}
          onToggle={() => toggleSection('education')}
          onEdit={() => onEdit?.('education')}
          editable={editable}
          count={profile_data.education.length}
        >
          <div className="space-y-4">
            {profile_data.education.map((edu, idx) => (
              <div key={idx}>
                <h4 className="text-lg font-semibold text-gray-900">
                  {edu.degree} in {edu.field_of_study}
                </h4>
                <p className="text-gray-700">{edu.institution}</p>
                {(edu.start_date || edu.end_date) && (
                  <p className="text-sm text-gray-600">
                    {edu.start_date && formatDate(edu.start_date)} - {edu.end_date && formatDate(edu.end_date)}
                  </p>
                )}
                {edu.gpa && (
                  <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>
                )}
                {edu.honors && edu.honors.length > 0 && (
                  <div className="mt-2">
                    {edu.honors.map((honor, hIdx) => (
                      <span key={hIdx} className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded mr-2">
                        🏆 {honor}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Projects Section */}
      {profile_data.projects && profile_data.projects.length > 0 && (
        <Section
          title="Projects"
          icon="🚀"
          isExpanded={expandedSections.has('projects')}
          onToggle={() => toggleSection('projects')}
          onEdit={() => onEdit?.('projects')}
          editable={editable}
          count={profile_data.projects.length}
        >
          <div className="space-y-4">
            {profile_data.projects.map((project, idx) => (
              <div key={idx} className="border-l-4 border-purple-600 pl-4">
                <div className="flex justify-between items-start">
                  <h4 className="text-lg font-semibold text-gray-900">{project.name}</h4>
                  {project.url && (
                    <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
                      View Project →
                    </a>
                  )}
                </div>
                {project.role && <p className="text-sm text-gray-600">{project.role}</p>}
                <p className="text-gray-700 mt-2">{project.description}</p>
                {project.tech_stack && project.tech_stack.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {project.tech_stack.map((tech, tIdx) => (
                      <span key={tIdx} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Certifications Section */}
      {profile_data.certifications && profile_data.certifications.length > 0 && (
        <Section
          title="Certifications"
          icon="📜"
          isExpanded={expandedSections.has('certifications')}
          onToggle={() => toggleSection('certifications')}
          onEdit={() => onEdit?.('certifications')}
          editable={editable}
          count={profile_data.certifications.length}
        >
          <div className="space-y-3">
            {profile_data.certifications.map((cert, idx) => (
              <div key={idx}>
                <h4 className="font-semibold text-gray-900">{cert.name}</h4>
                <p className="text-sm text-gray-700">{cert.issuing_organization}</p>
                {cert.issue_date && (
                  <p className="text-xs text-gray-600">
                    Issued: {formatDate(cert.issue_date)}
                    {cert.expiry_date && ` • Expires: ${formatDate(cert.expiry_date)}`}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Profile Metadata */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Profile Information</h3>
        <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
          <div>
            <span className="font-medium">Created:</span> {new Date(profile.created_at).toLocaleDateString()}
          </div>
          <div>
            <span className="font-medium">Last Updated:</span> {new Date(profile.updated_at).toLocaleDateString()}
          </div>
          <div>
            <span className="font-medium">Version:</span> {profile.version}
          </div>
          {profile.metadata?.ai_displacement_risk && (
            <div>
              <span className="font-medium">AI Risk:</span> {profile.metadata.ai_displacement_risk.score}%
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Section Component
interface SectionProps {
  title: string;
  icon: string;
  children: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  onEdit?: () => void;
  editable?: boolean;
  count?: number;
}

function Section({ title, icon, children, isExpanded, onToggle, onEdit, editable, count }: SectionProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div
        className="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {count !== undefined && (
              <p className="text-xs text-gray-500">{count} item{count !== 1 ? 's' : ''}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {editable && onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
            >
              Edit
            </button>
          )}
          <button className="text-gray-500 hover:text-gray-700">
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>
      {isExpanded && (
        <div className="p-4 border-t border-gray-200">
          {children}
        </div>
      )}
    </div>
  );
}

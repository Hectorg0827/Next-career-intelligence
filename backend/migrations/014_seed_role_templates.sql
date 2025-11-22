-- Seed role_skill_templates with common professions
-- Run this after migrations to populate the templates

INSERT INTO public.role_skill_templates (occupation_code, role_title, skills) VALUES
('software_engineer', 'Software Engineer', '[
  {"name": "Python", "confidence": 0.7, "category": "Technical"},
  {"name": "JavaScript", "confidence": 0.6, "category": "Technical"},
  {"name": "Git", "confidence": 0.8, "category": "Tool"},
  {"name": "Problem Solving", "confidence": 0.9, "category": "Soft"},
  {"name": "Code Review", "confidence": 0.7, "category": "Soft"},
  {"name": "Documentation", "confidence": 0.6, "category": "Soft"}
]'),

('product_manager', 'Product Manager', '[
  {"name": "Roadmap Planning", "confidence": 0.8, "category": "Domain"},
  {"name": "Stakeholder Management", "confidence": 0.9, "category": "Soft"},
  {"name": "User Research", "confidence": 0.7, "category": "Domain"},
  {"name": "Data Analysis", "confidence": 0.6, "category": "Technical"},
  {"name": "Jira", "confidence": 0.7, "category": "Tool"},
  {"name": "Prioritization", "confidence": 0.8, "category": "Soft"}
]'),

('data_analyst', 'Data Analyst', '[
  {"name": "SQL", "confidence": 0.9, "category": "Technical"},
  {"name": "Excel", "confidence": 0.8, "category": "Tool"},
  {"name": "Python", "confidence": 0.6, "category": "Technical"},
  {"name": "Data Visualization", "confidence": 0.8, "category": "Technical"},
  {"name": "Statistical Analysis", "confidence": 0.7, "category": "Technical"},
  {"name": "Tableau", "confidence": 0.5, "category": "Tool"}
]'),

('police_officer', 'Police Officer', '[
  {"name": "Firearm Safety", "confidence": 0.7, "category": "Technical"},
  {"name": "Conflict Resolution", "confidence": 0.9, "category": "Soft"},
  {"name": "Report Writing", "confidence": 0.8, "category": "Soft"},
  {"name": "Emergency Response", "confidence": 0.8, "category": "Domain"},
  {"name": "Investigation", "confidence": 0.7, "category": "Domain"},
  {"name": "Community Engagement", "confidence": 0.6, "category": "Soft"}
]'),

('marketing_manager', 'Marketing Manager', '[
  {"name": "Campaign Strategy", "confidence": 0.8, "category": "Domain"},
  {"name": "Social Media Management", "confidence": 0.7, "category": "Domain"},
  {"name": "Content Marketing", "confidence": 0.7, "category": "Domain"},
  {"name": "Google Analytics", "confidence": 0.6, "category": "Tool"},
  {"name": "Budget Management", "confidence": 0.7, "category": "Soft"},
  {"name": "Brand Development", "confidence": 0.6, "category": "Domain"}
]'),

('sales_representative', 'Sales Representative', '[
  {"name": "Customer Relationship Management", "confidence": 0.9, "category": "Soft"},
  {"name": "Negotiation", "confidence": 0.8, "category": "Soft"},
  {"name": "Product Knowledge", "confidence": 0.7, "category": "Domain"},
  {"name": "Cold Calling", "confidence": 0.6, "category": "Domain"},
  {"name": "Salesforce", "confidence": 0.5, "category": "Tool"},
  {"name": "Presentation Skills", "confidence": 0.7, "category": "Soft"}
]'),

('graphic_designer', 'Graphic Designer', '[
  {"name": "Adobe Photoshop", "confidence": 0.8, "category": "Tool"},
  {"name": "Adobe Illustrator", "confidence": 0.8, "category": "Tool"},
  {"name": "Typography", "confidence": 0.7, "category": "Technical"},
  {"name": "Brand Identity", "confidence": 0.7, "category": "Domain"},
  {"name": "Color Theory", "confidence": 0.6, "category": "Technical"},
  {"name": "Client Communication", "confidence": 0.7, "category": "Soft"}
]'),

('nurse', 'Registered Nurse', '[
  {"name": "Patient Care", "confidence": 0.9, "category": "Domain"},
  {"name": "Medical Documentation", "confidence": 0.8, "category": "Technical"},
  {"name": "Vital Signs Monitoring", "confidence": 0.8, "category": "Technical"},
  {"name": "Medication Administration", "confidence": 0.9, "category": "Technical"},
  {"name": "Empathy", "confidence": 0.9, "category": "Soft"},
  {"name": "Emergency Response", "confidence": 0.7, "category": "Domain"}
]'),

('financial_analyst', 'Financial Analyst', '[
  {"name": "Financial Modeling", "confidence": 0.8, "category": "Technical"},
  {"name": "Excel", "confidence": 0.9, "category": "Tool"},
  {"name": "Data Analysis", "confidence": 0.8, "category": "Technical"},
  {"name": "Valuation", "confidence": 0.7, "category": "Technical"},
  {"name": "PowerPoint", "confidence": 0.6, "category": "Tool"},
  {"name": "Financial Reporting", "confidence": 0.8, "category": "Domain"}
]'),

('teacher', 'Teacher', '[
  {"name": "Lesson Planning", "confidence": 0.8, "category": "Domain"},
  {"name": "Classroom Management", "confidence": 0.9, "category": "Soft"},
  {"name": "Student Assessment", "confidence": 0.8, "category": "Domain"},
  {"name": "Communication", "confidence": 0.9, "category": "Soft"},
  {"name": "Curriculum Development", "confidence": 0.7, "category": "Domain"},
  {"name": "Technology Integration", "confidence": 0.6, "category": "Technical"}
]')

ON CONFLICT (occupation_code) DO NOTHING;

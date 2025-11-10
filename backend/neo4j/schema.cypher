// ========================================
// Neo4j Talent Graph - Schema & Initial Data
// ========================================
// Run this in Neo4j Browser (http://localhost:7474) after starting Docker

// ========================================
// 1. CONSTRAINTS (Ensure data integrity)
// ========================================

// Users
CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (u:User) REQUIRE u.user_id IS UNIQUE;

CREATE CONSTRAINT user_email IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

// Skills
CREATE CONSTRAINT skill_name IF NOT EXISTS
FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// Roles
CREATE CONSTRAINT role_title_seniority IF NOT EXISTS
FOR (r:Role) REQUIRE (r.title, r.seniority) IS UNIQUE;

// Companies
CREATE CONSTRAINT company_name IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

// Courses
CREATE CONSTRAINT course_id IF NOT EXISTS
FOR (co:Course) REQUIRE co.course_id IS UNIQUE;

// Industries
CREATE CONSTRAINT industry_name IF NOT EXISTS
FOR (i:Industry) REQUIRE i.name IS UNIQUE;

// ========================================
// 2. INDEXES (Performance optimization)
// ========================================

// Full-text search on skills
CREATE FULLTEXT INDEX skill_search IF NOT EXISTS
FOR (s:Skill) ON EACH [s.name, s.category, s.description];

// Full-text search on roles
CREATE FULLTEXT INDEX role_search IF NOT EXISTS
FOR (r:Role) ON EACH [r.title, r.description];

// Range indexes for filtering
CREATE INDEX user_created_at IF NOT EXISTS FOR (u:User) ON (u.created_at);
CREATE INDEX skill_demand_score IF NOT EXISTS FOR (s:Skill) ON (s.demand_score);
CREATE INDEX skill_category IF NOT EXISTS FOR (s:Skill) ON (s.category);
CREATE INDEX role_seniority IF NOT EXISTS FOR (r:Role) ON (r.seniority);
CREATE INDEX role_avg_salary IF NOT EXISTS FOR (r:Role) ON (r.avg_salary);
CREATE INDEX company_size IF NOT EXISTS FOR (c:Company) ON (c.size);

// ========================================
// 3. SAMPLE DATA - Skills
// ========================================

// Programming Languages
CREATE (python:Skill {
  name: "Python",
  category: "Programming Language",
  demand_score: 95,
  growth_rate: 0.15,
  automation_risk: 0.2,
  avg_salary_premium: 15000,
  learning_curve: "moderate",
  description: "High-level programming language for web, data, and AI"
});

CREATE (javascript:Skill {
  name: "JavaScript",
  category: "Programming Language",
  demand_score: 98,
  growth_rate: 0.10,
  automation_risk: 0.15,
  avg_salary_premium: 12000,
  learning_curve: "moderate"
});

CREATE (typescript:Skill {
  name: "TypeScript",
  category: "Programming Language",
  demand_score: 90,
  growth_rate: 0.25,
  automation_risk: 0.15,
  avg_salary_premium: 18000,
  learning_curve: "moderate"
});

CREATE (java:Skill {
  name: "Java",
  category: "Programming Language",
  demand_score: 85,
  growth_rate: 0.05,
  automation_risk: 0.25,
  avg_salary_premium: 10000,
  learning_curve: "steep"
});

CREATE (go:Skill {
  name: "Go",
  category: "Programming Language",
  demand_score: 75,
  growth_rate: 0.30,
  automation_risk: 0.20,
  avg_salary_premium: 20000,
  learning_curve: "moderate"
});

// Frameworks
CREATE (react:Skill {
  name: "React",
  category: "Frontend Framework",
  demand_score: 93,
  growth_rate: 0.12,
  automation_risk: 0.15,
  avg_salary_premium: 15000,
  learning_curve: "moderate"
});

CREATE (nextjs:Skill {
  name: "Next.js",
  category: "Frontend Framework",
  demand_score: 80,
  growth_rate: 0.35,
  automation_risk: 0.15,
  avg_salary_premium: 18000,
  learning_curve: "moderate"
});

CREATE (fastapi:Skill {
  name: "FastAPI",
  category: "Backend Framework",
  demand_score: 70,
  growth_rate: 0.40,
  automation_risk: 0.20,
  avg_salary_premium: 16000,
  learning_curve: "easy"
});

// Cloud & DevOps
CREATE (aws:Skill {
  name: "AWS",
  category: "Cloud Platform",
  demand_score: 92,
  growth_rate: 0.18,
  automation_risk: 0.25,
  avg_salary_premium: 22000,
  learning_curve: "steep"
});

CREATE (docker:Skill {
  name: "Docker",
  category: "DevOps Tool",
  demand_score: 88,
  growth_rate: 0.15,
  automation_risk: 0.30,
  avg_salary_premium: 14000,
  learning_curve: "moderate"
});

CREATE (kubernetes:Skill {
  name: "Kubernetes",
  category: "DevOps Tool",
  demand_score: 85,
  growth_rate: 0.22,
  automation_risk: 0.30,
  avg_salary_premium: 25000,
  learning_curve: "steep"
});

// Data & AI
CREATE (sql:Skill {
  name: "SQL",
  category: "Database",
  demand_score: 94,
  growth_rate: 0.08,
  automation_risk: 0.20,
  avg_salary_premium: 8000,
  learning_curve: "easy"
});

CREATE (postgresql:Skill {
  name: "PostgreSQL",
  category: "Database",
  demand_score: 82,
  growth_rate: 0.12,
  automation_risk: 0.20,
  avg_salary_premium: 12000,
  learning_curve: "moderate"
});

CREATE (machine_learning:Skill {
  name: "Machine Learning",
  category: "AI/ML",
  demand_score: 89,
  growth_rate: 0.28,
  automation_risk: 0.10,
  avg_salary_premium: 30000,
  learning_curve: "steep"
});

CREATE (llm:Skill {
  name: "Large Language Models",
  category: "AI/ML",
  demand_score: 75,
  growth_rate: 0.50,
  automation_risk: 0.05,
  avg_salary_premium: 40000,
  learning_curve: "steep"
});

// Soft Skills
CREATE (leadership:Skill {
  name: "Leadership",
  category: "Soft Skill",
  demand_score: 90,
  growth_rate: 0.05,
  automation_risk: 0.05,
  avg_salary_premium: 25000,
  learning_curve: "lifelong"
});

CREATE (communication:Skill {
  name: "Communication",
  category: "Soft Skill",
  demand_score: 95,
  growth_rate: 0.05,
  automation_risk: 0.10,
  avg_salary_premium: 15000,
  learning_curve: "lifelong"
});

// ========================================
// 4. SAMPLE DATA - Roles
// ========================================

CREATE (se_entry:Role {
  title: "Software Engineer",
  seniority: "entry",
  avg_salary: 85000,
  salary_range_min: 70000,
  salary_range_max: 100000,
  demand_score: 92,
  typical_years_experience: 1,
  description: "Entry-level software developer building web and mobile applications"
});

CREATE (se_mid:Role {
  title: "Software Engineer",
  seniority: "mid",
  avg_salary: 120000,
  salary_range_min: 100000,
  salary_range_max: 140000,
  demand_score: 95,
  typical_years_experience: 4,
  description: "Mid-level engineer working independently on complex features"
});

CREATE (se_senior:Role {
  title: "Software Engineer",
  seniority: "senior",
  avg_salary: 160000,
  salary_range_min: 140000,
  salary_range_max: 200000,
  demand_score: 98,
  typical_years_experience: 7,
  description: "Senior engineer leading technical design and mentoring juniors"
});

CREATE (staff_eng:Role {
  title: "Staff Engineer",
  seniority: "staff",
  avg_salary: 200000,
  salary_range_min: 180000,
  salary_range_max: 250000,
  demand_score: 88,
  typical_years_experience: 10,
  description: "Technical leader setting architecture and driving org-wide initiatives"
});

CREATE (eng_manager:Role {
  title: "Engineering Manager",
  seniority: "manager",
  avg_salary: 180000,
  salary_range_min: 150000,
  salary_range_max: 220000,
  demand_score: 85,
  typical_years_experience: 8,
  description: "Manager leading and growing engineering teams"
});

// ========================================
// 5. RELATIONSHIPS - Skills Required by Roles
// ========================================

// Entry Software Engineer
MATCH (se_entry:Role {title: "Software Engineer", seniority: "entry"})
MATCH (python:Skill {name: "Python"})
CREATE (se_entry)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.8, substitutable: true}]->(python);

MATCH (se_entry:Role {title: "Software Engineer", seniority: "entry"})
MATCH (javascript:Skill {name: "JavaScript"})
CREATE (se_entry)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.9, substitutable: true}]->(javascript);

MATCH (se_entry:Role {title: "Software Engineer", seniority: "entry"})
MATCH (react:Skill {name: "React"})
CREATE (se_entry)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.7, substitutable: true}]->(react);

MATCH (se_entry:Role {title: "Software Engineer", seniority: "entry"})
MATCH (sql:Skill {name: "SQL"})
CREATE (se_entry)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.6, substitutable: false}]->(sql);

// Mid Software Engineer
MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
MATCH (python:Skill {name: "Python"})
CREATE (se_mid)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.9, substitutable: false}]->(python);

MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
MATCH (typescript:Skill {name: "TypeScript"})
CREATE (se_mid)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.8, substitutable: false}]->(typescript);

MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
MATCH (aws:Skill {name: "AWS"})
CREATE (se_mid)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.6, substitutable: true}]->(aws);

MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
MATCH (docker:Skill {name: "Docker"})
CREATE (se_mid)-[:REQUIRES_SKILL {proficiency: "beginner", importance: 0.5, substitutable: true}]->(docker);

// Senior Software Engineer
MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (python:Skill {name: "Python"})
CREATE (se_senior)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.95, substitutable: false}]->(python);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (typescript:Skill {name: "TypeScript"})
CREATE (se_senior)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.9, substitutable: false}]->(typescript);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (aws:Skill {name: "AWS"})
CREATE (se_senior)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.8, substitutable: false}]->(aws);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (kubernetes:Skill {name: "Kubernetes"})
CREATE (se_senior)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.7, substitutable: true}]->(kubernetes);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (leadership:Skill {name: "Leadership"})
CREATE (se_senior)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.8, substitutable: false}]->(leadership);

// Staff Engineer
MATCH (staff_eng:Role {title: "Staff Engineer", seniority: "staff"})
MATCH (python:Skill {name: "Python"})
CREATE (staff_eng)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.95, substitutable: false}]->(python);

MATCH (staff_eng:Role {title: "Staff Engineer", seniority: "staff"})
MATCH (aws:Skill {name: "AWS"})
CREATE (staff_eng)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.9, substitutable: false}]->(aws);

MATCH (staff_eng:Role {title: "Staff Engineer", seniority: "staff"})
MATCH (leadership:Skill {name: "Leadership"})
CREATE (staff_eng)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.95, substitutable: false}]->(leadership);

MATCH (staff_eng:Role {title: "Staff Engineer", seniority: "staff"})
MATCH (communication:Skill {name: "Communication"})
CREATE (staff_eng)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.9, substitutable: false}]->(communication);

// ========================================
// 6. RELATIONSHIPS - Career Pathways
// ========================================

MATCH (se_entry:Role {title: "Software Engineer", seniority: "entry"})
MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
CREATE (se_entry)-[:PATHWAY_TO {
  typical_years: 3,
  success_rate: 0.8,
  difficulty: "moderate",
  common_blockers: ["Need more system design experience", "Lack of mentorship"]
}]->(se_mid);

MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
CREATE (se_mid)-[:PATHWAY_TO {
  typical_years: 4,
  success_rate: 0.7,
  difficulty: "challenging",
  common_blockers: ["Limited leadership experience", "Not enough impact"]
}]->(se_senior);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (staff_eng:Role {title: "Staff Engineer", seniority: "staff"})
CREATE (se_senior)-[:PATHWAY_TO {
  typical_years: 5,
  success_rate: 0.4,
  difficulty: "very challenging",
  common_blockers: ["Lack of org-wide impact", "Technical leadership gaps"]
}]->(staff_eng);

MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
MATCH (eng_manager:Role {title: "Engineering Manager", seniority: "manager"})
CREATE (se_senior)-[:PATHWAY_TO {
  typical_years: 3,
  success_rate: 0.5,
  difficulty: "challenging",
  common_blockers: ["No management experience", "Not interested in people management"]
}]->(eng_manager);

// ========================================
// 7. RELATIONSHIPS - Skill Pairings
// ========================================
// Skills that are commonly learned together

MATCH (python:Skill {name: "Python"})
MATCH (fastapi:Skill {name: "FastAPI"})
CREATE (python)-[:OFTEN_PAIRED_WITH {frequency: 0.8, synergy_score: 0.9}]->(fastapi);

MATCH (javascript:Skill {name: "JavaScript"})
MATCH (typescript:Skill {name: "TypeScript"})
CREATE (javascript)-[:OFTEN_PAIRED_WITH {frequency: 0.85, synergy_score: 0.95}]->(typescript);

MATCH (typescript:Skill {name: "TypeScript"})
MATCH (react:Skill {name: "React"})
CREATE (typescript)-[:OFTEN_PAIRED_WITH {frequency: 0.9, synergy_score: 0.9}]->(react);

MATCH (react:Skill {name: "React"})
MATCH (nextjs:Skill {name: "Next.js"})
CREATE (react)-[:OFTEN_PAIRED_WITH {frequency: 0.7, synergy_score: 0.85}]->(nextjs);

MATCH (docker:Skill {name: "Docker"})
MATCH (kubernetes:Skill {name: "Kubernetes"})
CREATE (docker)-[:OFTEN_PAIRED_WITH {frequency: 0.75, synergy_score: 0.9}]->(kubernetes);

MATCH (aws:Skill {name: "AWS"})
MATCH (docker:Skill {name: "Docker"})
CREATE (aws)-[:OFTEN_PAIRED_WITH {frequency: 0.8, synergy_score: 0.85}]->(docker);

MATCH (python:Skill {name: "Python"})
MATCH (machine_learning:Skill {name: "Machine Learning"})
CREATE (python)-[:OFTEN_PAIRED_WITH {frequency: 0.95, synergy_score: 0.95}]->(machine_learning);

MATCH (machine_learning:Skill {name: "Machine Learning"})
MATCH (llm:Skill {name: "Large Language Models"})
CREATE (machine_learning)-[:OFTEN_PAIRED_WITH {frequency: 0.6, synergy_score: 0.8}]->(llm);

// ========================================
// 8. SAMPLE DATA - Companies
// ========================================

CREATE (google:Company {
  name: "Google",
  size: "enterprise",
  employee_count: 150000,
  hiring_velocity: 0.8,
  engineering_ratio: 0.45,
  avg_tenure_years: 4.2,
  glassdoor_rating: 4.4
});

CREATE (startup:Company {
  name: "TechStartup Inc",
  size: "startup",
  employee_count: 50,
  hiring_velocity: 0.95,
  engineering_ratio: 0.70,
  avg_tenure_years: 2.1,
  glassdoor_rating: 4.0
});

// Companies hire for roles
MATCH (google:Company {name: "Google"})
MATCH (se_senior:Role {title: "Software Engineer", seniority: "senior"})
CREATE (google)-[:HIRES_FOR {annual_openings: 500, avg_time_to_hire_days: 45}]->(se_senior);

MATCH (startup:Company {name: "TechStartup Inc"})
MATCH (se_mid:Role {title: "Software Engineer", seniority: "mid"})
CREATE (startup)-[:HIRES_FOR {annual_openings: 10, avg_time_to_hire_days: 30}]->(se_mid);

// ========================================
// SUCCESS MESSAGE
// ========================================

RETURN "✅ Neo4j Talent Graph schema created successfully!" AS message,
       count(*) AS total_nodes;

// To verify, run:
// MATCH (n) RETURN labels(n) AS node_type, count(n) AS count;
// MATCH ()-[r]->() RETURN type(r) AS relationship_type, count(r) AS count;

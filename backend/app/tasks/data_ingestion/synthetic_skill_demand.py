"""
Synthetic Job Market Data Generator for AI Displacement Risk Engine v1.0

Since real-time job posting APIs (Adzuna, LinkedIn) require API keys and rate limits,
this module generates realistic synthetic skill demand data based on market research
and industry trends.

The synthetic data maintains realistic patterns:
- Tech skills: High demand, growing trends (AI/ML, Cloud, DevOps)
- Traditional skills: Declining demand (COBOL, Flash, legacy systems)
- Evergreen skills: Stable demand (Communication, Project Management)
- Seasonal patterns: Realistic fluctuations over 365 days

Author: NEXT Career Intelligence Team
Date: November 16, 2025
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import asyncpg
from loguru import logger


# Skill categories with base demand scores and trend patterns
SKILL_DATA = {
    # High-demand, growing tech skills (AI/ML era)
    "ai_ml": [
        ("Python", 850, "surge", 0.92),  # (name, base_demand, trend, ai_substitutability)
        ("Machine Learning", 720, "surge", 0.78),
        ("TensorFlow", 480, "surge", 0.82),
        ("PyTorch", 520, "surge", 0.83),
        ("Natural Language Processing", 380, "surge", 0.85),
        ("Computer Vision", 320, "surge", 0.84),
        ("Deep Learning", 450, "surge", 0.81),
        ("Data Science", 680, "growth", 0.75),
        ("Neural Networks", 290, "surge", 0.79),
        ("Large Language Models", 180, "surge", 0.88),
        ("Prompt Engineering", 150, "surge", 0.45),  # Low substitutability - emerging skill
        ("AI Ethics", 95, "growth", 0.35),  # Low substitutability - human judgment
    ],
    
    # Cloud & DevOps (strong growth)
    "cloud_devops": [
        ("AWS", 920, "growth", 0.65),
        ("Azure", 780, "growth", 0.66),
        ("Google Cloud Platform", 540, "growth", 0.67),
        ("Docker", 650, "growth", 0.72),
        ("Kubernetes", 580, "growth", 0.71),
        ("Terraform", 420, "growth", 0.74),
        ("CI/CD", 510, "growth", 0.70),
        ("Jenkins", 380, "stable", 0.73),
        ("GitLab", 340, "growth", 0.68),
        ("DevOps", 720, "growth", 0.62),
    ],
    
    # Web development (stable/mature)
    "web_dev": [
        ("JavaScript", 980, "stable", 0.75),
        ("React", 850, "stable", 0.72),
        ("Node.js", 720, "stable", 0.74),
        ("TypeScript", 640, "growth", 0.70),
        ("Vue.js", 420, "stable", 0.73),
        ("Angular", 480, "decline", 0.76),
        ("HTML/CSS", 890, "stable", 0.68),
        ("REST APIs", 760, "stable", 0.77),
        ("GraphQL", 380, "growth", 0.71),
        ("Next.js", 320, "growth", 0.69),
    ],
    
    # Data & Analytics (strong demand)
    "data_analytics": [
        ("SQL", 920, "stable", 0.80),
        ("Tableau", 520, "stable", 0.73),
        ("Power BI", 580, "growth", 0.74),
        ("Excel", 850, "stable", 0.82),
        ("R Programming", 380, "decline", 0.78),
        ("Statistics", 420, "stable", 0.65),
        ("Data Visualization", 490, "stable", 0.70),
        ("ETL", 450, "stable", 0.81),
        ("Big Data", 510, "stable", 0.76),
        ("Apache Spark", 340, "stable", 0.79),
    ],
    
    # Mobile development (stable)
    "mobile": [
        ("iOS Development", 480, "stable", 0.68),
        ("Android Development", 520, "stable", 0.69),
        ("Swift", 420, "stable", 0.71),
        ("Kotlin", 380, "growth", 0.70),
        ("React Native", 450, "growth", 0.72),
        ("Flutter", 390, "growth", 0.71),
        ("Mobile UI/UX", 340, "stable", 0.58),
    ],
    
    # Cybersecurity (growing)
    "security": [
        ("Cybersecurity", 620, "growth", 0.55),
        ("Penetration Testing", 280, "growth", 0.52),
        ("Network Security", 420, "stable", 0.60),
        ("Cloud Security", 380, "surge", 0.58),
        ("Security Operations", 310, "growth", 0.57),
        ("Incident Response", 240, "stable", 0.53),
    ],
    
    # Business skills (evergreen)
    "business": [
        ("Project Management", 780, "stable", 0.45),
        ("Agile", 690, "stable", 0.48),
        ("Scrum", 520, "stable", 0.50),
        ("Product Management", 580, "growth", 0.42),
        ("Business Analysis", 490, "stable", 0.55),
        ("Stakeholder Management", 380, "stable", 0.38),
        ("Strategic Planning", 320, "stable", 0.40),
        ("Change Management", 280, "stable", 0.43),
    ],
    
    # Communication skills (low AI substitutability)
    "soft_skills": [
        ("Communication", 920, "stable", 0.30),
        ("Leadership", 680, "stable", 0.28),
        ("Team Collaboration", 740, "stable", 0.32),
        ("Problem Solving", 820, "stable", 0.35),
        ("Critical Thinking", 520, "stable", 0.33),
        ("Creativity", 450, "stable", 0.38),
        ("Emotional Intelligence", 280, "growth", 0.25),
        ("Negotiation", 340, "stable", 0.35),
    ],
    
    # Legacy/declining skills
    "legacy": [
        ("Java", 720, "decline", 0.74),
        ("C++", 480, "stable", 0.71),
        ("PHP", 420, "decline", 0.78),
        ("jQuery", 320, "decline", 0.82),
        ("COBOL", 85, "decline", 0.88),
        ("Flash", 15, "decline", 0.95),
        ("Perl", 95, "decline", 0.84),
        ("Visual Basic", 120, "decline", 0.86),
    ],
    
    # Finance/specialized
    "finance": [
        ("Financial Analysis", 420, "stable", 0.68),
        ("Accounting", 580, "stable", 0.75),
        ("Financial Modeling", 320, "stable", 0.72),
        ("Risk Management", 380, "stable", 0.62),
        ("Compliance", 290, "stable", 0.58),
    ],
}


class SyntheticJobMarketData:
    """
    Generates realistic synthetic job market data for skill demand tracking.
    
    Features:
    - 365-day historical data per skill
    - Realistic trend patterns (surge, growth, stable, decline)
    - Seasonal fluctuations (holiday slowdowns, quarterly hiring)
    - Weekend/weekday patterns
    - Random noise for realism
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize with database connection pool."""
        self.db_pool = db_pool
        
    async def generate_and_insert_data(self) -> Dict[str, int]:
        """
        Generate 365 days of skill demand data and insert into database.
        
        Returns:
            Statistics dictionary
        """
        logger.info("🎲 Generating synthetic job market data...")
        start_time = datetime.now()
        
        # Flatten skill data
        all_skills = []
        for category, skills in SKILL_DATA.items():
            for skill_name, base_demand, trend, ai_sub in skills:
                all_skills.append({
                    'name': skill_name,
                    'category': category,
                    'base_demand': base_demand,
                    'trend': trend,
                    'ai_substitutability': ai_sub
                })
        
        logger.info(f"✅ Prepared {len(all_skills)} skills across {len(SKILL_DATA)} categories")
        
        # Generate 365-day history for each skill
        records = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        for skill in all_skills:
            for day_offset in range(365):
                date = start_date + timedelta(days=day_offset)
                
                # Calculate demand for this date
                demand = self._calculate_demand(
                    skill['base_demand'],
                    skill['trend'],
                    day_offset,
                    date
                )
                
                # Calculate 30-day trend
                if day_offset >= 30:
                    trend_30d = self._calculate_trend(skill['trend'], day_offset)
                else:
                    trend_30d = 0.0
                
                # Normalize demand to 0-1 scale (base_demand is 1-1000)
                demand_normalized = min(1.0, demand / 1000.0)
                
                records.append((
                    skill['name'],           # skill_name
                    skill['category'],       # skill_category
                    'all',                   # industry (aggregate across all)
                    None,                    # occupation_code (NULL = all occupations)
                    'US',                    # geography
                    demand_normalized,       # demand_score (0-1)
                    trend_30d,              # trend_score (-1 to +1)
                    date.date(),            # snapshot_date (DATE type)
                    datetime.now()          # created_at (TIMESTAMP)
                ))
        
        logger.info(f"✅ Generated {len(records)} data points ({len(all_skills)} skills × 365 days)")
        
        # Bulk insert
        await self._bulk_insert_records(records)
        
        # Calculate statistics
        duration = (datetime.now() - start_time).total_seconds()
        stats = {
            'skills_tracked': len(all_skills),
            'days_of_history': 365,
            'total_data_points': len(records),
            'categories': len(SKILL_DATA),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info(f"✅ Synthetic job market data generation complete in {duration:.1f}s")
        
        return stats
    
    def _calculate_demand(self, base_demand: int, trend: str, day_offset: int, date: datetime) -> int:
        """
        Calculate demand score for a specific date.
        
        Factors:
        - Base demand level
        - Trend pattern (surge, growth, stable, decline)
        - Seasonal patterns (Q4 hiring surge, summer slowdown)
        - Weekend effects (lower demand)
        - Random noise
        """
        demand = float(base_demand)
        
        # Apply trend over 365 days
        progress = day_offset / 365.0  # 0.0 to 1.0
        
        if trend == "surge":
            # Exponential growth (AI/ML skills)
            demand *= (1.0 + 0.8 * progress)  # +80% over year
        elif trend == "growth":
            # Linear growth (Cloud, DevOps)
            demand *= (1.0 + 0.3 * progress)  # +30% over year
        elif trend == "stable":
            # Flat with noise (evergreen skills)
            demand *= (1.0 + 0.05 * (random.random() - 0.5))  # ±2.5%
        elif trend == "decline":
            # Linear decline (legacy skills)
            demand *= (1.0 - 0.2 * progress)  # -20% over year
        
        # Seasonal patterns
        month = date.month
        if month == 12:  # December hiring surge
            demand *= 1.15
        elif month in [7, 8]:  # Summer slowdown
            demand *= 0.92
        elif month in [1, 4, 7, 10]:  # Quarterly hiring bumps
            demand *= 1.08
        
        # Weekend effect (lower demand)
        if date.weekday() >= 5:  # Saturday or Sunday
            demand *= 0.75
        
        # Random daily noise (±10%)
        demand *= (1.0 + 0.1 * (random.random() - 0.5))
        
        # Ensure positive integer
        return max(1, int(demand))
    
    def _calculate_trend(self, trend_type: str, day_offset: int) -> float:
        """
        Calculate 30-day trend percentage.
        
        Returns:
            Float between -1.0 and 1.0 (e.g., 0.15 = +15% growth)
        """
        if trend_type == "surge":
            return 0.15 + 0.05 * random.random()  # +15-20%
        elif trend_type == "growth":
            return 0.05 + 0.03 * random.random()  # +5-8%
        elif trend_type == "stable":
            return -0.02 + 0.04 * random.random()  # -2% to +2%
        elif trend_type == "decline":
            return -0.08 - 0.04 * random.random()  # -8% to -12%
        else:
            return 0.0
    
    async def _bulk_insert_records(self, records: List[Tuple]):
        """Bulk insert skill demand records into database."""
        logger.info(f"💾 Inserting {len(records)} records into skill_demand_history...")
        
        insert_query = """
            INSERT INTO skill_demand_history (
                skill_name,
                skill_category,
                industry,
                occupation_code,
                geography,
                demand_score,
                trend_score,
                snapshot_date,
                created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (skill_name, industry, occupation_code, geography, snapshot_date) 
            DO UPDATE SET
                demand_score = EXCLUDED.demand_score,
                trend_score = EXCLUDED.trend_score,
                created_at = EXCLUDED.created_at
        """
        
        # Insert in batches of 1000 for performance
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            async with self.db_pool.acquire() as conn:
                await conn.executemany(insert_query, batch)
            
            if (i + batch_size) % 10000 == 0:
                logger.info(f"   Progress: {i + batch_size}/{len(records)} records...")
        
        logger.info(f"✅ Inserted {len(records)} records into skill_demand_history")


async def generate_skill_demand_data_cli():
    """CLI entry point for synthetic job market data generation."""
    logger.info("=" * 60)
    logger.info("Synthetic Job Market Data Generation - Phase 3")
    logger.info("=" * 60)
    
    # Database connection
    db_url = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"
    
    logger.info(f"📊 Connecting to database...")
    pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10, command_timeout=120)
    
    try:
        generator = SyntheticJobMarketData(pool)
        stats = await generator.generate_and_insert_data()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ SYNTHETIC JOB MARKET DATA GENERATION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"   Skills Tracked: {stats['skills_tracked']}")
        logger.info(f"   Days of History: {stats['days_of_history']}")
        logger.info(f"   Total Data Points: {stats['total_data_points']}")
        logger.info(f"   Categories: {stats['categories']}")
        logger.info(f"   Duration: {stats['duration_seconds']}s")
        logger.info("=" * 60)
        
        # Verify data with sample queries
        logger.info("\n📊 Verifying data quality...")
        
        async with pool.acquire() as conn:
            # Most in-demand skills (today)
            top_skills = await conn.fetch("""
                SELECT skill_name, demand_score, trend_score
                FROM skill_demand_history
                WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM skill_demand_history)
                ORDER BY demand_score DESC
                LIMIT 10
            """)
            
            logger.info(f"\n✅ Top 10 in-demand skills (today):")
            for i, skill in enumerate(top_skills, 1):
                trend_pct = skill['trend_score'] * 100
                logger.info(f"   {i}. {skill['skill_name']}: {skill['demand_score']:.2f} demand, "
                          f"trend: {trend_pct:+.1f}%")
            
            # Fastest growing skills
            growing = await conn.fetch("""
                SELECT skill_name, AVG(demand_score) as avg_demand, AVG(trend_score) as avg_trend
                FROM skill_demand_history
                WHERE snapshot_date >= NOW() - INTERVAL '30 days'
                GROUP BY skill_name
                ORDER BY avg_trend DESC
                LIMIT 5
            """)
            
            logger.info(f"\n✅ Fastest growing skills (30-day trend):")
            for i, skill in enumerate(growing, 1):
                logger.info(f"   {i}. {skill['skill_name']}: {skill['avg_trend']*100:+.1f}% growth")
        
    finally:
        await pool.close()
        logger.info("\n👋 Database connection closed")


if __name__ == "__main__":
    asyncio.run(generate_skill_demand_data_cli())

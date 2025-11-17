"""
O*NET Task Taxonomy Ingestion for AI Displacement Risk Engine v1.0

This module downloads O*NET database files, parses task statements and ratings,
calculates automation risk scores, and populates the ai_task_taxonomy table.

Data Source: O*NET Database (https://www.onetcenter.org/database.html)
Files Used:
- Task Statements.txt: Task descriptions for occupations
- Task Ratings.txt: Importance and frequency ratings
- Occupation Data.txt: Occupation metadata

Target: 1000+ tasks across 50+ occupations with automation risk scores.

Author: NEXT Career Intelligence Team
Date: November 16, 2025
"""

import asyncio
import csv
import os
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlretrieve

import asyncpg
from loguru import logger

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from app.config import settings
except ImportError:
    # Fallback settings if config not available
    class Settings:
        DATABASE_URL = os.getenv("DATABASE_URL", "")
    settings = Settings()


class ONETTaskIngestion:
    """
    Downloads and processes O*NET task data to populate ai_task_taxonomy.
    
    Process:
    1. Download O*NET database (if not cached)
    2. Parse Task Statements.txt (task descriptions)
    3. Parse Task Ratings.txt (importance/frequency)
    4. Calculate automation scores using AI capability heuristics
    5. Bulk insert into ai_task_taxonomy
    
    Automation Score Formula:
    - technical_capability: How capable is AI? (0-100)
      * Cognitive tasks (analysis, coding): Higher capability
      * Physical tasks (construction, surgery): Lower capability
      * Creative tasks (design, strategy): Medium capability
    
    - economic_viability: How likely to automate? (0-100)
      * High-volume tasks: More viable
      * High-cost labor tasks: More viable
      * Safety-critical tasks: Less viable
    
    - task_risk = technical_capability × economic_viability / 100
    """
    
    # O*NET database version and download URL
    ONET_VERSION = "28.2"
    ONET_BASE_URL = "https://www.onetcenter.org/dl_files"
    ONET_DATABASE_FILE = f"db_{ONET_VERSION.replace('.', '_')}_text.zip"
    
    # Local cache directory
    CACHE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "onet_cache"
    
    # Top 50 high-priority occupations (tech, business, healthcare)
    PRIORITY_OCCUPATIONS = [
        "15-1252.00",  # Software Developers
        "15-1256.00",  # Software Developers, Applications
        "15-1257.00",  # Web Developers
        "15-1299.08",  # Computer Systems Engineers/Architects
        "15-2051.00",  # Data Scientists
        "15-2051.01",  # Business Intelligence Analysts
        "15-2041.00",  # Statisticians
        "13-2011.00",  # Accountants and Auditors
        "13-1111.00",  # Management Analysts
        "13-1161.00",  # Market Research Analysts
        "11-1021.00",  # General and Operations Managers
        "11-2021.00",  # Marketing Managers
        "11-3021.00",  # Computer and Information Systems Managers
        "29-1141.00",  # Registered Nurses
        "29-1215.00",  # Family Medicine Physicians
        "29-1216.00",  # General Internal Medicine Physicians
        "25-1011.00",  # Business Teachers, Postsecondary
        "25-1021.00",  # Computer Science Teachers, Postsecondary
        "27-3031.00",  # Public Relations Specialists
        "27-1024.00",  # Graphic Designers
        "27-3043.00",  # Writers and Authors
        "23-1011.00",  # Lawyers
        "41-3031.00",  # Securities and Commodities Traders
        "41-4011.00",  # Sales Representatives, Wholesale
        "19-3051.00",  # Urban and Regional Planners
        "17-2051.00",  # Civil Engineers
        "17-2141.00",  # Mechanical Engineers
        "17-2112.00",  # Industrial Engineers
        "13-2072.00",  # Loan Officers
        "43-6011.00",  # Executive Secretaries
        "43-3031.00",  # Bookkeeping Clerks
        "53-3032.00",  # Heavy Truck Drivers
        "35-3023.00",  # Fast Food Workers
        "41-2031.00",  # Retail Salespersons
        "37-2011.00",  # Janitors and Cleaners
        "31-1131.00",  # Nursing Assistants
        "53-7062.00",  # Laborers, Freight/Stock
        "43-4051.00",  # Customer Service Representatives
        "43-9061.00",  # Office Clerks, General
        "47-2031.00",  # Carpenters
        "51-4041.00",  # Machinists
        "51-2092.00",  # Team Assemblers
        "49-9071.00",  # Maintenance Workers, General
        "33-3051.00",  # Police Officers
        "25-2021.00",  # Elementary School Teachers
        "25-2031.00",  # Secondary School Teachers
        "21-1012.00",  # Educational Counselors
        "39-9032.00",  # Recreation Workers
        "35-1012.00",  # Food Service Managers
        "11-9111.00",  # Medical and Health Services Managers
    ]
    
    # Keywords for automation capability heuristics
    COGNITIVE_KEYWORDS = [
        "analyze", "design", "develop", "plan", "evaluate", "research",
        "calculate", "program", "code", "debug", "test", "document",
        "process data", "interpret", "optimize", "model", "forecast"
    ]
    
    PHYSICAL_KEYWORDS = [
        "operate", "install", "repair", "assemble", "construct", "drive",
        "lift", "carry", "clean", "inspect", "maintain", "handle",
        "perform surgery", "administer", "treat patients"
    ]
    
    CREATIVE_KEYWORDS = [
        "create", "design", "write", "compose", "innovate", "conceptualize",
        "brainstorm", "strategize", "lead", "manage teams", "negotiate",
        "counsel", "teach", "present", "communicate"
    ]
    
    ROUTINE_KEYWORDS = [
        "record", "enter data", "file", "sort", "organize", "schedule",
        "answer calls", "process orders", "monitor", "check", "verify",
        "follow procedures", "maintain records"
    ]
    
    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize ingestion with database connection pool."""
        self.db_pool = db_pool
        self.cache_dir = self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_full_ingestion(self) -> Dict[str, int]:
        """
        Run complete O*NET data ingestion pipeline.
        
        Returns:
            Dict with statistics: {
                'tasks_inserted': int,
                'occupations_covered': int,
                'avg_tasks_per_occupation': float,
                'avg_automation_score': float
            }
        """
        logger.info("🚀 Starting O*NET task ingestion...")
        start_time = datetime.now()
        
        try:
            # Step 1: Download O*NET database (if needed)
            await self._download_onet_database()
            
            # Step 2: Parse task statements and ratings
            tasks_data = await self._parse_onet_tasks()
            logger.info(f"✅ Parsed {len(tasks_data)} tasks from O*NET database")
            
            # Step 3: Calculate automation scores
            enriched_tasks = await self._calculate_automation_scores(tasks_data)
            logger.info(f"✅ Calculated automation scores for {len(enriched_tasks)} tasks")
            
            # Step 4: Bulk insert into database
            stats = await self._bulk_insert_tasks(enriched_tasks)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ O*NET ingestion complete in {duration:.1f}s")
            logger.info(f"   📊 Statistics: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ O*NET ingestion failed: {e}")
            raise
    
    async def _download_onet_database(self) -> Path:
        """
        Download O*NET database ZIP file if not already cached.
        
        Returns:
            Path to downloaded ZIP file
        """
        zip_path = self.cache_dir / self.ONET_DATABASE_FILE
        
        if zip_path.exists():
            logger.info(f"✅ Using cached O*NET database: {zip_path}")
            return zip_path
        
        logger.info(f"📥 Downloading O*NET database v{self.ONET_VERSION}...")
        download_url = f"{self.ONET_BASE_URL}/{self.ONET_DATABASE_FILE}"
        
        try:
            # Download with progress (using urllib for simplicity)
            urlretrieve(download_url, zip_path)
            logger.info(f"✅ Downloaded O*NET database: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
            return zip_path
            
        except Exception as e:
            logger.error(f"❌ Failed to download O*NET database: {e}")
            logger.info("💡 Manual download: https://www.onetcenter.org/database.html")
            raise
    
    async def _parse_onet_tasks(self) -> List[Dict]:
        """
        Parse O*NET Task Statements and Task Ratings files.
        
        Returns:
            List of task dictionaries with structure:
            {
                'occupation_code': str,
                'task_id': str,
                'task_statement': str,
                'importance': float (1-5 scale),
                'frequency': Optional[float]
            }
        """
        logger.info("📖 Parsing O*NET task files...")
        
        zip_path = self.cache_dir / self.ONET_DATABASE_FILE
        
        # Extract task files from ZIP
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Task Statements
            statements_content = z.read('Task Statements.txt').decode('utf-8')
            # Task Ratings
            try:
                ratings_content = z.read('Task Ratings.txt').decode('utf-8')
            except KeyError:
                logger.warning("⚠️ Task Ratings.txt not found - using default importance")
                ratings_content = None
        
        # Parse statements
        statements = {}
        reader = csv.DictReader(statements_content.splitlines(), delimiter='\t')
        for row in reader:
            occ_code = row['O*NET-SOC Code']
            task_id = row['Task ID']
            statement = row['Task']
            
            # Only process priority occupations (save memory)
            if occ_code in self.PRIORITY_OCCUPATIONS or len(statements) < 1000:
                statements[(occ_code, task_id)] = {
                    'occupation_code': occ_code,
                    'task_id': task_id,
                    'task_statement': statement,
                    'importance': 3.0,  # Default medium importance
                    'frequency': None
                }
        
        # Parse ratings (importance scores)
        if ratings_content:
            reader = csv.DictReader(ratings_content.splitlines(), delimiter='\t')
            for row in reader:
                occ_code = row['O*NET-SOC Code']
                task_id = row['Task ID']
                scale_id = row['Scale ID']
                
                key = (occ_code, task_id)
                if key in statements:
                    if scale_id == 'IM':  # Importance
                        statements[key]['importance'] = float(row['Data Value'])
                    elif scale_id == 'FT':  # Frequency
                        statements[key]['frequency'] = float(row['Data Value'])
        
        tasks_list = list(statements.values())
        logger.info(f"✅ Parsed {len(tasks_list)} tasks across {len(set(t['occupation_code'] for t in tasks_list))} occupations")
        
        return tasks_list
    
    async def _calculate_automation_scores(self, tasks: List[Dict]) -> List[Dict]:
        """
        Calculate technical_capability, economic_viability, and task_risk scores.
        
        Uses keyword-based heuristics to estimate AI automation potential.
        
        Args:
            tasks: List of task dictionaries from _parse_onet_tasks
            
        Returns:
            Same list with added fields: technical_capability, economic_viability, task_risk
        """
        logger.info("🤖 Calculating automation risk scores...")
        
        for task in tasks:
            statement = task['task_statement'].lower()
            importance = task['importance']
            
            # Calculate technical_capability (0-100)
            tech_score = self._calculate_technical_capability(statement)
            
            # Calculate economic_viability (0-100)
            econ_score = self._calculate_economic_viability(statement, importance)
            
            # Calculate task_risk = tech × econ / 100
            task_risk = (tech_score * econ_score) / 100.0
            
            # Add scores to task
            task['technical_capability'] = round(tech_score, 1)
            task['economic_viability'] = round(econ_score, 1)
            task['task_risk'] = round(task_risk, 1)
        
        # Log distribution
        avg_risk = sum(t['task_risk'] for t in tasks) / len(tasks)
        high_risk = sum(1 for t in tasks if t['task_risk'] > 60)
        logger.info(f"   📊 Avg risk: {avg_risk:.1f}, High risk tasks: {high_risk}/{len(tasks)}")
        
        return tasks
    
    def _calculate_technical_capability(self, statement: str) -> float:
        """
        Estimate AI's technical capability to perform task (0-100).
        
        Heuristics:
        - Cognitive/analytical tasks: 70-90 (AI excels)
        - Routine data tasks: 80-95 (AI dominates)
        - Physical tasks: 10-40 (AI limited)
        - Creative tasks: 40-70 (AI improving)
        - Human interaction: 30-60 (AI weak on empathy)
        """
        score = 50.0  # Default baseline
        
        # Check keywords
        cognitive_matches = sum(1 for kw in self.COGNITIVE_KEYWORDS if kw in statement)
        physical_matches = sum(1 for kw in self.PHYSICAL_KEYWORDS if kw in statement)
        creative_matches = sum(1 for kw in self.CREATIVE_KEYWORDS if kw in statement)
        routine_matches = sum(1 for kw in self.ROUTINE_KEYWORDS if kw in statement)
        
        # Adjust score based on task type
        if routine_matches >= 2:
            score = 85.0  # Highly automatable routine tasks
        elif cognitive_matches >= 2:
            score = 75.0  # Strong AI capability for analysis
        elif physical_matches >= 2:
            score = 25.0  # Limited AI capability for physical work
        elif creative_matches >= 2:
            score = 55.0  # Moderate AI capability for creative work
        
        # Fine-tune adjustments
        if "data" in statement or "information" in statement:
            score += 10
        if "physical" in statement or "manual" in statement:
            score -= 15
        if "people" in statement or "customer" in statement or "patient" in statement:
            score -= 10
        if "strategy" in statement or "decision" in statement:
            score += 5
        
        # Clamp to 0-100
        return max(0.0, min(100.0, score))
    
    def _calculate_economic_viability(self, statement: str, importance: float) -> float:
        """
        Estimate economic viability of automating task (0-100).
        
        Factors:
        - Task importance (high importance = more incentive)
        - Task frequency (routine = more incentive)
        - Safety considerations (safety-critical = less incentive)
        - Labor cost (high-skill = more incentive)
        """
        # Base score from importance (1-5 scale → 20-100)
        score = 20 + (importance - 1) * 20
        
        # Adjust for frequency/routine
        if any(kw in statement for kw in self.ROUTINE_KEYWORDS):
            score += 15  # Routine tasks more viable
        
        # Adjust for safety-critical
        if "safe" in statement or "emergency" in statement or "critical" in statement:
            score -= 20  # Less viable to automate
        
        # Adjust for volume
        if "high volume" in statement or "large scale" in statement or "many" in statement:
            score += 10  # Economies of scale
        
        # Clamp to 0-100
        return max(0.0, min(100.0, score))
    
    async def _bulk_insert_tasks(self, tasks: List[Dict]) -> Dict[str, float]:
        """
        Bulk insert tasks into ai_task_taxonomy table.
        
        Args:
            tasks: List of task dictionaries with automation scores
            
        Returns:
            Statistics dictionary
        """
        logger.info(f"💾 Inserting {len(tasks)} tasks into database...")
        
        # Prepare records for bulk insert
        records = []
        for task in tasks:
            records.append((
                task['occupation_code'],
                task['task_id'],
                task['task_statement'],
                task['importance'],
                task['technical_capability'],
                task['economic_viability'],
                task['task_risk'],
                datetime.now()
            ))
        
        # Bulk insert with ON CONFLICT DO UPDATE
        insert_query = """
            INSERT INTO ai_task_taxonomy (
                occupation_code,
                task_id,
                task_statement,
                task_importance,
                technical_capability,
                economic_viability,
                task_risk,
                last_updated
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (occupation_code, task_id) 
            DO UPDATE SET
                task_statement = EXCLUDED.task_statement,
                task_importance = EXCLUDED.task_importance,
                technical_capability = EXCLUDED.technical_capability,
                economic_viability = EXCLUDED.economic_viability,
                task_risk = EXCLUDED.task_risk,
                last_updated = EXCLUDED.last_updated
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.executemany(insert_query, records)
        
        # Calculate statistics
        occupations = set(t['occupation_code'] for t in tasks)
        avg_tasks_per_occ = len(tasks) / len(occupations)
        avg_risk = sum(t['task_risk'] for t in tasks) / len(tasks)
        
        stats = {
            'tasks_inserted': len(tasks),
            'occupations_covered': len(occupations),
            'avg_tasks_per_occupation': round(avg_tasks_per_occ, 1),
            'avg_automation_score': round(avg_risk, 1)
        }
        
        logger.info(f"✅ Inserted {len(tasks)} tasks into ai_task_taxonomy")
        
        return stats


async def run_onet_ingestion_cli():
    """
    CLI entry point for O*NET data ingestion.
    
    Usage:
        python3 -m app.tasks.data_ingestion.onet_tasks
    """
    logger.info("=" * 60)
    logger.info("O*NET Task Taxonomy Ingestion - Phase 3")
    logger.info("=" * 60)
    
    # Create database connection pool
    db_url = settings.DATABASE_URL
    if not db_url or not db_url.startswith("postgresql://"):
        db_url = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"
    
    logger.info(f"📊 Connecting to database...")
    pool = await asyncpg.create_pool(db_url, min_size=2, max_size=5, command_timeout=60)
    
    try:
        # Run ingestion
        ingestion = ONETTaskIngestion(pool)
        stats = await ingestion.run_full_ingestion()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ INGESTION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"   Tasks Inserted: {stats['tasks_inserted']}")
        logger.info(f"   Occupations Covered: {stats['occupations_covered']}")
        logger.info(f"   Avg Tasks/Occupation: {stats['avg_tasks_per_occupation']}")
        logger.info(f"   Avg Automation Score: {stats['avg_automation_score']}/100")
        logger.info("=" * 60)
        
    finally:
        await pool.close()
        logger.info("👋 Database connection closed")


if __name__ == "__main__":
    # Run as standalone script
    asyncio.run(run_onet_ingestion_cli())

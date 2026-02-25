"""
Layoff Monitor
Fetches and caches layoff data from public sources.

Sources:
1. Layoffs.fyi public data (CSV, updated regularly)
2. WARN Act database (via BLS / state databases - public)

Data is refreshed weekly via scheduled task and stored in Supabase `layoff_alerts` table.
"""

import httpx
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


LAYOFFS_FYI_CSV_URL = "https://layoffs.fyi/data/layoffs.csv"


async def fetch_layoffs_fyi() -> List[Dict[str, Any]]:
    """
    Fetch layoff data from layoffs.fyi public CSV export.
    Returns normalized list of layoff alert dicts.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                LAYOFFS_FYI_CSV_URL,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NEXT Career Intelligence)"},
                follow_redirects=True,
            )
            response.raise_for_status()
            content = response.text

        reader = csv.DictReader(io.StringIO(content))
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        for row in reader:
            try:
                # Parse date — Layoffs.fyi format varies, attempt common formats
                date_str = row.get("Date") or row.get("date") or ""
                announcement_date = None
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        announcement_date = datetime.strptime(date_str.strip(), fmt)
                        break
                    except ValueError:
                        continue

                if not announcement_date or announcement_date < cutoff_date:
                    continue

                headcount_raw = row.get("Laid_Off_Count") or row.get("laid_off_count") or row.get("# Laid Off") or "0"
                try:
                    headcount = int(str(headcount_raw).replace(",", "").strip())
                except ValueError:
                    headcount = 0

                company = (row.get("Company") or row.get("company") or "").strip()
                industry = (row.get("Industry") or row.get("industry") or "").strip()
                source_url = (row.get("Source") or row.get("source") or "").strip()

                if not company:
                    continue

                alerts.append({
                    "company": company,
                    "headcount_reduction": headcount,
                    "industry": industry,
                    "announcement_date": announcement_date.date().isoformat(),
                    "source_url": source_url,
                    "data_source": "layoffs_fyi",
                })
            except Exception as row_err:
                logger.debug(f"Skipping layoff row: {row_err}")
                continue

        logger.info(f"Fetched {len(alerts)} layoff alerts from Layoffs.fyi (last 90 days)")
        return alerts

    except Exception as e:
        logger.warning(f"Layoffs.fyi fetch failed: {e}")
        return []


async def fetch_warn_act_data() -> List[Dict[str, Any]]:
    """
    Fetch WARN Act notices from the US Department of Labor public data.
    DOL publishes WARN notices at: https://www.dol.gov/agencies/eta/layoffs/warn
    Note: Federal WARN data requires scraping state websites; this uses a curated public feed.
    """
    # The DOL WARN data is only available via individual state pages.
    # A practical alternative is the aggregated dataset from Warn Tracker.
    # For now, return empty and log — this is a placeholder for state-specific integration.
    logger.info("WARN Act integration: state-level data requires per-state scraping; using layoffs.fyi as primary source")
    return []


async def store_layoff_alerts(alerts: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Upsert layoff alerts into Supabase `layoff_alerts` table.
    Returns stats: {inserted, updated, errors}
    """
    if not alerts:
        return {"inserted": 0, "updated": 0, "errors": 0}

    stats = {"inserted": 0, "updated": 0, "errors": 0}

    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()

        for alert in alerts:
            try:
                # Upsert on (company, announcement_date)
                existing = (
                    client.table("layoff_alerts")
                    .select("id")
                    .eq("company", alert["company"])
                    .eq("announcement_date", alert["announcement_date"])
                    .execute()
                )

                if existing.data:
                    client.table("layoff_alerts").update(alert).eq("id", existing.data[0]["id"]).execute()
                    stats["updated"] += 1
                else:
                    client.table("layoff_alerts").insert({
                        **alert,
                        "created_at": datetime.utcnow().isoformat(),
                    }).execute()
                    stats["inserted"] += 1

            except Exception as e:
                logger.error(f"Error storing layoff alert for {alert.get('company')}: {e}")
                stats["errors"] += 1

    except Exception as e:
        logger.error(f"Layoff alerts storage failed: {e}")
        stats["errors"] += len(alerts)

    logger.info(f"Layoff alerts stored: {stats}")
    return stats


async def get_layoff_alerts(
    industry: Optional[str] = None,
    days_back: int = 90,
) -> List[Dict[str, Any]]:
    """
    Get recent layoff alerts from Supabase, optionally filtered by industry.
    Falls back to live fetch if database unavailable.
    """
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()

        cutoff = (datetime.utcnow() - timedelta(days=days_back)).date().isoformat()
        query = client.table("layoff_alerts").select("*").gte("announcement_date", cutoff).order(
            "announcement_date", desc=True
        )

        if industry:
            query = query.ilike("industry", f"%{industry}%")

        result = query.limit(50).execute()
        return result.data or []

    except Exception as e:
        logger.warning(f"Could not fetch layoff alerts from DB: {e} — attempting live fetch")
        # Fall back to live Layoffs.fyi fetch
        alerts = await fetch_layoffs_fyi()
        if industry:
            alerts = [a for a in alerts if industry.lower() in (a.get("industry") or "").lower()]
        return alerts[:20]


async def run_layoff_update() -> Dict[str, int]:
    """
    Full refresh: fetch from all sources and upsert to DB.
    Called by the weekly scheduler task.
    """
    logger.info("Running weekly layoff alert update...")

    all_alerts: List[Dict[str, Any]] = []

    layoffs_fyi = await fetch_layoffs_fyi()
    all_alerts.extend(layoffs_fyi)

    warn_data = await fetch_warn_act_data()
    all_alerts.extend(warn_data)

    stats = await store_layoff_alerts(all_alerts)
    logger.info(f"Layoff update complete: {len(all_alerts)} alerts processed, {stats}")
    return stats

"""
Finance News Crawler — Entry Point

Usage:
  python main.py --run-now       # Execute immediately
  python main.py --schedule      # Start daemon mode (runs daily per config.yaml)
"""
import argparse
import logging
import os
import random
import time
from datetime import datetime

import pytz
import schedule
import yaml

from report_generator import generate_report
from scrapers import INTERNATIONAL_SCRAPERS, TAIWAN_SCRAPERS
from stock_tracker import fetch_stock_data

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(LOG_DIR, f"crawler_{datetime.now().strftime('%Y%m%d')}.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("main")


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_scrapers(scraper_classes: list, crawler_cfg: dict) -> list[tuple[str, list[dict]]]:
    max_articles = crawler_cfg.get("max_articles_per_site", 10)
    timeout = crawler_cfg.get("timeout", 30)
    retries = crawler_cfg.get("retries", 3)
    delay_min = crawler_cfg.get("request_delay_min", 2)
    delay_max = crawler_cfg.get("request_delay_max", 5)

    results = []
    for cls in scraper_classes:
        scraper = cls(max_articles=max_articles, timeout=timeout, retries=retries)
        logger.info(f"Scraping: {scraper.name} ...")
        articles = scraper.get_articles()
        logger.info(f"  -> {len(articles)} articles collected")
        results.append((scraper.name, articles))
        delay = random.uniform(delay_min, delay_max)
        time.sleep(delay)
    return results


def run_job(config: dict) -> None:
    logger.info("=" * 60)
    logger.info("Starting daily finance news crawl...")

    crawler_cfg = config.get("crawler", {})

    # 1. Stock data
    logger.info("Fetching stock data...")
    stock_date, stock_rows = fetch_stock_data()
    logger.info(f"Stock data date: {stock_date}")

    # 2. International news
    logger.info("--- International scrapers ---")
    international = run_scrapers(INTERNATIONAL_SCRAPERS, crawler_cfg)

    # 3. Taiwan news
    logger.info("--- Taiwan scrapers ---")
    taiwan = run_scrapers(TAIWAN_SCRAPERS, crawler_cfg)

    # 4. Generate report
    output_dir = "output"
    report_path = generate_report(stock_date, stock_rows, international, taiwan, output_dir)
    logger.info(f"Report saved: {report_path}")

    # 5. Email (optional)
    email_cfg = config.get("email", {})
    if email_cfg.get("enabled", False):
        logger.info("Sending email report...")
        from notifier.email_sender import send_report
        report_date = datetime.now().strftime("%Y-%m-%d")
        success = send_report(email_cfg, report_path, report_date)
        if success:
            logger.info("Email sent successfully.")
        else:
            logger.error("Email sending failed.")
    else:
        logger.info("Email disabled — skipping.")

    logger.info("Done.")
    logger.info("=" * 60)


def start_schedule(config: dict) -> None:
    sched_cfg = config.get("schedule", {})
    run_time = sched_cfg.get("run_time", "05:00")
    tz_name = sched_cfg.get("timezone", "Asia/Taipei")

    logger.info(f"Scheduler started. Will run daily at {run_time} ({tz_name}).")

    tz = pytz.timezone(tz_name)

    def job_wrapper():
        now = datetime.now(tz)
        logger.info(f"Triggered at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        run_job(config)

    schedule.every().day.at(run_time).do(job_wrapper)

    while True:
        schedule.run_pending()
        time.sleep(30)


def main():
    parser = argparse.ArgumentParser(description="Finance News Crawler")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-now", action="store_true", help="Run immediately and exit")
    group.add_argument("--schedule", action="store_true", help="Start daemon/schedule mode")
    args = parser.parse_args()

    config = load_config()

    if args.run_now:
        run_job(config)
    elif args.schedule:
        sched_cfg = config.get("schedule", {})
        if not sched_cfg.get("enabled", False):
            logger.warning("schedule.enabled is false in config.yaml. Running once and exiting.")
            run_job(config)
        else:
            start_schedule(config)


if __name__ == "__main__":
    main()

# Goodreads Data Pipeline

## Introduction
Reading is one my favorite activies. Whether I'm convering the decline of the Roman empire or diving into a massive fantasy series, I like to end each day by picking up a book. Though I enjoy the act, I've always struggled in finding that "next" book to read. I currently track my reading activity through Goodreads, which is part social media and part book database. My previous strategy was to sift through Reddit for recommendations and then dig through the reviews on Goodreads which too look far too long. I knew their was a better way to tackle this problem!

In this project, my goal is to succintly present book data so that I can help readers spend less time searching and more time reading.

## Architecture
The overarching architecture is following an ELT approach which is short for Extract, Load, and Transform. At a high level, this pipeline follows this chain:
1. Extract data via web scraping
2. Load to data lake
3. Load to data warehouse
4. Transform warehouse data
5. Visualize


![Goodreads Data Pipeline](https://github.com/user-attachments/assets/4c38c82c-8b21-4ae9-9bc2-8b7f7bca286f)

**Cloud Vendor**: Google Cloud Plaform <br />
**Infrastructure Deployment**: Terraform <br />
**Compute**: GCP VM Instance and BigQuery <br />
**Containerization**: Docker Compose <br />
**Orchestration**: Airflow <br />
**Ingestion**: Beautiful Soup Web Scraper <br />
**Storage**: GCP Cloud Storage <br />
**Transformation**: dbt Cloud <br />
**Reporting**: Looker Studio <br />


## Prerequisites


## Infrastructure

## Containerization

## Orchestration

![image](https://github.com/user-attachments/assets/e0ebd828-afab-4152-bfc2-ec4930236100)

## Web Scraping

## Storage

## Transformation

## Data Warehouse

## Visualization

## Conclusion

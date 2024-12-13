# Goodreads Data Pipeline

## Introduction
Reading is one my favorite activies. Whether I'm convering ancient history or , I try to spend at least some amount of time reading each day. Though I enjoy the act, I've always struggled in finding that "next" book to read. I currently track my reading activity through Goodreads, which is part social media and part book database. My previous strategy was to sift through Reddit for recommendations and then dig through the reviews on Goodreads which too look far too long. I knew there was a better way to tackle this problem! 

The following project is a data pipeline which ingests, loads, and transforms book data on a daily cadence. A dashboard then consumes this data and provides actionable insights so that users can spend less time researching and more time reading.

This project leans on what I've learned in the Data Engineer Zoomcamp. Thank you to Alexey and team for the content!

## Architecture
The architecture for this pipeline follows an ELT approach which is short for Extract, Load, and Transform. At a high level, the pipeline follows this:
1. Extract data via web scraping
2. Load to data lake
3. Load to data warehouse
4. Transform warehouse data
5. Visualize


![Goodreads Data Pipeline](https://github.com/user-attachments/assets/4c38c82c-8b21-4ae9-9bc2-8b7f7bca286f)

**Cloud Vendor**: Google Cloud Plaform <br />
**Infrastructure Deployment**: Terraform <br />
**Compute**: GCP VM Instance and BigQuery Compute <br />
**Containerization**: Docker Compose <br />
**Orchestration**: Airflow <br />
**Ingestion**: Beautiful Soup Web Scraper <br />
**Storage**: GCP Cloud Storage <br />
**Transformation**: dbt Cloud <br />
**Reporting**: Looker Studio <br />


## Prerequisites

The following preqs are free and relatively straightforward to setup

- Google Cloud account
- dbt Cloud account
- Github account

## Infrastructure

All of the core infrastructure is from Google Cloud:

**VM Instance** <br />



**Cloud Storage** <br />



**BigQuery** <br />



## Containerization




## Orchestration

Orchestration is handled by Airflow running on a Docker image inside the VM Instance. 

![image](https://github.com/user-attachments/assets/e0ebd828-afab-4152-bfc2-ec4930236100)

## Web Scraping

The first challenge of this project was figuring out how to extract data from Goodreads. Ideally we could use their API, but the company recently stopped issuing API keys. With that in mind, I started learning about webscraping. Though its not nearly as efficient, we can still extract meaningful data in a reasonble amount of time since the volume is so low. 



## Storage

The data lake in which to store the raw Parquet files from the scraper is Google Cloud Storage. As mentioned prior, the container was deployed via Terraform. I also made sure that the files are stored thoughtfully in the following folder hierarchy:

- Year
- 

## Transformation

## Data Warehouse

## Visualization

## Conclusion

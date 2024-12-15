# Goodreads Data Pipeline

## Introduction
Reading is one my favorite activies. Whether I'm learning about art history or binging a fantasy series, I've always enjoyed the educational and entertainment benefits of reading each day. Though I enjoy the act, I've always struggled in finding that "next" book to read. I currently track my reading activity through Goodreads, which is part social media and part book database. This is also the place where I sift through reviews on unread books to decide which book to buy next. This is a time consuming process however so I wanted to create a more concise solution with a better signal to noise ratio. 

The following project is a data pipeline which ingests, loads, and transforms book data on a daily cadence. A dashboard then consumes this data and provides actionable insights so that users can spend less time researching and more time reading.

This project leverages I've learned in the Data Engineering Zoomcamp. Thank you to Alexey and team for the content!

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

- Google Cloud account
- dbt Cloud account
- Github account
- Python 3
- Git Bash
- Visual Studio Code

## Web Scraping

Before diving into the pipeline, I needed to get a working script to ingest data from Goodreads and drop to a file. Ideally I could use their API, but the company recently stopped issuing API keys. With that in mind, I started learning about webscraping. Though its not nearly as efficient, we can still extract meaningful data in a reasonble amount of time since the volume is so low. I decided to focus specifically on the "Most Read This Week" books per genre. I started with the genre page and extraced just the urls for each of the 40 genres.

If I navigate to one to a genre, we can see 100 books on the page. When selecting an individual book, we can now see some meaningful data such as Publishing Date, Author, Number of Page, and Review data. Each book will ultimately be the grain of the dataset. To illustrate, this is how one example will appear if I save as a CSV:





At a high level, this is what the scraper is doing:

Extract list of genre URL's from the HTML and add to a list
Loop through the list and extract the book URLS from each and add to another list
Perform the scraping via the BLANK function and drop to a json file
Add each json to a list and generate one pandas dataframe
Conver the pandas dataframe to a parquet file



## Infrastructure

All of the core resources for this project are provided by Google Cloud: <br />
- VM Instance  <br />
- Cloud Storage <br />
- BigQuery  <br />

### VM Instance

The nucleus of this project is a virtual machine created via the Console



This machine has the following settings:



One can access the VM remotely through the following steps:

Create key in Console

Create hidden directory on local machines root (~) directory

Access the file via VS Code and paste the private key into .....





In addition to the compute resource, I am using Cloud Storage for the data lake and BigQuery for the data warehouse. These resources differ in that they were deployed via Terraform. This tool allows the user to use code to deploy resources without needing the Console UI. The VM can also be deployed using Terraform if needed. During testing, I was dropping and recreating the storage containers and BQ datasets on a regular basis (as opposed to just creating the VM once), so Terraform was a great tool to drop and replace resources efficiently.

The terraform folder has the main.tf and varibables.tf files which define the resources. To deploy, one runs the following commands sequentially on the VM: <br />





## Containerization









## Orchestration

Orchestration is handled by Airflow running on a Docker image inside the VM Instance. 

![image](https://github.com/user-attachments/assets/e0ebd828-afab-4152-bfc2-ec4930236100)


## Storage

The data lake in which to store the raw Parquet files from the scraper is Google Cloud Storage. As mentioned prior, the container was deployed via Terraform. I also made sure that the files are stored thoughtfully in the following folder hierarchy:

- Year
- 


## Data Warehouse 

## Transformation

## Visualization

## Conclusion

import os
import pendulum
import requests
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

start_time = datetime.now()

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
    response = requests.get(f"{url}", headers=headers)
    response = response.text
    soup = BeautifulSoup(response, 'lxml')
    return soup

parent_genre_url = 'https://www.goodreads.com/genres'
base_url = 'https://www.goodreads.com/'
genre_soup = get_soup(parent_genre_url)
genre_div = genre_soup.find_all('div',class_="rightContainer")

# Create and populate list of genre urls
genre_url_list = []
for child_div in genre_div:
    subchild_div = child_div.find_all('div', class_='left')
    for left_tag in subchild_div:
       a_tag = left_tag.find_all('a')
       for h_ref in a_tag:
            sub_directory = h_ref.get('href')
            split_list = sub_directory.split('/')
            final_url = base_url + split_list[1] + '/' + 'most_read' + '/' + split_list[2]
            genre_url_list.append(final_url)

# Create and populate list of book urls
book_url_list = []
for genre_url in genre_url_list:
    book_list_soup = get_soup(genre_url)
    book_list_div = book_list_soup.find_all('div', class_="leftAlignedImage bookBox")
    genre = genre_url.split('/most_read/')[1]
    # 10 books per genre
    for book_url_div in book_list_div[0:10]:
        try:
            book_url_full = book_url_div.find('a')['href']
            book_url = base_url + book_url_full
            book_url_genre = dict(book_url = book_url, genre = genre)
            book_url_list.append(book_url_genre)
        except TypeError:
            pass

# Book scraping function
def book(book_url,genre):
    book_soup = get_soup(book_url)
    try:
        book_div = book_soup.find('script', type="application/ld+json")
    except AttributeError:
        book_div = "None"
    try:
        publish_div = book_soup.find("div", class_="BookDetails").find("div", class_="FeaturedDetails").find_all("p")
    except AttributeError:
        publish_div = 'None'

    try:
        script_json = json.loads(book_div.string)
        title = script_json['name']
        author = script_json['author'][0]['name']
        no_pages = script_json['numberOfPages']
        rating_count = script_json['aggregateRating']['ratingCount']
        average_rating =  script_json['aggregateRating']['ratingValue']
        review_count = script_json['aggregateRating']['reviewCount']
    except (TypeError,KeyError,AttributeError,IndexError):
        title = "none"
        author = "none"
        no_pages = "-1"
        rating_count = "-1"
        average_rating = "-1"
        review_count = "-1"
    try:
        isbn = script_json['isbn']
    except KeyError:
        isbn = "none"
    try:
        publish_date = publish_div[1].text.split("First published")[1].strip()
    except (TypeError,KeyError,AttributeError,IndexError):
        publish_date = "none"

    book_dict = {
        "Title": title, 
        "Author": author,
        "Genre": genre,
        "NumberOfPages": str(no_pages),
        "PublishDate": publish_date,
        "RatingCount": str(rating_count),
        "AverageRating": str(average_rating),
        "ReviewCount": str(review_count),
        "ISBN": isbn
    }

    return book_dict

def main():
    book_list = []
    for book_pair in book_url_list:
        book_url = book_pair['book_url']
        genre = book_pair['genre']
        book_dict = book(book_url,genre)
        book_list.append(book_dict)
        
    df = pd.DataFrame(book_list)

    date_string = pendulum.now('UTC').format('YYYYMMDD')
    airflow_file_path = os.environ.get("AIRFLOW_HOME","/opt/airflow/")
    file_name = f"goodreads_{date_string}.parquet"
    df.to_parquet(f'{airflow_file_path}/data/{file_name}')

if __name__ == "__main__": 
    main()

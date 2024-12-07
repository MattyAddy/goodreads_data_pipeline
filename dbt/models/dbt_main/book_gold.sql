{{
    config(
        materialized='incremental',
        unique_key='book_id'
    )
}}

{% set now = modules.datetime.datetime.now() %}

with cte_silver as (
    select 
        book_id,
        title,
        author,
        genre,
        numberofpages,
        publishdate,
        ratingcount,
        averagerating,
        reviewcount,
        isbn,
        bookurl,
        cast('{{ now }}' as datetime) as insertdatetime
    from {{ ref('book_silver_stg') }}
)

select 
    book_id,
    title,
    author,
    genre,
    numberofpages,
    publishdate,
    ratingcount,
    averagerating,
    reviewcount,
    isbn,
    bookurl,
    insertdatetime
from cte_silver s

{% if is_incremental() %}

where s.insertdatetime >= (select max(insertdatetime) from {{ this }})

{% endif %}
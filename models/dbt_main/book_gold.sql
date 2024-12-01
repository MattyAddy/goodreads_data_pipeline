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
        cast('{{ now }}' as datetime) as insertdatetime,
        cast('{{ now }}' as datetime) as updatedatetime
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
    insertdatetime,
    updatedatetime
from cte_silver

{% if is_incremental() %}

where '{{ now }}' >= (select max(insertdatetime) from {{ this }})

{% endif %}
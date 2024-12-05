{{
    config(
        materialized='incremental',
        unique_key='book_id'
    )
}}

{% set now = modules.datetime.datetime.now() %}

with cte_fact as (
    select 
        book_id,
        title,
        a.author_dim_id,
        g.genre_dim_id,
        publishdate,
        numberofpages,
        ratingcount,
        averagerating,
        reviewcount,
        isbn,
        cast('{{ now }}' as datetime) as insertdatetime
    from {{ ref('book_gold') }} b
    left join {{ ref('dim_author') }} a ON a.author = b.author
    left join {{ ref('dim_genre') }} g ON g.genre = b.genre
)

select 
    book_id,
    title,
    author_dim_id,
    genre_dim_id,
    publishdate,
    numberofpages,
    ratingcount,
    averagerating,
    reviewcount,
    isbn,
    insertdatetime
from cte_fact s

{% if is_incremental() %}

where s.insertdatetime >= (select max(insertdatetime) from {{ this }})

{% endif %}


{{
    config(
        materialized = 'table'
    )
}}

{% set now = modules.datetime.datetime.now() %}

select distinct
    {{ dbt_utils.generate_surrogate_key(['author']) }} as author_dim_id,
    author,
    cast('{{ now }}' as datetime) as insertdatetime
from {{ ref('book_gold') }}

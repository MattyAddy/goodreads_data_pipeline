{% set models_to_generate1 = codegen.get_models(directory='dbt_main', prefix='book_gold') %}
{{ codegen.generate_model_yaml(
    model_names = models_to_generate1
) }}
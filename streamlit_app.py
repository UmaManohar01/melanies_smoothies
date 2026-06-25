import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Title and intro
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Text input for customer name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Query fruit names and search values
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# TEMPORARY DEBUG LINES (workshop asked for these)
st.dataframe(pd_df)
st.stop()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )

        st.subheader(fruit_chosen + ' Nutrition Information')

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    ingredients_string = ingredients_string.strip()

    if name_on_order:

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(NAME_ON_ORDER, INGREDIENTS)
        VALUES (
            '{name_on_order.replace("'", "''")}',
            '{ingredients_string.replace("'", "''")}'
        )
        """

        if st.button('Submit Order'):
            session.sql(my_insert_stmt).collect()
            st.success(
                f"Your Smoothie is ordered, {name_on_order}!",
                icon="✅"
            )

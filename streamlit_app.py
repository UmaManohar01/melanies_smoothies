import streamlit as st
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

# Query fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row.FRUIT_NAME for row in my_dataframe.collect()]

# Multiselect returns the chosen items
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

# Build string only if something is selected
ingredients_string = " ".join(ingredients_list) if ingredients_list else ""
st.write("Ingredients as string:", ingredients_string if ingredients_string else "No fruits selected yet.")

# Stop execution if name or ingredients are missing
if not (ingredients_string and name_on_order):
    st.warning("Please enter a name and select at least one fruit before submitting.")
    st.stop()

# Prepare SQL safely
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(NAME_ON_ORDER, INGREDIENTS)
    VALUES (
        '{name_on_order.replace("'", "''")}',
        '{ingredients_string.replace("'", "''")}'
    )
"""

st.write("SQL to be executed:", my_insert_stmt)

# Button to submit order
if st.button('Submit Order'):
    session.sql(my_insert_stmt).execute()
    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

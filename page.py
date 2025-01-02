import requests
import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt 


# Your Google Books API key
api = "AIzaSyCLFndPwb0LWBJmBMb38p46-MMq7FlCXrE"

# Function to fetch books from Google Books API
def fetch_books(query, api, max_results=50):
    books = []
    link = "https://www.googleapis.com/books/v1/volumes"
    start_index = 0
    max_per_request = 40

    while start_index < max_results:
        params = {
            "q": query,
            "key": api,
            "startIndex": start_index,
            "maxResults": min(max_per_request, max_results - start_index),
        }
        response = requests.get(link, params=params)
        if response.status_code != 200:
            st.error(f"Error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        for item in items:
            volume_info = item.get("volumeInfo", {})
            sale_info = item.get("saleInfo", {})
            books.append({
                "book_id": item.get("id", None),
                "search_key": query,
                "book_title": volume_info.get("title", None),
                "book_subtitle": volume_info.get("subtitle", "NA"),
                "book_authors": ", ".join(volume_info.get("authors", [])),
                "book_description": volume_info.get("description", "NA"),
                "industryIdentifiers": ", ".join([identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', [])]),
                "text_readingModes": volume_info.get("readingModes", {}).get("text", False),
                "image_readingModes": volume_info.get("readingModes", {}).get("image", False),
                "pageCount": volume_info.get("pageCount", None),
                "categories": ", ".join(volume_info.get("categories", [])),
                "language": volume_info.get("language", None),
                "imageLinks": volume_info.get("imageLinks", {}).get("thumbnail", None),
                "ratingsCount": volume_info.get("ratingsCount", None),
                "averageRating": volume_info.get("averageRating", None),
                "country": sale_info.get("country", None),
                "saleability": sale_info.get("saleability", None),
                "isEbook": sale_info.get("isEbook", False),
                "amount_listPrice": sale_info.get("listPrice", {}).get("amount", None),
                "currencyCode_listPrice": sale_info.get("listPrice", {}).get("currencyCode", None),
                "amount_retailPrice": sale_info.get("retailPrice", {}).get("amount", None),
                "currencyCode_retailPrice": sale_info.get("retailPrice", {}).get("currencyCode", None),
                "buyLink": sale_info.get("buyLink", None),
                "year": volume_info.get("publishedDate", "").split("-")[0]  # Extract year from publishedDate
            })
        start_index += max_per_request

    return books

# MySQL connection function
def get_mysql_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="books"
    )

# Streamlit Application
st.title("Books Explorer 📚")

# Tabs for navigation
tab1, tab2 = st.tabs(["Home", "Books Analysis"])

# Home Tab
with tab1:
    st.header("Books Table")
    search_query = st.text_input("Enter your search query:", "")
    if search_query:
        st.write(f"Searching for: **{search_query}**")
        books_data = fetch_books(search_query, api)
        if books_data:
            books_df = pd.DataFrame(books_data)
            st.dataframe(books_df)
        else:
            st.warning("No books found. Please try a different query.")


# Analysis Tab
with tab2:
    st.header("Books Analysis")

    # SQL Queries
    conn = get_mysql_connection()
    if conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
    queries = {
        "1.Check Availability of eBooks vs Physical Books": """
            SELECT CASE 
                WHEN isEbook = 1 THEN 'eBook' 
                ELSE 'Physical Book' END AS Book_Type, 
                COUNT(*) AS Count 
            FROM books GROUP BY Book_Type;
        """,
        "2.Find the Publisher with the Most Books Published": """
            SELECT book_authors, 
                COUNT(*) AS book_count
            FROM books GROUP BY book_authors
            ORDER BY book_count DESC
            LIMIT 3;
        """,
        "3.Identify the Publisher with the Highest Average Rating": """
            SELECT b.book_authors AS author_name,
            AVG(b.averageRating) AS average_rating
            FROM books b
            GROUP BY b.book_authors
            ORDER BY average_rating DESC
            limit 10;
        """,
          "4.Get the Top 5 Most Expensive Books by Retail Price": """
        SELECT book_title, amount_retailPrice,currencyCode_retailPrice
FROM books
ORDER BY amount_retailPrice DESC
LIMIT 5;
    """,
    "5.Find Books Published After 2010 with at Least 500 Pages": """
      SELECT book_title, year, pageCount
FROM books
WHERE year > 2010 AND pageCount >= 500;
    """,
    "6.List Books with Discounts Greater than 20%": """
       SELECT book_title,amount_listPrice,amount_retailPrice,currencyCode_listPrice,currencyCode_retailPrice,
       ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 AS discount_percentage
FROM books
WHERE ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 > 20;
    """,
    "7.Find the Average Page Count for eBooks vs Physical Books": """
       SELECT CASE 
        WHEN isEbook = 1 THEN 'eBook'
        ELSE 'Physical Book'
    END AS book_type,
    AVG(pageCount) AS average_page_count
FROM books GROUP BY book_type;
    """,
  "8.Find the Top 3 Authors with the Most Books": """
     SELECT book_authors, 
       COUNT(*) AS book_count
FROM books GROUP BY book_authors
ORDER BY book_count DESC
LIMIT 3;
 """,

    "9.List Publishers with More than 10 Books ":"""
      SELECT book_authors, 
       COUNT(*) AS book_count
FROM books GROUP BY book_authors
HAVING COUNT(*) > 10
ORDER BY book_count DESC;
    """,
  "10.Find the Average Page Count for Each Category": """
    SELECT categories,
       AVG(pageCount) AS average_page_count
FROM books
GROUP BY categories
ORDER BY average_page_count DESC;
""",
"11.Retrieve Books with More than 3 Authors": """
  
SELECT book_title, 
       book_authors
FROM books
WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;
""",
   "12.Books with Ratings Count Greater Than the Average": """
 SELECT book_title, 
       ratingsCount
FROM books
WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM books);
    """,
    "13.Books with the Same Author Published in the Same Year": """
  SELECT book_title, book_authors, year
FROM books
WHERE (book_authors, year) IN (SELECT book_authors, year FROM books
GROUP BY book_authors, year
    HAVING COUNT(*) > 1
)
ORDER BY book_authors, year;
    """,
    "14.Books with a Specific Keyword in the Title": """
     SELECT book_title, book_authors, year
FROM books
WHERE book_title LIKE '%Adventure%';
    """,
    "15.Year with the Highest Average Book Price": """
   SELECT year, 
       AVG(amount_retailPrice) AS average_price
FROM books GROUP BY year
ORDER BY average_price DESC
LIMIT 1
    """,
    "16.Count Authors Who Published 3 Consecutive Years": """
       SELECT book_authors,
       COUNT(DISTINCT year) AS published_years_count
FROM books
GROUP BY book_authors
HAVING COUNT(DISTINCT year) >= 2
   AND MIN(year) + 1 = MAX(year)
ORDER BY book_authors;
    """,
  "17.Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.": """
 SELECT book_authors, 
       year, 
       COUNT(*) AS book_count,
       COUNT(DISTINCT book_id) AS distinct_publishers
FROM books
GROUP BY book_authors, year
HAVING COUNT(DISTINCT book_id) > 1
ORDER BY book_authors, year;
 """,

    "18.Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries. ":"""
      SELECT 
    AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice ELSE NULL END) AS avg_ebook_price,
    AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice ELSE NULL END) AS avg_physical_price
FROM books;
    """,
  "19.Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.": """
    WITH stats AS (
    SELECT AVG(averageRating) AS avg_rating,
        STDDEV(averageRating) AS stddev_rating
    FROM books
)
SELECT book_title, averageRating, ratingsCount
FROM books, stats
WHERE 
    averageRating > (stats.avg_rating + 2 * stats.stddev_rating)
    OR averageRating < (stats.avg_rating - 2 * stats.stddev_rating);

""",
"20.Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published.": """
  
SELECT b.book_authors, 
       AVG(b.averageRating) AS avg_rating, 
       COUNT(b.book_id) AS num_books
FROM books b
GROUP BY b.book_authors
HAVING COUNT(b.book_id) > 4
ORDER BY avg_rating DESC;
"""
 }
  # Execute queries and fetch data
    for query_name, query in queries.items():
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            with st.expander(query_name):
                df = pd.DataFrame(data)
                for row in data:
                    st.write(row) 
                if query_name == "1.Check Availability of eBooks vs Physical Books":
                    st.bar_chart(df.set_index("Book_Type")["Count"])
                    
                elif query_name == "2.Find the Publisher with the Most Books Published":
                    st.bar_chart(df.set_index("book_authors")["book_count"])
                    
                elif query_name == "3.Identify the Publisher with the Highest Average Rating":
                    st.bar_chart(df.set_index("author_name")["average_rating"])
                    
                elif query_name == "4.Get the Top 5 Most Expensive Books by Retail Price":
                    st.bar_chart(df.set_index("book_title")["amount_retailPrice"])
                    
                elif query_name == "5.Find Books Published After 2010 with at Least 500 Pages": 
                    st.bar_chart(df.set_index("book_title")["pageCount"])
                    
                elif query_name == "6.List Books with Discounts Greater than 20%":
                    st.bar_chart(df.set_index("book_title")["discount_percentage"])
                    
                elif query_name == "7.Find the Average Page Count for eBooks vs Physical Books":
                    st.bar_chart(df.set_index("book_type")["average_page_count"])
                    
                elif query_name == "8.Find the Top 3 Authors with the Most Books":
                    st.bar_chart(df.set_index("book_authors")["book_count"])
                    
                elif query_name == "9.List Publishers with More than 10 Books ":
                    st.bar_chart(df.set_index("book_authors")["book_count"])
                    
                elif query_name == "10.Find the Average Page Count for Each Category":
                    st.bar_chart(df.set_index("categories")["average_page_count"])
                    
                elif query_name == "11.Retrieve Books with More than 3 Authors":
                    st.bar_chart(df.set_index("book_title")["book_authors"])
                    
                elif query_name == "12.Books with Ratings Count Greater Than the Average":
                    st.bar_chart(df.set_index("book_title")["ratingsCount"])
                    
                elif query_name == "13.Books with the Same Author Published in the Same Year":
                    st.bar_chart(df.set_index("book_title")["year"])
                    
                elif query_name == "14.Books with a Specific Keyword in the Title":
                    st.bar_chart(df.set_index("book_title")["year"])
                    
                elif query_name == "15.Year with the Highest Average Book Price":
                    st.bar_chart(df.set_index("year")["average_price"])
                    
                elif query_name == "16.Count Authors Who Published 3 Consecutive Years":
                    st.bar_chart(df.set_index("book_authors")["published_years_count"])
                    
                elif query_name == "17.Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.":
                    st.bar_chart(df.set_index("book_authors")["book_count"])
                    
                elif query_name == "18.Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries. ":
                    st.bar_chart(df.set_index("avg_ebook_price")["avg_physical_price"])
                    
                elif query_name == "19.Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.":
                    st.bar_chart(df.set_index("book_title")["averageRating"])
                    
                elif query_name == "20.Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published.":
                    st.bar_chart(df.set_index("book_authors")["avg_rating"])
                    
        
                else:
                    st.warning(f"No data available for query: {query_name}")

    conn.close()
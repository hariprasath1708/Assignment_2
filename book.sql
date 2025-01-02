create database books;
use books;
Show tables;

select*from books;

DESCRIBE books;

SELECT COUNT(*) FROM books;

SELECT CASE 
        WHEN isEbook = 1 THEN 'eBook' 
        ELSE 'Physical Book' END AS Book_Type, 
    COUNT(*) AS Count 
FROM books GROUP BY Book_Type;

#2) Find the Publisher with the Most Books Published

SELECT book_authors, 
    COUNT(*) AS book_count
FROM books GROUP BY book_authors
ORDER BY book_count DESC
LIMIT 3;

#3) Identify the Publisher with the Highest Average Rating

SELECT b.book_authors AS author_name,
       AVG(b.averageRating) AS average_rating
FROM books b
GROUP BY b.book_authors
ORDER BY average_rating DESC
limit 10;

#4) Get the Top 5 Most Expensive Books by Retail Price

SELECT book_title, amount_retailPrice,currencyCode_retailPrice
FROM books
ORDER BY amount_retailPrice DESC
LIMIT 5;

#5)Find Books Published After 2010 with at Least 500 Pages

SELECT book_title, year, pageCount
FROM books
WHERE year > 2010 AND pageCount >= 500;

#6)List Books with Discounts Greater than 20%

SELECT book_title,amount_listPrice,amount_retailPrice,currencyCode_listPrice,currencyCode_retailPrice,
       ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 AS discount_percentage
FROM books
WHERE ((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100 > 20;

#7)Find the Average Page Count for eBooks vs Physical Books

SELECT CASE 
        WHEN isEbook = 1 THEN 'eBook'
        ELSE 'Physical Book'
    END AS book_type,
    AVG(pageCount) AS average_page_count
FROM books GROUP BY book_type;

#8)Find the Top 3 Authors with the Most Books

SELECT book_authors, 
       COUNT(*) AS book_count
FROM books GROUP BY book_authors
ORDER BY book_count DESC
LIMIT 3;

#9)List Publishers with More than 10 Books 
#highest value is 7 books

SELECT book_authors, 
       COUNT(*) AS book_count
FROM books GROUP BY book_authors
HAVING COUNT(*) > 10
ORDER BY book_count DESC;

#10)Find the Average Page Count for Each Category

SELECT categories,
       AVG(pageCount) AS average_page_count
FROM books
GROUP BY categories
ORDER BY average_page_count DESC;

#11)Retrieve Books with More than 3 Authors

SELECT book_title, 
       book_authors
FROM books
WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;

#12)Books with Ratings Count Greater Than the Average

SELECT book_title, 
       ratingsCount
FROM books
WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM books);

#13)Books with the Same Author Published in the Same Year

SELECT book_title, book_authors, year
FROM books
WHERE (book_authors, year) IN (SELECT book_authors, year FROM books
GROUP BY book_authors, year
    HAVING COUNT(*) > 1
)
ORDER BY book_authors, year;

#14)Books with a Specific Keyword in the Title

SELECT book_title, book_authors, year
FROM books
WHERE book_title LIKE '%Adventure%';

#15)Year with the Highest Average Book Price

SELECT year, 
       AVG(amount_retailPrice) AS average_price
FROM books GROUP BY year
ORDER BY average_price DESC
LIMIT 1

#16)Count Authors Who Published 3 Consecutive Years

SELECT book_authors,
       COUNT(DISTINCT year) AS published_years_count
FROM books
GROUP BY book_authors
HAVING COUNT(DISTINCT year) >= 2
   AND MIN(year) + 1 = MAX(year)
ORDER BY book_authors;

#17)Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.
SELECT book_authors, 
       year, 
       COUNT(*) AS book_count,
       COUNT(DISTINCT book_id) AS distinct_publishers
FROM books
GROUP BY book_authors, year
HAVING COUNT(DISTINCT book_id) > 1
ORDER BY book_authors, year;

#18)Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.

SELECT 
    AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice ELSE NULL END) AS avg_ebook_price,
    AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice ELSE NULL END) AS avg_physical_price
FROM books;

#19)Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.

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

#20)Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published.

SELECT b.book_authors, 
       AVG(b.averageRating) AS avg_rating, 
       COUNT(b.book_id) AS num_books
FROM books b
GROUP BY b.book_authors
HAVING COUNT(b.book_id) > 4
ORDER BY avg_rating DESC;






# Movie Id Scraper

I am doing pro bono work in upwork.com for my portfolio, that is one of the projects i chose to do.

This is a program that scrapes the live feed of hdss.to, and matches their corresponding id's in themoviedb.org
and finally saves them your google spreadsheet.


# Job Posting 
https://www.upwork.com/jobs/~01820e85810cfbdc3e

Job Posting Says:
I need a bot-automation to scrap data from a website (titles, descriptions etc )https://hdss.to/ and scrap the 
Tmdb ID (https://www.themoviedb.org/?language=fr-CA) that match the movie/tv show and add it on a (created) live database 
(google spreadsheet).

The bot will have to update the database everything new data are upload to the feed.

# How Scraper Works?

You will see 'credentials.json' file in project files. It's empty. You should replace it with your Google Spreadsheet API
credential file, and name it 'credential.json'

Now you can start the main.py with or without command line arguments. 


# First Time Running The Program

In first running, program will open the browser and ask you to sign in with your google account. After that, this process won't repeat.
Then, it will create a spreadsheet named 'Movie Data' in your drive and will start scraping as expected.

# Command Line Arguments
You can specify -sec argument to set a timer in seconds for waiting before the program scrapes again.

For example, if you run:
python3 main.py --sec=60

Program will scrape the movie data, and waits for 60 seconds. Then it will scrape again.
Since movie data isn't that volatile, I Recommend 10 minutes (600 seconds) for that parameter.

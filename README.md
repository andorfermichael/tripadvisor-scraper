# TripAdvisor Scraper

Scrape the hotel reviews of a whole city on [TripAdvisor](http://www.tripadvisor.com).

## Requirements

- python 3.5

## Installation & Setup
Download and install required libs and data:
```bash
pip install bs4
```

## Usage Scraper
Store all reviews of New York City:
```python
python tripadvisor-scraper.py 60763 New_York_City_New_York
```

Store all reviews of Paris:
```python
python tripadvisor-scraper.py 187147 Paris_Ile_de_France
```

Store all reviews of Vienna:
```python
python tripadvisor-scraper.py 190454 Vienna
```

The scraper requires the ```city location id``` and the ```city name``` as commandline arguments.
Both can be retrieved from the url, for example, ```https://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html```
The ```city location id``` is the number after the g. The ```city name``` is the string from the dash after the ```city location id``` to the dash before ```Hotels```.

Store all reviews of Vienna and additionally store the review urls list as pickle for rescraping later:
```python
python tripadvisor-scraper.py 190454 vienna --pickle store
```
A pickle is stored in ```data/timestamp-cityname```


Store all reviews of Vienna using a review urls list loaded from pickle/20160601-1522-vienna.pickle:
```python
python tripadvisor-scraper.py 190454 Vienna --pickle load --filename 20160601-1522-vienna.pickle
```

A pickle to load has to be placed in the pickle directory at the same directory level as the ```tripadvisor-scraper.py```

## Usage Totalizer
Put all reviews and hotel information of a city together:
```python
python tripadvisor-totalizer.py /Users/admin/tripadvisor-scraper/data/20160716-202314-vienna
```

## Author

[Michael Andorfer](mailto:mandorfer.mmt-b2014@fh-salzburg.ac.at)
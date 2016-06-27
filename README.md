# TripAdvisor Scrapper

```TripAdvisor Scrapper``` scrapes the reviews of a whole city on [TripAdvisor](http://www.tripadvisor.com).

## Requirements

- python 3.5

## Installation & Setup
Download and install required libs and data:
```bash
pip install bs4
```

## Usage
Store all reviews of New York City:
```python
python tripadvisor-scrapper 60763 New_York_City_New_York
```

Store all reviews of Paris:
```python
python tripadvisor-scrapper 187147 Paris_Ile_de_France
```

Store all reviews of Vienna:
```python
python tripadvisor-scrapper 190454 Vienna
```

The scrapper requires the ```city location id``` and the ```city name``` as commandline arguments.
Both can be retrieved from the url, for example, ```https://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html```
The ```city location id``` is the number after the g. The ```city name``` is the string from the dash after the ```city location id``` to the dash before ```Hotels```.
# Broken Link Checker

## Steps

1. Install dependencies:

```commandline
pip install -r requirements.txt
```

2. Update `START_PAGE = 'https://www.scrapebay.com'`
   in [broken_links/spiders/find_broken.py](broken_links/spiders/find_broken.py)
2. Run the spider:

```commandline
scrapy crawl find_broken -o output_file.csv
```

## Video Walkthrough

Visit https://www.youtube.com/watch?v=dmtHyl8nLMI

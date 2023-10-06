import requests
from bs4 import BeautifulSoup


def headline_tag(tag, tag_text, seen_text, webpage_text):
    webpage_text += f"{tag_text}"
    for span_tag in tag.find_all('span'):  # Find all span tags in headline, if there is one
        span_text = span_tag.text.strip()
        if span_text not in seen_text:  # Check if text has already been seen
            seen_text.add(span_text)
            webpage_text += f"{span_text}"
    webpage_text += "\n"
    return seen_text, webpage_text


def scrape_page(url, depth=0, max_depth=3):
    if depth > max_depth:
        return
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(f"{'  ' * depth}Scraping: {url}")

    webpage_text = ""
    tags = [f'h{i}' for i in range(1, 7)]
    tags.append('p')
    # tags -> [h1,h2,h3,h4,h5,h6,p]

    seen_text = set()

    for div in soup.find_all('div'):
        for tag in div.find_all(tags):  # Find all headlines and paragraphs in div
            tag_text = tag.text.strip()
            if tag_text not in seen_text:  # Check if text has already been seen
                seen_text.add(tag_text)

                if tag.name.startswith('h'):  # Check if tag is a headline (h1,h2,h3,...)
                    seen_text, webpage_text = headline_tag(tag, tag_text, seen_text, webpage_text)
                else:  # tag is a paragraph
                    webpage_text += tag_text + "\n"

    print(webpage_text)
    #
    #Check if sublevel is not repeated!!!!!!!!!!!!!!!!!
    # # Scrape subleves
    # for link in soup.find_all('a'):
    #     href = link.get('href')
    #     if href and href.startswith('http'):
    #         scrape_page(href, depth + 1, max_depth)


# Example usage
scrape_page("https://www.accesscity.es/")

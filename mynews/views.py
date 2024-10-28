from django.shortcuts import render,get_object_or_404
import requests
from bs4 import BeautifulSoup
from .models import News
from django.core.paginator import Paginator
# Create your views here.

import re
from bs4 import BeautifulSoup
import requests


from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from .models import News, Category as NewsCategory
# Create your views here.


#api handling
#apiKey = '8abf0c99c012459aa8a1f1bf1b7e091f'
apiKey = '49b580ec3f5740b19d1c1f4948c39e62' #second
def news_url(keyword, apiKey):
    return f'https://newsapi.org/v2/everything?q=kenyan {keyword}&from=2024-09-16&sortBy=publishedAt&apiKey={apiKey}'

def clean_content(text):
    # List of common unwanted patterns
    unwanted_phrases = [
        r'CHECK OUT:', r'ENROLL NOW', r'SUBSCRIBE', r'PAY ATTENTION:',
        r'Sponsored', r'Proofreading by', r'Source:', r'Read also',
        r'WhatsApp Channels', r'Contact us:', r'Click here', r'TUKO.co.ke', r'chars', r'Survey'
    ]

    # Join unwanted phrases into a regex pattern and remove them
    unwanted_pattern = '|'.join(unwanted_phrases)
    cleaned_text = re.sub(unwanted_pattern, '', text, flags=re.IGNORECASE)

    # Remove extra spaces, newlines, or unusual characters
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def get_article_content(url):
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    LANGUAGE = 'en-US,en;q=0.5'

    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE

    try:
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to find article content using different strategies
            article_content = (
                soup.find('div', class_='article-content') or
                soup.find('article') or
                soup.find('div', class_='main-content') or
                soup.find('div', class_='entry-content') or
                soup.find('section', class_='content') or
                soup.find('div', id='articleBody')
            )

            if article_content:
                # Extract paragraphs
                paragraphs = article_content.find_all('p')
                full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])

                # Clean the extracted content
                full_text = clean_content(full_text)

                if full_text.strip():  # Ensure content is non-empty
                    return full_text
                else:
                    return "Content found but is empty or minimal."
            else:
                return "Content not found in the specified containers."
        else:
            return f"Failed to retrieve article content. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"An error occurred during the request: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def mynews(request):
    categories = NewsCategory.objects.all()  # Get all categories

    for category in categories:
        keyword = category.name  # Use the category's name as the keyword
        api_url = news_url(keyword, apiKey)
        
        # Add error handling for API requests
        try:
            response = requests.get(api_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from the API: {e}")
            continue  # Skip this category and move to the next one

        if response.status_code == 200:
            data = response.json()

            news_count = 0  # Initialize a counter for the number of news items added

            for article in data.get('articles', []):
                if news_count >= 3:  # Stop after adding 3 news items for this category
                    break

                title = article.get('title', 'No Title')
                description = article.get('description', 'No Description')
                pub_date = article.get('publishedAt', None)
                source_name = article.get('source', {}).get('name', 'Unknown Source')
                author = article.get('author', 'Unknown Author')
                url = article.get('url', '')
                image_url = article.get('urlToImage', '')
                content = article.get('content', '')

                # Try to get the full article content by scraping the URL
                full_content = get_article_content(url)

                # If scraping fails or no content found, fallback to API-provided content
                if not full_content or "Content not found" in full_content:
                    full_content = content if content else "Content not available"

                # Only add the news if it doesn't already exist
                if not News.objects.filter(title=title, url=url).exists():
                    if title != '[Removed]':  # Skip articles with the title '[Removed]'
                        news = News.objects.create(
                            category=category,  # Assign the current category
                            title=title,
                            description=description,
                            pub_date=pub_date,
                            source=source_name,
                            author=author,
                            url=url,
                            image=image_url,
                            content=full_content,
                        )
                        news_count += 1  # Increment the counter when a news item is added
                        print(f'News added: {title}')
                        news.save()

    # Retrieve all news and order by published date
    news = News.objects.all().order_by('-pub_date')
    paginator = Paginator(news, 12)  # Show 12 news items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Get the correct page

    context = {
        'page_obj': page_obj,  # Pass the page object to the template
    }
    return render(request, 'mynews/index.html', context)

def Category(request, category):
    print(f"Requested category: {category}")  

    category_instance = get_object_or_404(NewsCategory, name__iexact=category)

    articles = News.objects.filter(category=category_instance)

    # Prepare context for the template
    context = {
        'category': category_instance,
        'news': articles,
    }

    
    return render(request, 'mynews/category.html', context)

    

def Details(request, id):
    news = News.objects.get(id=id)
    context = {
        'news': news,
    }
    return render(request, 'mynews/details.html', context)



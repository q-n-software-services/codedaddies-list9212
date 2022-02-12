import re

from django.shortcuts import render
import requests
from requests.compat import quote_plus
from . import models
from bs4 import BeautifulSoup
from requests.utils import requote_uri

# Create your views here.
BASE_CRAIGSLIST_URL = 'https://newyork.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    # print(data)
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price')
        else:
            new_response = requests.get(post_url)
            new_data = new_response.text
            new_soup = BeautifulSoup(new_data, features='html.parser')
            post_text = new_soup.find(id='postingbody').text

            r1 = re.findall(r'\$\w+', post_text)
            if r1:
                post_price = r1[0]
            else:
                post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = 'https://images.craigslist.org/{}_300x300.jpg'.format(post_image_id)
        else:
            post_image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLx93wSFSe7rdU-yOMD4OIO17x8KqjWz7yzQ&usqp=CAU'
#
        final_postings.append((post_title, post_url, post_price, post_image_url))




    print(final_url)
    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }
    return render(request, 'my_app/new_search.html', stuff_for_frontend)


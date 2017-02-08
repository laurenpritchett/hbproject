import flickrapi
import json
import os

api_key = os.environ[u'FLICKR_KEY']
api_secret = os.environ[u'FLICKR_SECRET']

flickr = flickrapi.FlickrAPI(api_key, api_secret)


def get_photos_by_location(lat, lon):
    """Get URL for interesting photos with specified latitude and longitude."""
    url_pairs = []

    photos = flickr.photos.search(per_page='10', format='json', lat=lat, lon=lon,
                                  sort='interestingness-desc')

    photo_info = json.loads(photos)

    for info in range(len(photo_info['photos']['photo'])):
        photo_id = photo_info['photos']['photo'][info]['id']
        user_id = photo_info['photos']['photo'][info]['owner']
        photo_source_template = "https://www.flickr.com/photos/{}/{}/"
        photo_source_url = photo_source_template.format(user_id, photo_id)

        farm_id = photo_info['photos']['photo'][info]['farm']
        server_id = photo_info['photos']['photo'][info]['server']
        photo_secret = photo_info['photos']['photo'][info]['secret']

        photo_url_template = "https://farm{}.staticflickr.com/{}/{}_{}.jpg"
        photo_url = photo_url_template.format(farm_id, server_id, photo_id, photo_secret)
        url_pairs.append([photo_source_url, photo_url])
    return url_pairs


laguna_beach_photo_urls = get_photos_by_location(33.5422, -117.7831)
print laguna_beach_photo_urls
import os
import random
import requests
from bs4 import BeautifulSoup
import tweepy
import urllib.parse

# --- FUNGSI UNTUK SCRAPING YAHOO SPORTS ---
def scrape_yahoo_sports():
    """Mengambil 5 artikel teratas dari Yahoo Sports, lalu memilih satu secara acak."""
    url = "https://sports.yahoo.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cari semua artikel yang ada di halaman utama
        all_articles = soup.find_all('li', {'class': 'js-stream-content'})
        
        if not all_articles:
            print("Peringatan: Tidak ada artikel yang ditemukan. Mungkin struktur website berubah.")
            return None, None

        # Ambil 5 artikel teratas dari daftar
        top_5_articles = all_articles[:5]
        print(f"Mengambil 5 artikel teratas, memilih satu secara acak...")

        # Pilih satu artikel secara acak dari 5 teratas
        selected_article = random.choice(top_5_articles)

        # Ambil judul dari tag 'h3' di dalam artikel
        title_element = selected_article.find('h3')
        title = title_element.get_text(strip=True) if title_element else "Judul Tidak Ditemukan"
        
        # Ambil gambar dari tag 'img' di dalam artikel
        image_element = selected_article.find('img')
        image_url = image_element['src'] if image_element and image_element.has_attr('src') else None

        print(f"Artikel yang dipilih: '{title}'")
        print(f"URL Gambar: {image_url}")
        
        return title, image_url

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses Yahoo Sports: {e}")
        return None, None
    except Exception as e:
        print(f"Terjadi error saat scraping: {e}")
        return None, None

# --- FUNGSI UNTUK MENDAPATKAN LINK ---
def get_random_link(filename="links.txt"):
    """Membaca file dan memilih satu link secara acak."""
    try:
        with open(filename, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
        return random.choice(links) if links else None
    except FileNotFoundError:
        print(f"Error: File '{filename}' tidak ditemukan.")
        return None

# --- FUNGSI UNTUK POSTING KE X.COM ---
def post_to_x(text_to_post, image_url=None):
    """Memposting teks dan gambar (opsional) ke X.com."""
    try:
        media_ids = []
        # Inisialisasi API v1.1 untuk upload media
        auth = tweepy.OAuth1UserHandler(
            os.getenv('X_API_KEY'), os.getenv('X_API_SECRET'),
            os.getenv('X_ACCESS_TOKEN'), os.getenv('X_ACCESS_TOKEN_SECRET')
        )
        api = tweepy.API(auth)
        
        if image_url:
            filename = 'temp_image.jpg'
            # Unduh gambar
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as image_file:
                    for chunk in response.iter_content(1024):
                        image_file.write(chunk)
                
                # Upload gambar ke X
                media = api.media_upload(filename=filename)
                media_ids.append(media.media_id_string)
                print("Gambar berhasil di-upload.")
            else:
                print(f"Gagal mengunduh gambar. Status code: {response.status_code}")

        # Inisialisasi Client v2 untuk membuat tweet
        client = tweepy.Client(
            bearer_token=os.getenv('X_BEARER_TOKEN'),
            consumer_key=os.getenv('X_API_KEY'),
            consumer_secret=os.getenv('X_API_SECRET'),
            access_token=os.getenv('X_ACCESS_TOKEN'),
            access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET')
        )
        
        # Buat tweet dengan atau tanpa media
        if media_ids:
            response = client.create_tweet(text=text_to_post, media_ids=media_ids)
        else:
            response = client.create_tweet(text=text_to_post)
            
        print(f"Berhasil memposting tweet ID: {response.data['id']}")
        
    except Exception as e:
        print(f"Error saat memposting ke X.com: {e}")

# --- FUNGSI UTAMA ---
if __name__ == "__main__":
    print("Memulai proses auto-posting...")
    
    # Panggil fungsi scrape Yahoo Sports
    article_title, image_url = scrape_yahoo_sports()
    
    if article_title:
        random_link = get_random_link()
        
        if random_link:
            # Gabungkan judul artikel dan link acak tanpa enter
            final_post_text = f"{article_title} {random_link}"
            
            print("--- POSTINGAN FINAL ---")
            print(f"Teks: {final_post_text}")
            print(f"Gambar: {image_url}")
            print("-----------------------")
            
            # Kirim teks gabungan dan URL gambar ke fungsi posting
            post_to_x(final_post_text, image_url)
    
    print("Proses selesai.")
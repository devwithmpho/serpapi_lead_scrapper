import phonenumbers
from urllib.parse import urlparse, parse_qs, unquote
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SOCIAL_DOMAINS = [
    "www.instagram.com",
    "www.facebook.com",
    "www.tiktok.com",
    "www.wa.me.com"
]

### DATA CLEANING
## Phone Numbers
def clean_number(number):
    try:
        parsed = phonenumbers.parse(str(number), "ZA")

        if phonenumbers.is_valid_number(parsed) and parsed.country_code == 27:
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        else:
            return None
    except Exception:
        return None
    
## Websites
#  unwrap Google redirect
def unwrap_url(url):
    if url.startswith("/url?"):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "q" in qs:
            return unquote(qs["q"][0])
    return url

def get_root_domain(url):
    parsed = urlparse(url)
    if not parsed.netloc:
        return None
    elif parsed.netloc in SOCIAL_DOMAINS:
        return f"{parsed.scheme}://{parsed.netloc}/{parsed.path}"
    else:
        return f"{parsed.scheme}://{parsed.netloc}"
    
def create_session():
    session = requests.Session()

    retry_strategy = Retry(
        total=1,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=100,
        pool_maxsize=100
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session
    
def get_loading_time(url, session):
    try:
        start = time.perf_counter()
        response = session.head(url, timeout=3, allow_redirects=True)

        # fallback to GET if HEAD is blocked
        if response.status_code >= 400:
            response = session.get(url, timeout=5)

        total_time = time.perf_counter() - start
        return total_time

    except requests.RequestException:
        return None

def clean_url(url, session):
    if url != None:
        unwrapped_url = unwrap_url(url)
        root_url = get_root_domain(unwrapped_url)
        load_time = get_loading_time(root_url, session)
        
        if root_url != None and load_time != None and load_time > 2:
            return root_url
        else:
            return None
    else:
        return "No Website"
import phonenumbers
from urllib.parse import urlparse, parse_qs, unquote

BLOCKED_DOMAINS = [
    "facebook.com",
    "fb.me",
    "instagram.com",
    "twitter.com",
    "tiktok.com",
    "linkedin.com",
    "infobel.co.za",
    "yellowpages",
    "cylex",
    "yelp",
    "gumtree",
    "hotfrog",
    "snupit",
    "bizcommunity"
]

### DATA CLEANING
## Phone Numbers
def clean_number(number):
    try:
        parsed = phonenumbers.parse(str(number), "ZA")

        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
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
    return f"{parsed.scheme}://{parsed.netloc}"

def is_official_site(url):
    if not url:
        return False
    return not any(domain in url for domain in BLOCKED_DOMAINS)

def clean_website(url):
    if url != None:
        unwrapped_url = unwrap_url(url)
        root_url = get_root_domain(unwrapped_url)

        if not is_official_site(root_url):
            return None
        
        return root_url
    else:
        return None
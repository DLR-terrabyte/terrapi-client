import os


TERRABYTE_PUBLIC_API_URL = os.environ.get(
    "TERRABYTE_PUBLIC_API_URL",
    "https://stac.terrabyte.lrz.de/public/api"
)
TERRABYTE_PRIVATE_API_URL = os.environ.get(
    "TERRABYTE_PRIVATE_API_URL",
    "https://stac.terrabyte.lrz.de/private/api"
)

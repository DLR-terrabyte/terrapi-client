__version__ = "0.0.1"

from typing import Any, Optional
from urllib.parse import urljoin

import pystac
import pystac_client
import requests

from terrapi.adapter import create_requests_adapter, wrap_request

from terrapi.settings import (
    TERRABYTE_PRIVATE_API_URL,
    TERRABYTE_PUBLIC_API_URL,
)


def open_private_catalog() -> pystac_client.Client:
    return pystac_client.Client.open(
        url=TERRABYTE_PRIVATE_API_URL,
        request_modifier=create_requests_adapter(),
    )


def _send_client_request(client: pystac_client.Client, url: str, *args, **kwargs):
    return wrap_request(client._stac_io.session, url, *args, **kwargs)


def create_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections",
        method="POST",
        json=collection.to_dict(),
    ).raise_for_status()


def update_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections",
        method="PUT",
        json=collection.to_dict(),
    ).raise_for_status()


def delete_private_collection(
    client: pystac_client.Client, collection: pystac.Collection
):
    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection.id}",
        method="DELETE",
    ).raise_for_status()


def create_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")

    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items",
        method="POST",
        json=item.to_dict(),
    ).raise_for_status()


def update_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")

    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items/{item.id}",
        method="PUT",
        json=item.to_dict(),
    ).raise_for_status()


def delete_private_item(
    client: pystac_client.Client, item: pystac.Item, collection_id: Optional[str] = None
):
    collection_id = collection_id or item.collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID for item {item}")

    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items/{item.id}",
        method="DELETE",
    ).raise_for_status()


def open_public_catalog() -> pystac_client.Client:
    return pystac_client.Client.open(
        url=TERRABYTE_PUBLIC_API_URL,
    )

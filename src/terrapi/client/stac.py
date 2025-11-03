from typing import Any, Optional, Union, List, Dict
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

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
    client: pystac_client.Client, collection_id: str
):
    _send_client_request(
        client,
        f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}",
        method="DELETE",
    ).raise_for_status()


def create_private_item(
    client: pystac_client.Client,
    item: Union[pystac.Item, List[pystac.Item]],
    collection_id: Optional[str] = None
):
    if isinstance(item, pystac.Item):
        items = [item]
    else:
        items = item

    collection_id = collection_id or items[0].collection_id
    if not collection_id:
        raise ValueError(f"Could not determine collection ID.")

    if len(items) == 1:
        payload = items[0].to_dict()
    else:
        payload = {
            "type": "FeatureCollection",
            "features": [item.to_dict() for item in items],
        }

    _send_client_request(
        client=client,
        url=f"{TERRABYTE_PRIVATE_API_URL}/collections/{collection_id}/items",
        method="POST",
        json=payload,
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


def login(
    force: bool = False,
    delete: bool = False,
    valid_days: int = 0,
    valid_hours: int = 0,
    valid_till: Optional[datetime] = None,
    valid: bool = False,
    decode: bool = False,
    debug: bool = False
) -> Optional[Dict[str, Any]]:
    """Interactively login via 2FA Browser redirect to obtain refresh Token for the API.
    
    Args:
        force: Force new login, discarding any existing tokens
        delete: Delete existing Refresh Token
        valid_days: Min Nr of days the Token needs to be valid
        valid_hours: Min Nr of hours the Token needs valid
        valid_till: Date the Refresh token needs be valid
        valid: Print how long the current Refresh Token is valid
        decode: Decode and display token contents
        debug: Enable debug output
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing token information:
            - 'validity': datetime of token expiry if valid=True
            - 'token': decoded token payload if decode=True
            - None if delete=True or on error
    """
    from terrapi.auth.config import RefreshTokenStore
    from terrapi.auth.oidc import jwt_decode
    from terrapi.settings import TERRABYTE_CLIENT_ID
    
    result = {}
    token_store = RefreshTokenStore()
    stac_issuer = urlparse(TERRABYTE_PRIVATE_API_URL)._replace(
        path="", query="", fragment=""
    ).geturl()
    
    if debug:
        print(f"Using issuer: {stac_issuer}")
    
    # Handle validity check
    if valid:
        validity = token_store.get_expiry_date_refresh_token(
            stac_issuer, 
            TERRABYTE_CLIENT_ID
        )
        if validity:
            print(f"Refresh Token valid till: {validity.astimezone()}")
            result['validity'] = validity
        else:
            print("No valid Refresh Token on file")
            result['validity'] = None
        if not force:  # Return early only if not forcing new token
            return result
    
    # Handle deletion
    if delete:
        if debug:
            print("Deleting Refresh Token")
        token_store.delete_refresh_token(stac_issuer, TERRABYTE_CLIENT_ID)
        return None
    
    # Calculate validity period
    valid_till_date = datetime.now() + timedelta(hours=valid_hours, days=valid_days)
    if valid_till:
        valid_till_date = max(valid_till, valid_till_date)
    
    if debug:
        print(f"Token needs to be valid until: {valid_till_date}")
    
    # Get tokens using the requests adapter
    auth = create_requests_adapter()
    tokens = auth._get_tokens(force_renew=force, not_expired_before=valid_till_date)
    
    if tokens:
        if decode:
            try:
                header, payload = jwt_decode(tokens.access_token)
                if debug:
                    print("\nToken Header:")
                    print("-" * 12)
                    for key, value in header.items():
                        print(f"{key}: {value}")
                    print("\nToken Payload:")
                    print("-" * 13)
                    for key, value in payload.items():
                        if key in ['exp', 'iat', 'auth_time']:
                            date = datetime.fromtimestamp(value)
                            print(f"{key}: {value} ({date})")
                        else:
                            print(f"{key}: {value}")
                    result['token'] = payload
            except Exception as e:
                print(f"Error decoding token: {str(e)}")
                result['token'] = None
    
    return result if result else None

# copied from https://github.com/Open-EO/openeo-python-client/blob/master/openeo/config.py

import logging
import os
import platform
from configparser import ConfigParser
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterator, List, Optional, Sequence, Union


DEFAULT_APP_NAME = "terrabyte_client"

_log = logging.getLogger(__name__)


def _get_user_dir(
    app_name=DEFAULT_APP_NAME,
    xdg_env_var="XDG_CONFIG_HOME",
    win_env_var="APPDATA",
    fallback="~/.config",
    win_fallback="~\\AppData\\Roaming",
    macos_fallback="~/Library/Preferences",
    auto_create=True,
) -> Path:
    """
    Get platform specific config/data/cache folder
    """
    # Platform specific root locations (from highest priority to lowest)
    env = os.environ
    if platform.system() == "Windows":
        roots = [env.get(win_env_var), win_fallback, fallback]
    elif platform.system() == "Darwin":
        roots = [env.get(xdg_env_var), macos_fallback, fallback]
    else:
        # Assume unix
        roots = [env.get(xdg_env_var), fallback]

    # Filter out None's, expand user prefix and append app name
    dirs = [Path(r).expanduser() / app_name for r in roots if r]
    # Prepend with OPENEO_CONFIG_HOME if set.
    if env.get("OPENEO_CONFIG_HOME"):
        dirs.insert(0, Path(env.get("OPENEO_CONFIG_HOME")))

    # Use highest prio dir that already exists.
    for p in dirs:
        if p.exists() and p.is_dir():
            return p

    # No existing dir: create highest prio one (if possible)
    if auto_create:
        for p in dirs:
            try:
                p.mkdir(parents=True)
                _log.info("Created user dir for {a!r}: {p}".format(a=app_name, p=p))
                return p
            except OSError:
                pass

    raise Exception("Failed to find user dir for {a!r}. Tried: {p!r}".format(a=app_name, p=dirs))


def get_user_config_dir(app_name=DEFAULT_APP_NAME, auto_create=True) -> Path:
    """
    Get platform specific config folder
    """
    return _get_user_dir(
        app_name=app_name,
        xdg_env_var="XDG_CONFIG_HOME",
        win_env_var="APPDATA",
        fallback="~/.config",
        win_fallback="~\\AppData\\Roaming",
        macos_fallback="~/Library/Preferences",
        auto_create=auto_create,
    )


def get_user_data_dir(app_name=DEFAULT_APP_NAME, auto_create=True) -> Path:
    """
    Get platform specific data folder
    """
    return _get_user_dir(
        app_name=app_name,
        xdg_env_var="XDG_DATA_HOME",
        win_env_var="APPDATA",
        fallback="~/.local/share",
        win_fallback="~\\AppData\\Roaming",
        macos_fallback="~/Library",
        auto_create=auto_create,
    )
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
import json

# ======================================3rd Party Library Modules=====================================================||
# (none yet - requests imported lazily in fetch_weather)

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.panes.panes import NchantdPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "weather.yaml")


# T-065: canonical fallback weather payload. Returned when no
# API key is configured or the live call fails. Keeps the
# widget functional even offline.
_FALLBACK_WEATHER = {
    "city": "Unknown",
    "temperature_c": None,
    "humidity": None,
    "description": "Weather data unavailable",
    "icon": None,
    "fetched_at": None,
    "source": "fallback",
}


class NchantdWeatherPane(NchantdPane):
    """T-065: live weather pane.

    Pulls the current weather for ``config.dikt["city"]`` from
    the OpenWeatherMap API when an API key is configured. Falls
    back to a deterministic placeholder so the widget is never
    empty.
    """

    # Default OpenWeatherMap API endpoint + units
    OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    OWM_TIMEOUT = 6  # seconds

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdWeatherPane").override(cfg))
        self.html = self.config.dikt.get("html")
        self.weather = dict(_FALLBACK_WEATHER)

    def initModel(self):
        """Load the live weather data.

        T-065: previously inlined an f-string with literal
        backticks and never actually called the API. Now:
          1. Reads city + API key from the config
          2. Calls self.fetch_weather(city, api_key)
          3. Stores the result on self.weather
          4. Substitutes <[url]> and <[weather]> tokens in
             the configured HTML template
        Returns ``self``.
        """
        super().initModel()
        city = self.config.dikt.get("city")
        api_key = self.config.dikt.get("apiKey")
        self.weather = self.fetch_weather(city, api_key)
        if self.html:
            url = (
                f"{self.OWM_BASE_URL}?q={city}&appid={api_key}&units=metric"
                if city and api_key else "fallback"
            )
            self.html = self.html.replace("<[url]>", url)
            self.html = self.html.replace(
                "<[weather]>",
                json.dumps(self.weather, default=str),
            )
        return self

    def fetch_weather(self, city=None, api_key=None):
        """Fetch the live weather for ``city`` using OpenWeatherMap.

        T-065: a real GET request to the OpenWeatherMap API
        with a short timeout. Returns the parsed JSON on
        success, the fallback payload (``source='fallback'``)
        when ``api_key`` is missing or the request fails.

        Parameters:
            city: City name (default: config.dikt["city"]).
            api_key: OpenWeatherMap API key (default: config.dikt["apiKey"]).

        Returns:
            A dict with ``city``, ``temperature_c``, ``humidity``,
            ``description``, ``icon``, ``fetched_at``, ``source``
            (``"owm"`` or ``"fallback"``).
        """
        try:
            city = city or (self.config.dikt.get("city") if hasattr(self, "config") else None)
            api_key = api_key or (self.config.dikt.get("apiKey") if hasattr(self, "config") else None)
            if not api_key:
                logma.info("[weather] fetch_weather: no API key; using fallback")
                return dict(_FALLBACK_WEATHER, city=city or "Unknown")
            if not city:
                logma.info("[weather] fetch_weather: no city; using fallback")
                return dict(_FALLBACK_WEATHER)
            try:
                import requests  # type: ignore
            except ImportError:
                logma.warning("[weather] requests not installed; using fallback")
                return dict(_FALLBACK_WEATHER, city=city)
            try:
                response = requests.get(
                    self.OWM_BASE_URL,
                    params={"q": city, "appid": api_key, "units": "metric"},
                    timeout=self.OWM_TIMEOUT,
                )
                if response.status_code >= 300:
                    logma.warning(
                        f"[weather] fetch_weather: OWM status {response.status_code}; fallback"
                    )
                    return dict(_FALLBACK_WEATHER, city=city)
                data = response.json()
                main = data.get("main", {})
                weather_list = data.get("weather", [])
                desc = weather_list[0].get("description", "") if weather_list else ""
                icon = weather_list[0].get("icon") if weather_list else None
                return {
                    "city": city,
                    "temperature_c": main.get("temp"),
                    "humidity": main.get("humidity"),
                    "description": desc,
                    "icon": icon,
                    "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
                    "source": "owm",
                }
            except Exception as e:
                logma.error(f"[weather] fetch_weather OWM call failed: {e}", exc_info=True)
                return dict(_FALLBACK_WEATHER, city=city)
        except Exception as e:
            logma.error(f"[weather] fetch_weather outer failed: {e}", exc_info=True)
            return dict(_FALLBACK_WEATHER)

    def initView(self):
        """Render the weather pane view.

        T-065: the view now reads self.weather (set by
        initModel) and includes a temperature + humidity
        readout alongside the existing HTML embed.
        """
        super().initView()
        return self

    def initWidget(self):
        """Wire initModel + initView (T-065)."""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

GITHUB_API_BASE = "https://api.github.com"
PYPI_API_BASE = "https://pypi.org"
PYPISTATS_API_BASE = "https://pypistats.org/api"

FLET_ORG = "flet-dev"
FLET_REPO = "flet"
FLET_PACKAGES_PATH = "sdk/python/packages"

CACHE_TTL_SECONDS = 300  # 5 minutes

PACKAGES_PER_PAGE = 10

SORT_OPTIONS = [
    "default ranking",
    "most stars",
    "most downloads",
    "recently updated",
    "newest package",
    "trending",
]

PACKAGE_TYPES = ["UI Controls", "Services"]

# Packages to EXCLUDE from results (framework core, not extensions)
EXCLUDED_PACKAGES = {
    "flet",
    "flet-cli",
    "flet-desktop",
    "flet-web",
    "flet-runtime",
}

# Official Flet EXTENSION packages from flet-dev/flet monorepo
# These are the actual extensions (not core framework)
OFFICIAL_EXTENSION_PACKAGES = [
    "flet-ads",
    "flet-audio",
    "flet-audio-recorder",
    "flet-camera",
    "flet-charts",
    "flet-code-editor",
    "flet-color-pickers",
    "flet-datatable2",
    "flet-flashlight",
    "flet-geolocator",
    "flet-lottie",
    "flet-map",
    "flet-permission-handler",
    "flet-rive",
    "flet-secure-storage",
    "flet-video",
    "flet-webview",
]

# Classification: Flutter extensions for Flet — Services
# Services = ft.Service — SDKs, background services, platform APIs, no visual widget
KNOWN_SERVICE_EXTENSIONS = {
    "flet-ads",
    "flet-audio",
    "flet-audio-recorder",
    "flet-flashlight",
    "flet-geolocator",
    "flet-permission-handler",
    "flet-secure-storage",
    "flet-onesignal",
}

# Classification: Flutter extensions for Flet — UI Controls
# UI Controls = ft.LayoutControl — widgets that render on screen
KNOWN_UI_CONTROL_EXTENSIONS = {
    "flet-camera",
    "flet-charts",
    "flet-code-editor",
    "flet-color-pickers",
    "flet-datatable2",
    "flet-lottie",
    "flet-map",
    "flet-rive",
    "flet-video",
    "flet-webview",
}

# Known community Flet extension packages (third-party, not in monorepo)
KNOWN_COMMUNITY_EXTENSIONS = {
    "flet-onesignal",
    "fletmint",
    "flet-easy",
    "flet-storyboard",
}

# Known Python packages that are useful with Flet but NOT Flutter extensions
KNOWN_PYTHON_FLET_PACKAGES = [
    "fletmint",
    "flet-easy",
    "flet-storyboard",
]

try:
    VERSION = __import__("pkg_resources").get_distribution("gitboard").version
except Exception:
    VERSION = "unknown"

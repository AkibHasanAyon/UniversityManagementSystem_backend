
JAZZMIN_SETTINGS = {
    "site_title": "University Management System",
    "site_header": "UMS Administration",
    "site_brand": "UMS Admin",
    "welcome_sign": "Welcome to the University Management System",
    "copyright": "Acme University Ltd",
    "search_model": "users.User",
    "user_avatar": None,
    # "topmenu_links": [
    #     {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
    #     {"model": "auth.User"},
    # ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["users", "academic", "university"],
    "icons": {
        "auth": "fas fa-users-cog",
        "users.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

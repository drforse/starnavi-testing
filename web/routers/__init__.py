from . import posts, auth, analytics


routers = [auth.router, posts.router, analytics.router]

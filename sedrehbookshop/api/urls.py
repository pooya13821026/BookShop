from django.urls import path, include

urlpatterns = [
    path('book/', include(('sedrehbookshop.book.urls', 'book'))),
    path('users/', include(('sedrehbookshop.users.urls', 'users'))),
    path('auth/', include(('sedrehbookshop.authentication.urls', 'auth'))),
]

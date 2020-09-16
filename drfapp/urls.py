from django.urls import path

from drfapp import views

urlpatterns = [
    path("books/", views.BookAPIView.as_view()),
    path("books/<str:id>/", views.BookAPIView.as_view()),
    path("booksV2/", views.BookAPIViewV2.as_view()),
    path("booksV2/<str:id>/", views.BookAPIViewV2.as_view()),
]

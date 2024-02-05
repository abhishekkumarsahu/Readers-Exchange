from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('signup',views.signup, name='signup'),
    path('signin',views.signin, name='signin'),
    path('signout',views.signout, name='signout'),
    path('contact',views.contact, name='contact'),
    path('service',views.service, name='service'),
    path('insert_book',views.insert_book, name='insert_book'),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('req_send',views.req_send, name='req_send'),
    path('book_req/<uidb64>/<token>',views.book_req, name='book_req'),

]

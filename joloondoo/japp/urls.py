from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register_page, name='register_page'),
    path('registeruser', views.registerUser, name='registerUser'),
    path('practise', views.practise, name='practise'),
    path('login', views.login_page, name='login_page'),
    path('loginuser', views.loginUser, name='loginUser'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profile_page, name='profile_page'),
    path('getuser', views.getUser, name='getUser'),
    path('updateuser', views.updateUser, name='updateuser'),
    path('createsubject', views.createSubject, name='createsubject'),
    path('updatesubject/<int:subject_id>', views.updateSubject, name='updatesubject'),
    path('getsubject/<int:subject_id>', views.getSubject, name='getsubject'),
    path('createquestion', views.createQuestion, name='createquestion'),
    path('createanswer', views.createAnswer, name='createanswer'),
]
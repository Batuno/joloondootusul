from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #front
    path('register', views.register_page, name='register_page'), #front
    path('registeruser', views.registerUser, name='registerUser'), #back
    path('practise', views.practise, name='practise'), 
    path('login', views.login_page, name='login_page'), #front
    path('loginuser', views.loginUser, name='loginUser'), #back
    path('logout', views.logout, name='logout'), #back
    path('profile', views.profile_page, name='profile_page'), #front
    path('getuser', views.getUser, name='getUser'), #back
    path('updateuser', views.updateUser, name='updateuser'), #back

    # path('subjects', views.getSubject, name='getSubject'), #back
    path('getsubject', views.getSubject, name='getSubject'), #back
    path('createsubject', views.createSubject, name='createsubject'), #back
    path('updatesubject/<int:subject_id>', views.updateSubject, name='updatesubject'), #back

    path('createquestion', views.createQuestion, name='createquestion'), #back
    path('createanswer', views.createAnswer, name='createanswer'), #back
]
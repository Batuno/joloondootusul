from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register_page, name='register_page'),
    path('practise', views.practise, name='practise'),
    path('registeruser', views.registerUser, name='registeruser'),
    path('loginuser', views.loginUser, name='loginUser'),
    path('getuser', views.getUser, name='getuser'),
    path('updateuser', views.updateUser, name='updateuser'),
    path('createsubject', views.createSubject, name='createsubject'),
    path('updatesubject/<int:subject_id>', views.updateSubject, name='updatesubject'),
    path('getsubject/<int:subject_id>', views.getSubject, name='getsubject'),
    path('createquestion', views.createQuestion, name='createquestion'),
    path('createanswer', views.createAnswer, name='createanswer'),
]
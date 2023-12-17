from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #front
    path('register', views.register_page, name='register_page'), #front
    path('registeruser', views.registerUser, name='registerUser'), #back
    path('login', views.login_page, name='login_page'), #front
    path('loginuser', views.loginUser, name='loginUser'), #back
    path('logout', views.logout, name='logout'), #back

    # path('profile', views.profile_page, name='profile_page'), #front
    path('getuser', views.getUser, name='getUser'), #back # front
    path('updateuser', views.updateUser, name='updateuser'), #back
    path('trackuser/<int:user_id>', views.track_user, name='track_user'),

    # path('subjects', views.getSubject, name='getSubject'), #back
    path('getsubject', views.getSubject, name='getSubject'), #back #front
    path('createsubject', views.createSubject, name='createsubject'), #back
    path('updatesubject/<int:subject_id>', views.updateSubject, name='updatesubject'), #back

    path('getquestion', views.getQuestion, name='getQuestion'), #back #front
    path('createquestion', views.createQuestion, name='createquestion'), #back

    path('exam_tip', views.exam_tip, name='exam_tip'), #front
    path('get_exam', views.get_exam, name='get_exam'), #back
    path('submit_exam', views.submit_exam, name='submit_exam'), #back
    path('exam_review/<int:exam_id>/', views.get_exam_review, name='exam_review'), #back

    path('createanswer', views.createAnswer, name='createanswer'), #back
]
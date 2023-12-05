import datetime
import hashlib
import json
import logging
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
import psycopg2
from joloondoo import settings
from joloondoo.settings import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import logout as auth_logout

### ---------------------------------- utils here-----------------------------------------------------
def hashPassword(pass_word):
    password = pass_word
    hashObject = hashlib.sha256(password.encode())
    hashedPassword = hashObject.hexdigest()
    return hashedPassword


### -----------------------------------services here---------------------------------------------------
#registeruser
@api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def registerUser(request):
    con = None
    if request.method == 'POST':
        try:
            data = request.POST
            hashed_password = hashPassword(data['password'])
            created_at = datetime.datetime.now()
            subscription_expiry_date = created_at + datetime.timedelta(days=60)
            con = connect()
            cur = con.cursor()
            cur.execute(
                """INSERT INTO tbl_user 
                (username, email, first_name, last_name, password, phone, subscription_expiry_date, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING user_id""",
                (data['username'], data['email'], data['first_name'], data['last_name'], hashed_password, data['phone'], subscription_expiry_date, created_at)
            )
            user_id = cur.fetchone()[0]
            con.commit()

            return redirect('home') 

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Хэрэглэгчийг бүртгэхэд алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)

        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=500)
#loginuser
@api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def loginUser(request):
    con = None
    if request.method == 'POST':
        try:
            data = request.POST
            username = data.get('username', 'nokey')
            email = data.get('email', 'noemail')
            password = data.get('password', '')
            con = connect()
            cur = con.cursor()
            hashed_password = hashPassword(password)
            cur.execute("""
                        SELECT user_id, username, email, password FROM tbl_user u WHERE username = %s OR email = %s""",
                        [username, email]
                        )
            user_data = cur.fetchone()

            if user_data and hashed_password == user_data[3]:
                print("login suc")
                request.session['user_authenticated'] = True
                response_data = {
                    "user_id": user_data[0],
                    "username": user_data[1],
                    "email": user_data[2],
                    "message": "Амжилттай нэвтэрлээ."
                }
                print(response_data)
                # Redirect to home page
                return redirect('home')
            else:
                response_data = {
                    "message": "Хэрэглэгчийн нэр эсвэл нууц үг буруу байна"
                }
                return JsonResponse(response_data, status=401)

        except Exception as error:
            error_message = str(error)
            response_data = {
                "error": error_message,
                "message": "Амжилтгүй оролдлого."
            }
            return JsonResponse(response_data, status=500)
        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=500)
    
#getuser
@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def getUser(request):
    con = None
    if request.method == 'GET':
        try:
            data = request.GET
            user_id = data.get('user_id', 'nokey')
            con = connect()
            cur = con.cursor()
            cur.execute(f"SELECT * FROM tbl_user WHERE user_id = {user_id};")
            columns = cur.description
            respRow = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cur.fetchall()]
            

            if not respRow:
                response_data = {
                    "message": "Хэрэглэгчийн id тай тохирсон хэрэглэгч олдсонгүй."
                }
                return JsonResponse(response_data, status=404)
            
            response_data = {
                "message": "Амжилттай",
                "respRow": respRow,
            }
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Бүртгэлтэй хэрэглэгч олдсонгүй."
            }
            return JsonResponse(response_data, status=500)

        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=500)

@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def updateUser(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id', 'nokey')
            username = data.get('username', '')
            email = data.get('email', '')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            phone = data.get('phone', '')

            con = connect()
            cur = con.cursor()

            cur.execute(f"SELECT * FROM tbl_user WHERE user_id = {user_id};")
            existing_user = cur.fetchone()

            if not existing_user:
                response_data = {
                    "message": "Хэрэглэгчийн id тай тохирсон хэрэглэгч олдсонгүй.",
                }
                return JsonResponse(response_data, status=404)

            cur.execute(
                """
                UPDATE tbl_user 
                SET username = %s, email = %s, first_name = %s, last_name = %s, phone = %s
                WHERE user_id = %s
                RETURNING user_id;
                """,
                (username, email, first_name, last_name, phone, user_id)
            )

            updated_user_id = cur.fetchone()[0]
            con.commit()

            response_data = {
                "message": "Хэрэглэгчийн мэдээлэл амжилттай шинэчлэгдлээ.",
                "updated_user_id": updated_user_id,
            }
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Хэрэглэгчийн мэдээллийг шинэчлэхэд алдаа гарлаа.",
            }
            return JsonResponse(response_data, status=500)

        finally:
            if con is not None:
                con.close()

    else:
        response_data = {
            "message": "Method Not Allowed",
        }
        return JsonResponse(response_data, status=405)

@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def createSubject(request):
    if request.method == 'POST':
        try:
            s_name = request.POST.get('s_name', '')
            s_text = request.POST.get('s_text', '')
            image_file = request.FILES.get('s_images')

            if s_name and s_text and image_file:
                image_path = os.path.join(settings.MEDIA_ROOT, 'subjects', image_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                con = connect()
                cur = con.cursor()

                cur.execute(
                    """INSERT INTO tbl_subject 
                    (s_name, s_text, s_images) 
                    VALUES (%s, %s, %s) 
                    RETURNING subject_id""",
                    (s_name, s_text, f'subjects/{image_file.name}')
                )
                subject_id = cur.fetchone()[0]
                con.commit()

                response_data = {
                    "message": "Хичээл амжилттай үүслээ.",
                    "subject_id": subject_id
                }
                return JsonResponse(response_data, status=201)
            else:
                response_data = {
                    "message": "Хичээл үүсгэхэд алдаа гарлаа: Зураг, нэр, эх сурвалж хоосон байна."
                }
                return JsonResponse(response_data, status=400)
        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Хичээл үүсгэхэд алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)
        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=405)
        
@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def updateSubject(request, subject_id):
    if request.method == 'PUT':
        try:
            s_name = request.POST.get('s_name', '')
            s_text = request.POST.get('s_text', '')
            image_file = request.FILES.get('s_images')

            con = connect()
            cur = con.cursor()
            cur.execute("SELECT s_images FROM tbl_subject WHERE subject_id = %s", [subject_id])
            existing_image_path = cur.fetchone()[0]

            if s_name and s_text:
                if image_file:
                    image_path = os.path.join(settings.MEDIA_ROOT, 'subjects', image_file.name)
                    with open(image_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    s_images_path = f'subjects/{image_file.name}'
                else:
                    s_images_path = existing_image_path

                cur.execute(
                    """UPDATE tbl_subject 
                    SET s_name = %s, s_text = %s, s_images = %s
                    WHERE subject_id = %s
                    RETURNING subject_id""",
                    (s_name, s_text, s_images_path, subject_id)
                )
                updated_subject_id = cur.fetchone()[0]
                con.commit()

                response_data = {
                    "message": "Хичээл амжилттай шинэчлэгдлээ.",
                    "updated_subject_id": updated_subject_id
                }
                return JsonResponse(response_data, status=200)
            else:
                response_data = {
                    "message": "Хичээл шинэчлэхэд алдаа гарлаа: Нэр, эх сурвалж хоосон байна."
                }
                return JsonResponse(response_data, status=400)
        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Хичээл шинэчлэхэд алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)
        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=405)
    
@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def getSubject(request):
    con = None
    if request.method == 'GET':
        try:
            con = connect()
            cur = con.cursor()
            cur.execute("SELECT * FROM tbl_subject;")
            columns = cur.description
            subjects = [{columns[index][0]: column for index, column in enumerate(value)} for value in cur.fetchall()]

            if not subjects:
                response_data = {
                    "message": "No subjects found.",
                }
                return JsonResponse(response_data, status=404)

            response_data = {
                "message": "Successful",
                "subjects": subjects,
            }
            return render(request, 'subjects_page.html', {'subjects': subjects})
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Error fetching subjects.",
            }
            return JsonResponse(response_data, status=500)

        finally:
            if con is not None:
                con.close()

    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=405)

@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def createQuestion(request):
    if request.method == 'POST':
        try:
            subject_id = request.POST.get('subject_id', '')
            q_text = request.POST.get('q_text', '')
            image_file = request.FILES.get('q_images')

            con = connect()
            cur = con.cursor()
            cur.execute("SELECT * FROM tbl_subject WHERE subject_id = %s", [subject_id])
            subject = cur.fetchone()

            if subject and q_text and image_file:
                image_path = os.path.join(settings.MEDIA_ROOT, 'questions', image_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                cur.execute(
                    """INSERT INTO tbl_question 
                    (subject_id, q_text, q_images) 
                    VALUES (%s, %s, %s) 
                    RETURNING question_id""",
                    (subject_id, q_text, f'subjects/questions/{image_file.name}')
                )
                question_id = cur.fetchone()[0]
                con.commit()

                response_data = {
                    "message": "Асуулт амжилттай үүсгэгдлээ.",
                    "question_id": question_id
                }
                return JsonResponse(response_data, status=201)
            else:
                response_data = {
                    "message": "Асуулт үүсгэхэд алдаа гарлаа: Текст, зураг хоосон байна эсвэл сонгосон сэдэв олдсонгүй."
                }
                return JsonResponse(response_data, status=400)
        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Асуулт үүсгэхэд алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)
        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=405)


@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def createAnswer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id', '')
            a_text = data.get('a_text', '')
            a_iscorrect = data.get('a_iscorrect', False)
            con = connect()
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO tbl_answer (question_id, a_text, a_iscorrect)
                VALUES (%s, %s, %s)
                RETURNING answer_id
                """,
                [question_id, a_text, a_iscorrect]
            )

            answer_id = cur.fetchone()[0]
            con.commit()

            response_data = {
                "message": "Хариулт амжилттай үүсгэгдлээ.",
                "answer_id": answer_id
            }
            return JsonResponse(response_data, status=201)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Хариулт үүсгэхэд алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)

    else:
        response_data = {
            "message": "Method Not Allowed"
        }
        return JsonResponse(response_data, status=405)


def logout(request):
    if request.session.get('user_authenticated', False):
        del request.session['user_authenticated']
    auth_logout(request)

    return HttpResponseRedirect(reverse('home'))



def home(request):
    return render(request, 'home.html', {})




def profile_page(request):
    if not request.session.get('user_authenticated', False):
        return HttpResponseRedirect(reverse('login_page'))
    else:
        try:
            user_data = getUser()
            
            return render(request, 'profile_page.html', {'getUser': user_data})
        except Exception as error:
            return render(request, 'profile_page.html', {'error': str(error)})


def register_page(request):
    return render(request, 'register_page.html', {})

def login_page(request):
    return render(request, 'login_page.html', {})

def practise(request):
    return render(request, 'practise.html', {})

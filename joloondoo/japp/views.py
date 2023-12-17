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
import logging

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
                request.session['user_id'] = user_data[0]
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
            # data = json.loads(request.body)
            user_id = request.session.get('user_id')
            con = connect()
            cur = con.cursor()
            cur.execute(f"SELECT username, email, first_name, last_name, phone FROM tbl_user WHERE user_id = {user_id};")
            columns = cur.description
            user_data = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cur.fetchall()]
            

            if not user_data:
                response_data = {
                    "message": "Хэрэглэгчийн id тай тохирсон хэрэглэгч олдсонгүй."
                }
                return JsonResponse(response_data, status=404)
            
            response_data = {
                "message": "Амжилттай",
                "respRow": user_data,
            }
            return render(request, 'profile_page.html', {'user_data': user_data})
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
            "message": "Хүсэлт буруу байна."
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
            "message": "Хүсэлт буруу байна.",
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
            "message": "Хүсэлт буруу байна."
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
            "message": "Хүсэлт буруу байна."
        }
        return JsonResponse(response_data, status=405)
    
@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def getSubject(request):
    con = None
    if request.method == 'GET':
        try:
            con = connect()
            cur = con.cursor()
            cur.execute("SELECT * FROM tbl_subject ORDER BY subject_id;")
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
            "message": "Хүсэлт буруу байна."
        }
        return JsonResponse(response_data, status=405)

@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def createQuestion(request):
    if request.method == 'POST':
        try:
            qsubject_id = request.POST.get('qsubject_id', '')
            q_text = request.POST.get('q_text', '')
            image_file = request.FILES.get('q_images')

            con = connect()
            cur = con.cursor()
            cur.execute("SELECT * FROM tbl_qsubject WHERE qsubject_id = %s", [qsubject_id])
            subject = cur.fetchone()

            if subject and q_text and image_file:
                image_path = os.path.join(settings.MEDIA_ROOT, 'questions', image_file.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                cur.execute(
                    """INSERT INTO tbl_question 
                    (qsubject_id, q_text, q_images) 
                    VALUES (%s, %s, %s) 
                    RETURNING question_id""",
                    (qsubject_id, q_text, f'subjects/questions/{image_file.name}')
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
            "message": "Хүсэлт буруу байна."
        }
        return JsonResponse(response_data, status=405)

@ api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])   
def getQuestion(request):
    con = None
    if request.method == 'GET':
        try:
            con = connect()
            cur = con.cursor()
            cur.execute("""
                            SELECT q.question_id, q.q_images, q.q_text, s.qs_name, a.a_text, a.a_iscorrect
                            FROM tbl_question q
                            INNER JOIN tbl_qsubject s ON q.qsubject_id = s.qsubject_id
                            LEFT JOIN tbl_answer a ON q.question_id = a.question_id
                            ORDER BY q.question_id, a.a_text;
                        """)

            columns = cur.description
            rows = cur.fetchall()

            subjects = {}
            for row in rows:
                question_id, q_images, q_text, qs_name, a_text, a_iscorrect = row
                if qs_name not in subjects:
                    subjects[qs_name] = []
                if question_id not in [q['question_id'] for q in subjects[qs_name]]:
                    subjects[qs_name].append({
                        'question_id': question_id,
                        'q_images': q_images,
                        'q_text': q_text,
                        'answers': [],
                    })
                if a_text is not None:
                    subjects[qs_name][-1]['answers'].append({
                        'a_text': a_text,
                        'a_iscorrect': a_iscorrect,
                    })

            if not subjects:
                response_data = {
                    "message": "Тохирох id тай асуулт олдсонгүй."
                }
                return JsonResponse(response_data, status=404)

            response_data = {
                "message": "Амжилттай",
                "respRow": list(subjects.values()), 
            }
            return render(request, 'practise.html', {'subjects': subjects})
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Алдаа гарлаа."
            }
            return JsonResponse(response_data, status=500)

        finally:
            if con is not None:
                con.close()
    else:
        response_data = {
            "message": "Хүсэлт буруу байна."
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
            "message": "Хүсэлт буруу байна."
        }
        return JsonResponse(response_data, status=405)


@api_view(["POST", "GET", "PUT", "PATCH", "DELETE"])
def get_exam(request):
    if request.method == 'GET':
        try:
            con = connect()
            cur = con.cursor()
            cur.execute("""
                SELECT q.question_id, q.q_text, q.q_images, a.answer_id, a.a_text, a.a_iscorrect
                FROM (
                    SELECT * FROM tbl_question
                    ORDER BY RANDOM()
                    LIMIT 20
                ) AS q
                LEFT JOIN tbl_answer AS a ON q.question_id = a.question_id

            """)

            rows = cur.fetchall()

            questions = {}
            for row in rows:
                question_id, q_text, q_images, answer_id, a_text, a_iscorrect = row
                if question_id not in [q['question_id'] for q in questions.values()]:
                    questions[question_id] = {
                        'question_id': question_id,
                        'text': q_text,
                        'image': q_images,
                        'answers': [],
                    }
                if a_text is not None:
                    questions[question_id]['answers'].append({
                        'answer_id': answer_id,
                        'text': a_text,
                        'a_iscorrect': a_iscorrect,
                    })


            if not questions:
                response_data = {
                    "message": "No questions found."
                }
                return JsonResponse(response_data, status=404)

            response_data = {
                "message": "Successful",
                "questions": questions,
            }

            return render(request, 'get_exam.html', {'questions': questions.values()})
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Error fetching questions.",
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
def submit_exam(request):
    con = None
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = data.get('score', '')
            time_taken = data.get('time_taken')
            date_taken = datetime.datetime.now()
            user_id = request.session.get('user_id')
            answers = data.get('answers', {})

            if user_id is None:
                response_data = {
                    "error": "User is not logged in.",
                    "message": "Error submitting exam."
                }
                return JsonResponse(response_data, status=400)
            
            con = connect()
            cur = con.cursor()
            print(user_id, date_taken, time_taken, score)
            cur.execute(
                """
                INSERT INTO tbl_examscore (user_id, score, date_taken, time_taken)
                VALUES (%s, %s, %s, %s)
                RETURNING exam_id
                """,
                (user_id, score, date_taken, time_taken)
            )
            exam_id = cur.fetchone()[0]

            for question_id, answer_id in answers.items():
                cur.execute(
                    """
                    INSERT INTO tbl_useranswer (user_id, question_id, exam_id, answer_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, question_id, exam_id, answer_id)
                )

            con.commit()
            

            response_data = {
                "message": "Exam submitted successfully.",
                "exam_score_id": exam_id,
            }
            return JsonResponse(response_data, status=201)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Error submitting exam.",
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
def get_exam_review(request, exam_id):
    con = None
    if request.method == 'GET':
        try:
            user_id = request.session.get('user_id')
            
            if user_id is None:
                response_data = {
                    "error": "User is not logged in.",
                    "message": "Error fetching exam review."
                }
                return JsonResponse(response_data, status=400)

            con = connect()
            cur = con.cursor()
            cur.execute(
                """
                SELECT q.question_id, q.q_images, q_explanation, es.score, a.answer_id, a.a_text, a.a_iscorrect, ua.answer_id AS useranswer_id
                FROM tbl_question q
                INNER JOIN tbl_answer a ON q.question_id = a.question_id
                LEFT JOIN tbl_useranswer ua ON q.question_id = ua.question_id AND ua.exam_id = %s AND ua.user_id = %s
                LEFT JOIN tbl_examscore es ON es.exam_id=ua.exam_id
                WHERE ua.exam_id = %s
                """,
                (exam_id, user_id, exam_id)
            )

            rows = cur.fetchall()
            questions = {}
            for row in rows:
                question_id, q_images, q_explanation, score, answer_id, a_text, a_iscorrect, useranswer_id = row
                if question_id not in questions:
                    questions[question_id] = {
                        'question_id': question_id,
                        'image': q_images,
                        'explanation': q_explanation,
                        'answers': [],
                    }
                questions[question_id]['answers'].append({
                    'answer_id': answer_id,
                    'text': a_text,
                    'correct': a_iscorrect,
                    'user_answer': useranswer_id == answer_id,
                })

            response_data = {
                "message": "Successful",
                "questions": questions,
            }
            return render(request, 'review_exam.html', {'questions': questions, 'score': score})
            return JsonResponse(response_data, status=200)

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Error fetching exam review.",
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
def track_user(request, user_id):
    con = None
    if request.method == 'GET':
        try:
            if user_id is None:
                response_data = {
                    "error": "User is not logged in.",
                    "message": "Error fetching user exam history."
                }
                return JsonResponse(response_data, status=400)

            con = connect()
            cur = con.cursor()
            cur.execute("SELECT * FROM tbl_examscore WHERE user_id = %s", [user_id])
            columns = [col[0] for col in cur.description]
            exam_history = [
                dict(zip(columns, row))
                for row in cur.fetchall()
            ]

            return render(request, 'track_user.html', {'exam_history': exam_history})

        except Exception as error:
            response_data = {
                "error": str(error),
                "message": "Error fetching user exam history.",
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

def logout(request):
    if request.session.get('user_authenticated', False):
        del request.session['user_authenticated']
    auth_logout(request)

    return HttpResponseRedirect(reverse('home'))



def home(request):
    return render(request, 'home.html', {})


def exam_tip(request):
    return render(request, 'exam_tip.html', {})



def register_page(request):
    return render(request, 'register_page.html', {})

def login_page(request):
    return render(request, 'login_page.html', {})

def practise(request):
    return render(request, 'practise.html', {})



# def getQuestion(request):
#     con = None
#     if request.method == 'GET':
#         try:
#             con = connect()
#             cur = con.cursor()
#             cur.execute("""
#                             SELECT q.question_id, q.q_images, q.q_text, s.s_name, a.a_text, a.a_iscorrect
#                             FROM tbl_question q
#                             INNER JOIN tbl_subject s ON q.subject_id = s.subject_id
#                             LEFT JOIN tbl_answer a ON q.question_id = a.question_id;
#                         """)
#             columns = cur.description
#             rows = cur.fetchall()

#             questions = {}
#             for row in rows:
#                 question_id, q_images, q_text, s_name, a_text, a_iscorrect = row
#                 if question_id not in questions:
#                     questions[question_id] = {
#                         'question_id': question_id,
#                         'q_images': q_images,
#                         'q_text': q_text,
#                         's_name': s_name,
#                         'answers': [],
#                     }
#                 if a_text is not None:
#                     questions[question_id]['answers'].append({
#                         'a_text': a_text,
#                         'a_iscorrect': a_iscorrect,
#                     })

#             if not questions:
#                 response_data = {
#                     "message": "Тохирох id тай асуулт олдсонгүй."
#                 }
#                 return JsonResponse(response_data, status=404)

#             response_data = {
#                 "message": "Амжилттай",
#                 "respRow": list(questions.values()), 
#             }
#             return render(request, 'practise.html', {'questions': questions})
#             return JsonResponse(response_data, status=200)

#         except Exception as error:
#             response_data = {
#                 "error": str(error),
#                 "message": "Алдаа гарлаа."
#             }
#             return JsonResponse(response_data, status=500)

#         finally:
#             if con is not None:
#                 con.close()
#     else:
#         response_data = {
#             "message": "Хүсэлт буруу байна."
#         }
#         return JsonResponse(response_data, status=405)
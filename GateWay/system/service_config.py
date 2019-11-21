question_system = {
    "questions_list": "http://127.0.0.1:8001/api/v1/questions/",
    "question": "http://127.0.0.1:8001/api/v1/questions/",
    "add_question": "http://127.0.0.1:8001/api/v1/questions/add/",
    "is_exist": "http://127.0.0.1:8001/api/v1/questions/%s/exist/",
    "attache": "http://127.0.0.1:8001/api/v1/questions/%s/files/%s/",
    "try_delete_file": "http://127.0.0.1:8001/api/v1/files/%s/",
                }

answer_system = {
    "count_answers_question": "http://127.0.0.1:8002/api/v1/answers/counts",
    "answers_for_question": "http://127.0.0.1:8002/api/v1/answers/",
    "add_answer": "http://127.0.0.1:8002/api/v1/answers/add/",
    "is_exist": "http://127.0.0.1:8002/api/v1/answers/%s/exist/",
    "attache": "http://127.0.0.1:8002/api/v1/answers/%s/files/%s/",
    "try_delete_file": "http://127.0.0.1:8002/api/v1/files/%s/",
    "delete_and_return_files": "http://127.0.0.1:8002/api/v1/answers/%s/get_files/",
    'check_belong_answers': "http://127.0.0.1:8002/api/v1/answers/question_belong/%s/"
                }

file_system = {
    "list_of_files": "http://127.0.0.1:8003/api/v1/files/list/",
    "add_file": "http://127.0.0.1:8003/api/v1/files/add/",
    "delete_file": "http://127.0.0.1:8003/api/v1/files/%s/",
    "download": "http://127.0.0.1:8003/api/v1/files/%s/",

              }
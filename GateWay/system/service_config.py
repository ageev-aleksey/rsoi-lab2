import logging
question_system_dst = "127.0.0.1:8001"
answer_systme_dst = "127.0.0.1:8002"
file_system_dst = "127.0.0.1:8003"

logging.info("RUN GateWay. Waiting for required services. question_system: %s; answer_system: %s; file_system: %s",
             question_system_dst, answer_systme_dst, file_system_dst)

question_system = {
    "questions_list": f"http://{question_system_dst}/api/v1/questions/",
    "question": f"http://{question_system_dst}/api/v1/questions/%s",
    "add_question": f"http://{question_system_dst}/api/v1/questions/add/",
    "is_exist": f"http://{question_system_dst}/api/v1/questions/%s/exist/",
    "attache": f"http://{question_system_dst}/api/v1/questions/%s/files/%s/",
    "try_delete_file": f"http://{question_system_dst}/api/v1/files/%s/",
    "delete_and_return_files": f"http://{question_system_dst}/api/v1/questions/%s/get_files/",
                }

answer_system = {
    "count_answers_question": f"http://{answer_systme_dst}/api/v1/answers/counts/",
    "answers_for_question": f"http://{answer_systme_dst}/api/v1/answers/",
    "add_answer": f"http://{answer_systme_dst}/api/v1/answers/add/",
    "is_exist": f"http://{answer_systme_dst}/api/v1/answers/%s/exist/",
    "attache": f"http://{answer_systme_dst}/api/v1/answers/%s/files/%s/",
    "try_delete_file": f"http://{answer_systme_dst}/api/v1/files/%s/",
    "delete_and_return_files": f"http://{answer_systme_dst}/api/v1/answers/%s/get_files/",
    'check_belong_answers': f"http://{answer_systme_dst}/api/v1/answers/question_belong/%s/",
    "get_answers": f"http://{answer_systme_dst}/api/v1/answers/of_question/%s/"
                }

file_system = {
    "list_of_files": f"http://{file_system_dst}/api/v1/files/list/",
    "add_file": f"http://{file_system_dst}/api/v1/files/add/",
    "delete_file": f"http://{file_system_dst}/api/v1/files/%s/",
    "download": f"http://{file_system_dst}/api/v1/files/%s/",

              }
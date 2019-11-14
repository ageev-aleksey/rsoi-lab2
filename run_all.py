import os
from multiprocessing import Process
 
def run_question_service():
	print("Questions")
	os.system("python ./Questions/manage.py runserver 8000")

def run_answers_service():
	print("Answers")
	os.system("python ./Answers/manage.py runserver 8001")

def run_files_service():
	print("FilesSystem")
	os.system("python ./FilesSystem/manage.py runserver 8002")


def run_get_way():
	print("GateWay")
	os.system("python ./GateWay/manage.py runserver 8003")

if __name__ == "__main__":
	proc1 = Process(target=run_question_service)
	proc1.run()

	proc2 = Process(target=run_answers_service)
	proc2.run()

	proc3 = Process(target=run_files_service)
	proc3.run()

	run_get_way()

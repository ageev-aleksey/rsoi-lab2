from system import models
import faker
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create fake data in DataBase by Faker. It is python library for generate random data'
    def add_arguments(self, parser):
        parser.add_argument("--ndata", type=int, default=1000, help="generate questions and answer")
        parser.add_argument("--std_answers", type=int, default=3, help="standard deviations of normal distribution number"
                                                                       " answers for each questions.")
    def handle(self, *args, **options):





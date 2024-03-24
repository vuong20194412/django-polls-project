from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone

import datetime


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    publication_date = models.DateTimeField("date published")

    def __str__(self):
        return f"{self.question_text} {self.publication_date.strftime(f'%d/%m/%Y:%H:%M:%S{self.publication_date.tzinfo}')}"

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.publication_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        if isinstance(self.question, models.Model):
            return f"o{self.question.id} {self.choice_text} {self.vote_count}"
        else:
            return f"i{self.question} {self.choice_text} {self.vote_count}"

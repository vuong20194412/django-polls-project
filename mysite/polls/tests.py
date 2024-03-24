import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.http import SimpleCookie

from .models import Question, Choice


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(publication_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(publication_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(publication_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def get_tz_sub_utc_minutes_cookie():
    minutes = int((datetime.datetime.now().replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now(
        datetime.timezone.utc)).total_seconds() / 60)
    return SimpleCookie({'tz_sub_utc_minutes': str(minutes)})


def create_choice(choice_text, question_id):
    """
    Create a choice with the given `choice_text` and question.
    """
    return Choice.objects.create(question_id=question_id, choice_text=choice_text, vote_count=0)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, publication_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a publication_date in the past are displayed on the
        index page.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Past question.", days=-30)
        create_choice('_', question_id=question.id)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a publication_date in the future aren't displayed on
        the index page.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Future question.", days=30)
        create_choice('_', question_id=question.id)
        response = self.client.get(reverse("polls:index"))

        latest_question_list = response.context["latest_question_list"]

        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(latest_question_list, [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Past question.", days=-30)
        create_choice('_', question_id=question.id)
        question1 = create_question(question_text="Future question.", days=30)
        create_choice('_', question_id=question1.id)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        create_choice('_', question_id=question1.id)
        create_choice('_', question_id=question2.id)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

    def test_question_no_choices(self):
        """
        If questions exist without choices, an appropriate message is displayed.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a publication_date in the future
        returns a 404 not found.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        future_question = create_question(question_text="Future question.", days=5)
        create_choice('_', question_id=future_question.id)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a publication_date in the past
        displays the question's text.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        past_question = create_question(question_text="Past Question.", days=-5)
        create_choice('_', question_id=past_question.id)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_no_choices(self):
        """
        The detail view of a question exist without choices,
        returns a 404 not found.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))

        self.assertEqual(response.status_code, 404)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a publication_date in the future
        returns a 404 not found.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        future_question = create_question(question_text="Future question.", days=5)
        create_choice('_', question_id=future_question.id)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a publication_date in the past
        displays the question's text.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        past_question = create_question(question_text="Past Question.", days=-5)
        create_choice('_', question_id=past_question.id)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_no_choices(self):
        """
        The results view of a question exist without choices,
        returns a 404 not found.
        """
        self.client.cookies = get_tz_sub_utc_minutes_cookie()

        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:results", args=(question.id,)))

        self.assertEqual(response.status_code, 404)

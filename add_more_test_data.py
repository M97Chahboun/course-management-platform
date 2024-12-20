import os

import random
from datetime import timedelta

import django
from django.utils import timezone

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "course_management.settings"
)
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from courses.models import (  # noqa: E402
    Course,
    Enrollment,
    Homework,
    HomeworkState,
    Question,
    Submission,
    Answer,
    QuestionTypes,
    AnswerTypes,
    Project,
    ProjectState,
    ProjectSubmission,
    ReviewCriteria,
    ReviewCriteriaTypes,
    PeerReview,
    PeerReviewState,
    CriteriaResponse,
    QUESTION_ANSWER_DELIMITER,
)

from courses.projects import (  # noqa: E402
    assign_peer_reviews_for_project,
    score_project,
)


User = get_user_model()

course = Course.objects.get(slug="fake-course")


def create_random_question(homework: Homework):
    question_type = random.choice(
        [QuestionTypes.FREE_FORM, QuestionTypes.MULTIPLE_CHOICE]
    )
    print(
        f"Creating question of type {question_type} for homework {homework}"
    )
    question_id = random.randint(1, 1000)

    if question_type == QuestionTypes.MULTIPLE_CHOICE:
        answers = ["1", "2", "3", "4"]
        correct_answer = random.choice(answers)
        print(
            f"  Correct answer is {correct_answer}, possible answers are {answers}"
        )

        return Question.objects.create(
            homework=homework,
            text=f"Question text {question_id}",
            correct_answer=correct_answer,
            question_type=QuestionTypes.MULTIPLE_CHOICE.value,
            possible_answers=QUESTION_ANSWER_DELIMITER.join(answers),
            scores_for_correct_answer=1,
        )

    elif question_type == QuestionTypes.FREE_FORM:
        correct_answer = "Example answer"
        print(f"  Correct answer is {correct_answer}")

        return Question.objects.create(
            homework=homework,
            text=f"Question text {question_id}",
            correct_answer=correct_answer,
            question_type=QuestionTypes.FREE_FORM.value,
            answer_type=AnswerTypes.EXACT_STRING.value,
            scores_for_correct_answer=1,
        )


# Function to create questions for a given homework
def create_questions_for_homework(homework: Homework):
    num_questions = random.randint(3, 6)

    for i in range(num_questions):
        create_random_question(homework)


def generate_answer(
    question: Question, submission: Submission
) -> Answer:
    is_correct = random.choice([True, False])

    student_answer = ""

    if is_correct:
        student_answer = question.correct_answer
    else:
        if (
            question.question_type
            == QuestionTypes.MULTIPLE_CHOICE.value
        ):
            num_possible_answers = len(question.get_possible_answers())
            student_answer_int = random.choice(
                range(1, num_possible_answers + 1)
            )
            student_answer = str(student_answer_int)
        elif question.question_type == QuestionTypes.FREE_FORM.value:
            student_answer = "Incorrect answer"

    print(
        f"  Answer is correct: {is_correct}, student answer: {student_answer}"
    )

    return Answer.objects.create(
        submission=submission,
        question=question,
        answer_text=student_answer,
    )


def create_answers_for_student(submission):
    for question in submission.homework.question_set.all():
        generate_answer(question, submission)


for hw in range(1, 6):
    print(f"Creating homework {hw}")
    homework, created = Homework.objects.get_or_create(
        course=course,
        slug=f"extra-homework-{hw}",
        title=f"Test Homework {hw}",
        due_date=timezone.now() - timedelta(days=hw),
        description=f"Description for homework {hw}",
        state=HomeworkState.OPEN.value,
    )

    if created:
        create_questions_for_homework(homework)


# Create 20 users and their submissions
for u in range(1, 21):
    username = f"student{u}"
    print(f"Creating student {username} and their submissions")

    user, _ = User.objects.get_or_create(username=username)


all_users = list(User.objects.all())
homeworks = list(Homework.objects.filter(course=course))

for user in all_users:
    enrollment, created = Enrollment.objects.get_or_create(
        course=course,
        student=user,
    )

    for homework in homeworks:
        submission, created = Submission.objects.get_or_create(
            homework=homework,
            student=user,
            defaults={"enrollment": enrollment},
            time_spent_lectures=random.randint(0, 10),
            time_spent_homework=random.randint(0, 10),
        )

        if created:
            create_answers_for_student(submission)


for i in [1, 2, 3]:
    project, created = Project.objects.get_or_create(
        course=course,
        slug=f"project-{i}",
        title=f"Test Project {i}",
        submission_due_date=timezone.now() - timedelta(days=i),
        peer_review_due_date=timezone.now() + timedelta(days=i),
        state=ProjectState.COLLECTING_SUBMISSIONS.value,
    )

    print(f"Created project {project} and now creating submissions")

    if not created:
        continue

    for user in all_users:
        print(f"  Creating submission for {user}")

        enrollment = Enrollment.objects.get(
            course=course,
            student=user,
        )
        ProjectSubmission.objects.create(
            project=project,
            student=user,
            enrollment=enrollment,
            github_link=f"https://github.com/{user.username}/project-{i}",
            commit_id=f"commit-{i}",
        )


p1 = Project.objects.get(
    course=course,
    slug=f"project-1",
)

p2 = Project.objects.get(
    course=course,
    slug=f"project-2",
)

criteria = ReviewCriteria.objects.filter(course=course)
enrollments = Enrollment.objects.filter(course=course)

for p in [p1, p2]:
    assign_peer_reviews_for_project(p)

    submissions = ProjectSubmission.objects.filter(
        enrollment__in=enrollments, project=p
    )
    reviews = PeerReview.objects.filter(reviewer__in=submissions)

    for r in reviews:
        if random.uniform(0, 1) < 0.2:
            print(f"Skipping review {r.id}")
            continue

        for c in criteria:
            options = c.options

            if (
                c.review_criteria_type
                == ReviewCriteriaTypes.RADIO_BUTTONS.value
            ):
                i = random.randint(0, len(options) - 1)
                answer = str(i + 1)
            if (
                c.review_criteria_type
                == ReviewCriteriaTypes.CHECKBOXES.value
            ):
                answers = []
                for i in range(len(options)):
                    if random.uniform(0, 1) < 0.3:
                        answers.append(str(i + 1))
                answer = ",".join(answers)

            CriteriaResponse.objects.create(
                review=r,
                criteria=c,
                answer=answer,
            )

        print(f"Submitted review {r.id}")
        r.state = PeerReviewState.SUBMITTED.value
        r.save()


p1.peer_review_due_date = timezone.now()
score_project(p1)

from django.db import models
from config.settings import HABIT_FREQUENCY
from users.models import User


class Week(models.Model):
    day = models.CharField(max_length=3, verbose_name="день недели")


class Habit(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="habits",
        null=True,
        blank=True,
    )
    place = models.CharField(
        max_length=200,
        verbose_name="Место",
        help_text="Введите место, где вы будете выполнять.",
    )
    time = models.DateTimeField(
        verbose_name="Время",
        help_text=("Введите время, когда нужно выполнять привычку. Если "
                   "привычка выполняется несколько раз в день, нужно также "
                   "указать время окончания."),
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=200,
        verbose_name="Действие",
        help_text="Введите действие, которое нужно выполнить.",
    )
    is_pleasant = models.BooleanField(
        verbose_name="Полезня или нет",
        help_text=("Выберите, является ли привычка приятной. Только приятные "
                   "привычки могут служить вознаграждением для полезных "
                   "привычек."),
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="Связанная привычка",
        help_text="Выберите связанную приятную привычку (в качестве вознаграждения). Только для полезных привычек!",
        blank=True,
        null=True,
    )
    frequency = models.CharField(
        choices=HABIT_FREQUENCY,
        verbose_name="Частота выполнения ",
        help_text=("Выберите, как часто нужно выполнять полезную привычку. "
                   "ВНИМАНИЕ! Полезная привычка должна выполняться как минимум "
                   "раз в неделю. Только для полезных привычек!"),
        default="m h * * *",
        blank=True,
        null=True,
    )
    reward = models.CharField(
        max_length=200,
        verbose_name="Вознаграждение",
        help_text="Введите вознаграждение за выполнение привычки.",
        blank=True,
        null=True,
    )
    end_time = models.DateTimeField(
        verbose_name="Время окончания",
        help_text=("Введите время, когда нужно в последний раз за день "
                   "выполнить привычку. Только для полезных привычек, которые "
                   "выполняются несколько раз в день!"),
        null=True,
        blank=True,
    )
    days_of_week = models.ManyToManyField(
        Week,
        verbose_name="Дни недели",
        help_text="Выберите конкретные дни, когда нужно выполнять полезную привычку.",
        blank=True,
    )
    time_needed = models.PositiveIntegerField(
        verbose_name="требуемое время",
        help_text="Введите время, необходимое для выполнения привычки, в секундах = 120 секунд.",
        default=120,
    )
    is_public = models.BooleanField(
        verbose_name="Статус публикации",
        help_text="Является ли привычка публичной или приватной?",
    )

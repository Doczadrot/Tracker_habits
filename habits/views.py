from django_celery_beat.models import PeriodicTask
from rest_framework import generics
from rest_framework.permissions import AllowAny

from habits.models import Habit
from habits.paginators import HabitPagination
from habits.serializers import HabitSerializer, PublicHabitSerializer
from habits.services import create_replacements, create_schedule, create_task, make_replacements
from users.permissions import IsUser


class HabitMixin:
    """Миксин для общей логики работы с привычками."""

    def _setup_habit_schedule(self, habit, update=False):
        """Настраивает расписание для привычки."""
        if not habit.is_pleasant:
            replacements = create_replacements(habit)
            habit.frequency = make_replacements(habit.frequency, replacements)
            habit.save()

            if habit.user.tg_chat_id:
                # Удаляем старую задачу при обновлении
                if update:
                    try:
                        task = PeriodicTask.objects.get(name=f"Отправка напоминания {habit.pk}")
                        task.enabled = False
                        task.delete()
                    except PeriodicTask.DoesNotExist:
                        pass

                schedule = create_schedule(habit.frequency)
                create_task(schedule, habit)


class HabitCreateAPIView(HabitMixin, generics.CreateAPIView):
    serializer_class = HabitSerializer

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        self._setup_habit_schedule(habit)


class PublicHabitListAPIView(generics.ListAPIView):
    serializer_class = PublicHabitSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (IsUser,)


class HabitUpdateAPIView(HabitMixin, generics.UpdateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (IsUser,)

    def perform_update(self, serializer):
        habit = serializer.save(user=self.request.user)
        self._setup_habit_schedule(habit, update=True)


class HabitDestroyAPIView(generics.DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = (IsUser,)
    serializer_class = HabitSerializer

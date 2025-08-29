from datetime import datetime

from rest_framework import serializers

from habits.models import Habit


class HabitValidator:
    def validate_time_needed(self, attrs):

        if attrs["time_needed"] > 120:
            raise serializers.ValidationError("Время на выполнение должно быть меньше 2 минут (120 секунд).")

    def validate_related_habit(self, attrs):

        if attrs.get("related_habit_id"):
            related_habit = Habit.objects.get(pk=attrs.get("related_habit_id"))
            if not related_habit.is_pleasant:
                raise serializers.ValidationError("В качестве связанной привычки можно выбрать только приятную.")

    def validate_reward(self, attrs):

        if attrs.get("related_habit_id") and attrs.get("reward"):
            raise serializers.ValidationError(
                "Нельзя выбрать одновременно связанную привычку и награду. Выберите что-то одно."
            )

    def validate_pleasant_habit(self, attrs):

        if attrs.get("is_pleasant") and any(
            [attrs.get("related_habit_id"), attrs.get("reward"), attrs.get("frequency"), attrs.get("time")]
        ):
            raise serializers.ValidationError(
                "Приятная привычка уже является вознаграждением, у неё не может быть связанной "
                "привычки или награды, и она не должна быть регулярной."
            )
        if not attrs.get("is_pleasant") and not any(
            [
                all([attrs.get("reward"), attrs.get("frequency"), attrs.get("time")]),
                all([attrs.get("related_habit_id"), attrs.get("frequency"), attrs.get("time")]),
            ]
        ):
            raise serializers.ValidationError(
                "Полезная привычка должна иметь награду или связанную привычку, а также выполняться "
                "регулярно и в определённое время."
            )

    def validate_end_time(self, attrs):

        if attrs.get("frequency") and "x" in attrs.get("frequency") and not attrs.get("end_time"):
            raise serializers.ValidationError(
                "Для привычки, которая выполняется несколько раз в день, должно быть указано время окончания."
            )
        if attrs.get("frequency") and "x" not in attrs.get("frequency") and attrs.get("end_time"):
            raise serializers.ValidationError(
                "Время окончания должно быть указано только для привычек, выполняемых несколько раз в день."
            )
        if (
            attrs.get("end_time")
            and attrs.get("time")
            and datetime.fromisoformat(attrs.get("end_time")).date()
            != datetime.fromisoformat(attrs.get("time")).date()
        ):
            raise serializers.ValidationError("Время начала и окончания должно быть в пределах одного дня.")
        if attrs.get("end_time") and attrs.get("time") and attrs.get("end_time") <= attrs.get("time"):
            raise serializers.ValidationError("Время окончания не может быть раньше или равно времени начала.")

    def validate_days_of_week(self, attrs):

        if attrs.get("frequency") and "d" in attrs.get("frequency") and not attrs.get("days_of_week"):
            raise serializers.ValidationError(
                "Для привычки, которая должна выполняться в определённые дни недели, эти дни должны быть выбраны."
            )
        if attrs.get("frequency") and "d" not in attrs.get("frequency") and attrs.get("days_of_week"):
            raise serializers.ValidationError(
                "Конкретные дни недели должны быть выбраны только для привычек, выполняемых в выбранные дни."
            )

    def __call__(self, attrs):
        self.validate_time_needed(attrs)
        self.validate_related_habit(attrs)
        self.validate_reward(attrs)
        self.validate_pleasant_habit(attrs)
        self.validate_end_time(attrs)
        self.validate_days_of_week(attrs)
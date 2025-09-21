# Generated manually to rename author field to user

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        # Rename the column in the database
        migrations.RunSQL(
            "ALTER TABLE habits_habit RENAME COLUMN author_id TO user_id;",
            reverse_sql="ALTER TABLE habits_habit RENAME COLUMN user_id TO author_id;"
        ),
        # Rename the field
        migrations.RenameField(
            model_name='habit',
            old_name='author',
            new_name='user',
        ),
    ]

# Generated by Django 4.2.7 on 2024-06-21 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model_provider_mgmt', '0001_initial'),
        ('bot_mgmt', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botskillrule',
            name='prompt',
        ),
        migrations.RemoveField(
            model_name='botskillrule',
            name='skill',
        ),
        migrations.AddField(
            model_name='botskillrule',
            name='llm_skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='model_provider_mgmt.llmskill', verbose_name='LLM技能'),
        ),
        migrations.AddField(
            model_name='botskillrule',
            name='overwrite_skill_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='覆盖技能ID'),
        ),
    ]

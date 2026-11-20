# Generated for the advanced free-tier feature set.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_generatedreport_userpdfdocument'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='karmapledge',
            constraint=models.UniqueConstraint(
                fields=('user', 'bottle'),
                name='unique_pledge_per_user_bottle',
            ),
        ),
        migrations.CreateModel(
            name='PledgeVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval', models.BooleanField()),
                ('comments', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('pledge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='core.karmapledge')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pledge_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(
                        fields=('pledge', 'voter'),
                        name='unique_vote_per_pledge_voter',
                    )
                ],
            },
        ),
    ]

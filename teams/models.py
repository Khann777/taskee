from django.db import models
from account.models import CustomUser

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField('TeamMember', related_name='teams')
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leader')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - leader: {self.leader.username}'

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('team', 'user')

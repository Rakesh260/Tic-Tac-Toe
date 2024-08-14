from django.db import models

from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        db_table = 'player'
        managed = True

class Game(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    board = models.CharField(max_length=9, default=" " * 9)
    is_player_turn = models.BooleanField(default=True)
    status = models.CharField(max_length=10,
                              choices=[('ongoing', 'Ongoing'), ('win', 'Win'), ('lose', 'Lose'), ('draw', 'Draw')])

    class Meta:
        db_table = 'game'
        managed = True


class Leaderboard(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)

    class Meta:
        db_table = 'leader_board'
        managed = True

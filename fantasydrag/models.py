from django.contrib.auth.models import User
from django.db import models


class Queen(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class DragRace(models.Model):
	season = models.IntegerField()
	race_type = models.CharField(
		max_length=25,
		choices=[
			('standard', 'standard'),
			('all star', 'all star')
		]
	)
	queens = models.ManyToManyField(Queen)

	def __str__(self):
		return 'Season {} {}'.format(self.race_type, self.season)


class Episode(models.Model):
	drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
	number = models.IntegerField()

	def __str__(self):
		return '{} episode #{}'.format(self.drag_race, self.number)


class Rule(models.Model):
	drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
	name = models.CharField(max_length=250)
	description = models.TextField()
	point_value = models.IntegerField(default=1)

	def __str__(self):
		return '{}, "{}": ({} points) {}'.format(self.drag_race, self.name, self.point_value, self.description)


class Score(models.Model):
	episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
	queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
	rule = models.ForeignKey(Rule, on_delete=models.CASCADE)

	def __str__(self):
		return '{}: {} // {}'.format(self.queen, self.episode, self.rule)


class Participant(models.Model):
	name = models.CharField(max_length=100)
	user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return self.name


class Panel(models.Model):
	name = models.CharField(max_length=250, unique=True)
	participants = models.ManyToManyField(Participant)
	drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class Draft(models.Model):
	participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
	queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
	panel = models.ForeignKey(Panel, on_delete=models.CASCADE)

	def __str__(self):
		return '{}, {}::{}'.format(self.panel, self.participant, self.queen)

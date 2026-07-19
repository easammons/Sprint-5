from django.db import models

# Create your models here.

EF_CHOICES = [
    ("EF0", "EF0"),
    ("EF1", "EF1"),
    ("EF2", "EF2"),
    ("EF3", "EF3"),
    ("EF4", "EF4"),
    ("EF5", "EF5"),
]

class Tornado(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    ef_rating = models.CharField(max_length=3, choices=EF_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    plot_image = models.CharField(max_length=255)  # e.g. "weather/tornadoes/jarrell.png"

    def __str__(self):
        return f"{self.name} ({self.ef_rating}, {self.date})"

    class Meta:
        ordering = ["-date"]
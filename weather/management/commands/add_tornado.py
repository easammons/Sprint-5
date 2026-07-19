# import pandas as pd
# from django.core.management.base import BaseCommand
# from weather.models import Tornado
# from weather.plotting import generate_tornado_plot


# class Command(BaseCommand):
#     help = "Add a tornado: fetch NOAA data, generate its plot, and save to DB"

#     def handle(self, *args, **options):
#         # Edit these values per tornado, then run:
#         # python manage.py add_tornado
#         name = "Jarrell Tornado"
#         ef_rating = "EF5"
#         date = "1997-05-27"
#         location = "Jarrell, TX"

#         stations = {
#             "KGRK": "72257603902",
#             "KAUS": "72254513904",
#             "KACT": "72256013959",
#         }

#         tornado_start = pd.Timestamp("1997-05-27 15:40")
#         tornado_end = pd.Timestamp("1997-05-27 15:53")
#         start_time = pd.Timestamp("1997-05-27 09:00")
#         end_time = pd.Timestamp("1997-05-27 21:00")

#         image_path = generate_tornado_plot(
#             name=name,
#             stations=stations,
#             start_time=start_time,
#             end_time=end_time,
#             tornado_start=tornado_start,
#             tornado_end=tornado_end,
#             output_filename="jarrell.png",
#             year=1997,
#         )

#         tornado, created = Tornado.objects.update_or_create(
#             name=name,
#             defaults=dict(
#                 date=date,
#                 ef_rating=ef_rating,
#                 location=location,
#                 start_time=tornado_start,
#                 end_time=tornado_end,
#                 plot_image=image_path,
#             ),
#         )

#         self.stdout.write(self.style.SUCCESS(f"Saved: {tornado}"))

import json
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from weather.models import Tornado
from weather.plotting import generate_tornado_plot


class Command(BaseCommand):
    help = "Add a tornado: fetch NOAA data, generate its plot, and save to DB"

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Tornado name, e.g. 'Moore Tornado'")
        parser.add_argument("--ef", required=True, choices=["EF0", "EF1", "EF2", "EF3", "EF4", "EF5"])
        parser.add_argument("--date", required=True, help="YYYY-MM-DD, the tornado's date")
        parser.add_argument("--location", default="", help="e.g. 'Moore, OK'")
        parser.add_argument(
            "--stations", required=True,
            help='JSON dict of station name -> NOAA station ID, e.g. \'{"KOUN": "72357003954"}\''
        )
        parser.add_argument("--tornado-start", required=True, help="YYYY-MM-DD HH:MM")
        parser.add_argument("--tornado-end", required=True, help="YYYY-MM-DD HH:MM")
        parser.add_argument("--window-start", required=True, help="YYYY-MM-DD HH:MM (data window start)")
        parser.add_argument("--window-end", required=True, help="YYYY-MM-DD HH:MM (data window end)")
        parser.add_argument("--filename", required=True, help="Output PNG filename, e.g. 'moore.png'")

    def handle(self, *args, **options):
        try:
            stations = json.loads(options["stations"])
        except json.JSONDecodeError:
            raise CommandError("--stations must be valid JSON, e.g. '{\"KOUN\": \"72357003954\"}'")

        tornado_start = pd.Timestamp(options["tornado_start"])
        tornado_end = pd.Timestamp(options["tornado_end"])
        window_start = pd.Timestamp(options["window_start"])
        window_end = pd.Timestamp(options["window_end"])
        year = tornado_start.year

        self.stdout.write(f"Fetching NOAA data for {options['name']}...")

        image_path = generate_tornado_plot(
            name=options["name"],
            stations=stations,
            start_time=window_start,
            end_time=window_end,
            tornado_start=tornado_start,
            tornado_end=tornado_end,
            output_filename=options["filename"],
            year=year,
        )

        tornado, created = Tornado.objects.update_or_create(
            name=options["name"],
            defaults=dict(
                date=options["date"],
                ef_rating=options["ef"],
                location=options["location"],
                start_time=timezone.make_aware(tornado_start.to_pydatetime()),
                end_time=timezone.make_aware(tornado_end.to_pydatetime()),
                plot_image=image_path,
            ),
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action}: {tornado}"))
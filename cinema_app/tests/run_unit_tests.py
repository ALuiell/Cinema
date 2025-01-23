import os
import django

# Установите DJANGO_SETTINGS_MODULE перед любыми Django-импортами
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings")
django.setup()

import unittest
from cinema_app.tests.unit import models_genre
from cinema_app.tests.unit import models_ticket
from cinema_app.tests.unit import models_hall
from cinema_app.tests.unit import models_session
from cinema_app.tests.unit import models_movie

def suite():
    # Define a test suite and add all test cases
    suite = unittest.TestSuite()

    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_hall.HallModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_genre.GenreModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_movie.MovieModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_session.SessionModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_ticket.TicketModelTestCase))

    return suite


if __name__ == "__main__":
    # Run tests using TextTestRunner
    runner = unittest.TextTestRunner(verbosity=2)  # verbosity=2 for detailed output
    runner.run(suite())

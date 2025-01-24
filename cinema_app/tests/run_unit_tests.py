import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema.settings")
django.setup()

import unittest
from cinema_app.tests.unit import models_genre
from cinema_app.tests.unit import models_ticket
from cinema_app.tests.unit import models_hall
from cinema_app.tests.unit import models_session
from cinema_app.tests.unit import models_movie
from cinema_app.tests.unit import models_order

def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_hall.HallModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_genre.GenreModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_movie.MovieModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_session.SessionModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_ticket.TicketModelTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(models_order.OrderModelTestCase))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())

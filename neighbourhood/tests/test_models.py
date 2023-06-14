from django.test import TestCase

from neighbourhood.models import Team


class TeamTest(TestCase):
    fixtures = ["teams.json"]

    def test_group_count(self):
        self.assertEqual(4, Team.objects.count())
        self.assertEqual(3, Team.objects.filter(confirmed=True).count())

    def test_find_nearest(self):
        nearest = Team.find_nearest_teams(
            latitude=55.95280796489685, longitude=-3.200368880780104
        )

        self.assertEqual(3, nearest.count())

        teams = list(nearest.values_list("name", flat=True))
        self.assertEqual(
            teams, ["edinburgh castle", "scottish parliament", "Holyrood palace"]
        )

    def test_limit_nearest_by_distance(self):
        nearest = Team.find_nearest_teams(
            latitude=55.95270795489685, longitude=-3.171959, distance=1
        )

        self.assertEqual(2, nearest.count())

        teams = list(nearest.values_list("name", flat=True))
        self.assertEqual(teams, ["Holyrood palace", "scottish parliament"])

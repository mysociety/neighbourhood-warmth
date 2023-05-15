from django.test import TestCase
from neighbourhood.models import Team


class TeamTest(TestCase):
    fixtures = ["groups.json"]

    def test_group_count(self):
        self.assertEqual(3, Team.objects.count())

    def test_find_nearest(self):
        nearest = Team.find_nearest_groups(
            latitude=55.95280796489685, longitude=-3.200368880780104
        )

        self.assertEqual(3, nearest.count())

        groups = list(nearest.values_list("name", flat=True))
        self.assertEqual(
            groups, ["edinburgh castle", "scottish parliament", "Holyrood palace"]
        )

    def test_limit_nearest_by_distance(self):
        nearest = Team.find_nearest_groups(
            latitude=55.95270795489685, longitude=-3.171959, distance=1
        )

        self.assertEqual(2, nearest.count())

        groups = list(nearest.values_list("name", flat=True))
        self.assertEqual(groups, ["Holyrood palace", "scottish parliament"])

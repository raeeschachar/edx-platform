"""
Test the partitions and partitions service

"""

from unittest import TestCase
from mock import Mock, MagicMock

from xmodule.partitions.partitions import Group, UserPartition
from xmodule.partitions.partitions_service import PartitionService


class TestGroup(TestCase):
    def test_construct(self):
        test_id = "an_id"
        name = "Grendel"
        g = Group(test_id, name)
        self.assertEqual(g.id, test_id)
        self.assertEqual(g.name, name)

    def test_to_json(self):
        test_id = "an_id"
        name = "Grendel"
        g = Group(test_id, name)
        jsonified = g.to_json()
        self.assertEqual(jsonified, {"id": test_id,
                                     "name": name,
                                     "version": g.VERSION})

    def test_from_json(self):
        test_id = "an_id"
        name = "Grendel"
        jsonified = {"id": test_id,
                     "name": name,
                     "version": Group.VERSION}
        g = Group.from_json(jsonified)
        self.assertEqual(g.id, test_id)
        self.assertEqual(g.name, name)


class StaticPartitionService(PartitionService):
    def __init__(self, partitions, **kwargs):
        super(StaticPartitionService, self).__init__(**kwargs)
        self._partitions = partitions

    @property
    def course_partitions(self):
        return self._partitions


class TestPartitionsService(TestCase):
    """
    Test getting a user's group out of a partition

    """

    def setUp(self):
        groups = [Group(0, 'Group 1'), Group(1, 'Group 2')]
        self.partition_id = 0

        # construct the user_service
        self.user_tags = dict()
        user_tags_service = MagicMock()

        def mock_set_tag(_scope, key, value):
            self.user_tags[key] = value

        def mock_get_tag(_scope, key):
            if key in self.user_tags:
                return self.user_tags[key]
            return None

        user_tags_service.set_tag = mock_set_tag
        user_tags_service.get_tag = mock_get_tag

        user_partition = UserPartition(self.partition_id, 'Test Partition', 'for testing purposes', groups)
        self.partitions_service = StaticPartitionService(
            [user_partition],
            user_tags_service=user_tags_service,
            course_id=Mock(),
            track_function=Mock()
        )


    def test_get_user_group_for_partition(self):
        # get a group assigned to the user
        group1 = self.partitions_service.get_user_group_for_partition(self.partition_id)

        # make sure we get the same group back out if we try a second time
        group2 = self.partitions_service.get_user_group_for_partition(self.partition_id)

        self.assertEqual(group1, group2)

        # test that we error if given an invalid partition id
        with self.assertRaises(ValueError):
            self.partitions_service.get_user_group_for_partition(3)

from tests.zcx_test_case import ZCXTestCase


class TestSessionRing(ZCXTestCase):

    def setUp(self):
        self._session_ring.go_to_track(0)
        self._session_ring.go_to_scene(0)
        self.tracklist = list(self.song.tracks)

    def test_ring_tracks(self):
        for i in range(8):
            self.assertEqual(self.tracklist[i], self._session_ring.get_ring_track(i))

        self._session_ring.move(x=8)

        for i in range(8):
            self.assertEqual(self.tracklist[i + 8], self._session_ring.get_ring_track(i))

    def test_directional_moves(self):
        self.assertEqual(self._session_ring.track_offset, 0)
        self.assertEqual(self._session_ring.scene_offset, 0)
        self._session_ring.move(x=1)
        self.assertEqual(self._session_ring.track_offset, 1)
        self._session_ring.move(y=1)
        self.assertEqual(self._session_ring.scene_offset, 1)
        self._session_ring.move(x=-1)
        self.assertEqual(self._session_ring.track_offset, 0)
        self._session_ring.move(y=-1)
        self.assertEqual(self._session_ring.scene_offset, 0)

    def test_absolute_moves(self):
        self._session_ring.go_to_track(10)
        self.assertEqual(self._session_ring.track_offset, 10)
        self.assertEqual(self.tracklist[10], self._session_ring.get_ring_track(0))

        self._session_ring.go_to_track("tension")
        self.assertEqual(self._session_ring.track_offset, 5)

        self._session_ring.go_to_scene(3)
        self.assertEqual(self._session_ring.scene_offset, 3)

        self._session_ring.go_to_scene("my cool scene")
        self.assertEqual(self._session_ring.scene_offset, 8)

    def test_ring_boundary(self):
        self._session_ring.move(x=10000, y=10000)
        self.assertEqual(self._session_ring.get_ring_track(self._session_ring.width - 1), self.tracklist[-1])
        self.assertEqual(self._session_ring.scene_offset, len(list(self.song.scenes)) - self._session_ring.height)

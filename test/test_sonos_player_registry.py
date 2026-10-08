"""Sonos lookup regression tests; no speakers or Spotify credentials required."""

import socket
import threading
import unittest
from unittest.mock import patch

from soco import core as soco_core
from soco.core import SoCo
from soco.xml import XML
from soco.zonegroupstate import ZoneGroupState

from spotifywebapipython.models import SpotifyConnectDevice, ZeroconfDiscoveryResult
from spotifywebapipython.spotifyapierror import SpotifyApiError
from spotifywebapipython.spotifyconnect.spotifyconnectdirectorytask import (
    SpotifyConnectDirectoryTask,
)


class SonosPlayerRegistryTest(unittest.TestCase):
    PLAYER_IP = "192.0.2.1"
    OTHER_IP = "192.0.2.2"

    @staticmethod
    def reset_registry():
        reset = getattr(soco_core, "soco_reset", None)
        if reset is not None:
            reset()
        else:
            # SoCo 0.30.6 has the same registry but no public reset helper.
            type(SoCo)._instances.clear()

    def setUp(self):
        # Isolate SoCo's global caches and restore them after each test. Resetting
        # this registry must never affect a running discovery thread or HA process.
        for target, name, value in (
            (type(SoCo), "_instances", {}),
            (SoCo, "zone_group_states", {}),
        ):
            replacement = patch.object(target, name, value)
            replacement.start()
            self.addCleanup(replacement.stop)
        for name in ("connect", "connect_ex"):
            network = patch.object(
                socket.socket, name, side_effect=AssertionError("Network forbidden")
            )
            network.start()
            self.addCleanup(network.stop)

        # Only exercise lookup; do not initialize the directory's network workers.
        self.directory = object.__new__(SpotifyConnectDirectoryTask)
        self.directory._SpotifyConnectDevices_RLock = threading.RLock()
        self.cached = SoCo(self.PLAYER_IP)
        self.cached._household_id = "test-household"
        self.directory._SonosPlayers = {self.PLAYER_IP: self.cached}
        self.device = SpotifyConnectDevice()
        self.device.Name = "Test speaker"
        discovery = ZeroconfDiscoveryResult()
        discovery.HostIpAddresses = [self.PLAYER_IP]
        self.device.DiscoveryResult = discovery

    def topology(self, coordinator="ONE"):
        # Simulate a topology update after another integration resets SoCo. The
        # parser updates the current singleton instances, not our cached object.
        state = ZoneGroupState()
        state._cache_until = float("inf")
        SoCo.zone_group_states["test-household"] = state
        tree = XML.fromstring(
            f'<ZoneGroups><ZoneGroup Coordinator="{coordinator}" ID="test">'
            f'<ZoneGroupMember UUID="ONE" Location="http://{self.PLAYER_IP}:1400/xml/device_description.xml" ZoneName="One" />'
            f'<ZoneGroupMember UUID="TWO" Location="http://{self.OTHER_IP}:1400/xml/device_description.xml" ZoneName="Two" />'
            '</ZoneGroup></ZoneGroups>'
        )
        state.update_soco_instances(tree)
        for ip in (self.PLAYER_IP, self.OTHER_IP):
            SoCo(ip)._household_id = "test-household"

    def test_reacquires_coordinator_after_registry_reset(self):
        self.reset_registry()
        self.topology()
        self.assertFalse(self.cached.is_coordinator)
        self.assertIsNone(self.cached.group)
        self.assertTrue(SoCo(self.PLAYER_IP).is_coordinator)

        result = self.directory.GetSonosPlayer(self.device)

        self.assertIs(result, SoCo(self.PLAYER_IP))
        self.assertIsNot(result, self.cached)
        self.assertIs(self.directory._SonosPlayers[self.PLAYER_IP], result)
        self.assertTrue(result.is_coordinator)

    def test_member_resolves_to_current_coordinator_after_reset(self):
        self.reset_registry()
        self.topology("TWO")

        result = self.directory.GetSonosPlayer(self.device)

        self.assertIs(result, SoCo(self.OTHER_IP))
        self.assertIs(self.directory._SonosPlayers[self.PLAYER_IP], SoCo(self.PLAYER_IP))

    def test_former_coordinator_does_not_keep_stale_role(self):
        self.topology()
        self.assertTrue(self.cached.is_coordinator)
        self.reset_registry()
        self.topology("TWO")

        self.assertIs(self.directory.GetSonosPlayer(self.device), SoCo(self.OTHER_IP))

    def test_non_coordinator_lookup_reacquires_member_after_reset(self):
        self.reset_registry()
        self.topology("TWO")

        result = self.directory.GetSonosPlayer(self.device, returnCoordinator=False)

        self.assertIs(result, SoCo(self.PLAYER_IP))
        self.assertIsNot(result, self.cached)
        self.assertFalse(result.is_coordinator)

    def test_healthy_lookup_reuses_current_instance(self):
        self.topology()
        self.assertIs(self.directory.GetSonosPlayer(self.device), self.cached)
        self.assertIs(self.directory.GetSonosPlayer(self.device), self.cached)

    def test_missing_coordinator_preserves_existing_fallback(self):
        self.topology("MISSING")
        result = self.directory.GetSonosPlayer(self.device)
        self.assertIs(result, self.cached)
        self.assertFalse(result.is_coordinator)
        self.assertIsNone(result.group.coordinator)

    def test_invalid_coordinator_option_defaults_to_true(self):
        self.topology("TWO")
        self.assertIs(self.directory.GetSonosPlayer(self.device, None), SoCo(self.OTHER_IP))

    def test_missing_device_preserves_validation(self):
        with self.assertRaises(SpotifyApiError):
            self.directory.GetSonosPlayer(None)

    def test_unknown_device_is_not_added_to_directory(self):
        self.directory._SonosPlayers.clear()
        with self.assertRaisesRegex(SpotifyApiError, "Could not find Sonos Controller"):
            self.directory.GetSonosPlayer(self.device)
        self.assertEqual(self.directory._SonosPlayers, {})


if __name__ == "__main__":
    unittest.main()

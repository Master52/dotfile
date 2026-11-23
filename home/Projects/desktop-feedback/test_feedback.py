import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


def load(name):
    loader = importlib.machinery.SourceFileLoader(name.replace('-', '_'), str(Path.home() / '.local/bin' / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


battery = load('battery-notify')
screenshot = load('screenshot-tool')


class FeedbackTests(unittest.TestCase):
    def test_low_battery_alerts_once_then_escalates(self):
        previous = None
        warned = 0
        notices = []
        for percent in (35, 20, 19, 18, 10, 9, 9):
            current = {'percent': percent, 'ac': False}
            events, warned = battery.events(current, previous, warned)
            notices += events
            previous = current
        self.assertEqual([n[1] for n in notices], ['Battery low', 'Battery critically low'])

    def test_critical_on_startup_does_not_also_show_low_alert(self):
        notices, warned = battery.events({'percent': 5, 'ac': False}, None, 0)
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0][0], 'critical')
        self.assertEqual(warned, 2)

    def test_connecting_charger_resets_alert_cycle(self):
        notices, warned = battery.events({'percent': 8, 'ac': True}, {'percent': 8, 'ac': False}, 2)
        self.assertEqual(notices[0][1], 'Charger connected')
        self.assertEqual(warned, 0)
        notices, warned = battery.events({'percent': 9, 'ac': False}, {'percent': 9, 'ac': True}, warned)
        self.assertEqual([n[1] for n in notices], ['Charger disconnected', 'Battery critically low'])

    def test_no_charger_notification_at_initial_startup(self):
        notices, _ = battery.events({'percent': 80, 'ac': True}, None, 0)
        self.assertEqual(notices, [])

    def test_reverse_and_out_of_bounds_area_selection(self):
        self.assertEqual(screenshot.rectangle((150, 140), (20, 30), 200, 200), (20, 30, 130, 110))
        self.assertEqual(screenshot.rectangle((-50, -20), (400, 500), 200, 200), (0, 0, 200, 200))

    def test_zero_width_selection_is_not_a_real_capture(self):
        self.assertEqual(screenshot.rectangle((10, 10), (10, 100), 200, 200)[2], 0)

    def test_window_selection_filters_hidden_desktops_and_respects_stacking(self):
        def client(wid, hidden=False):
            return {'id': wid, 'hidden': hidden, 'client': {'shown': True}}
        tree = {'firstChild': client(1), 'secondChild': {'firstChild': client(2), 'secondChild': client(3, True)}}
        state = {'stackingList': [2, 4, 1, 3], 'monitors': [
            {'focusedDesktopId': 10, 'desktops': [{'id': 10, 'root': tree}, {'id': 11, 'root': client(4)}]}]}
        self.assertEqual(screenshot.visible_window_ids(state), [2, 1])


if __name__ == '__main__':
    unittest.main()

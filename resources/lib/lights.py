import json
import requests

from tools import xbmclog


class Light(object):

    def __init__(self, bridge_ip, username, light_id, spec):
        self.bridge_ip = bridge_ip
        self.username = username

        self.light_id = light_id
        self.fullspectrum = ((spec['type'] == 'Color Light') or
                             (spec['type'] == 'Extended Color Light'))
        self.livingwhite = False
        self.name = spec['name'].encode("utf-8")

        self.init_hue = None
        self.hue = None
        try:
            self.init_hue = spec['state']['hue']
            self.hue = self.init_hue
        except KeyError:
            self.livingwhite = True

        self.init_sat = None
        self.sat = None
        try:
            self.init_sat = spec['state']['sat']
            self.sat = self.init_sat
        except KeyError:
            self.livingwhite = True

        try:
            self.init_bri = spec['state']['bri']
            self.bri = self.init_bri
        except KeyError:
            self.livingwhite = True

        self.init_on = spec['state']['on']
        self.on = self.init_on

        self.session = requests.Session()

    def set_state(self, hue=None, sat=None, bri=None, on=None,
                  transition_time=None):
        state = {}
        if transition_time is not None:
            state['transitiontime'] = transition_time
        if on is not None and on != self.on:
            self.on = on
            state['on'] = on
        if hue is not None and not self.livingwhite and hue != self.hue:
            self.hue = hue
            state['hue'] = hue
        if sat is not None and not self.livingwhite and sat != self.sat:
            self.sat = sat
            state['sat'] = sat
        if bri is not None and bri != self.bri:
            self.bri = bri
            state['bri'] = bri
            # Hue specific
            if bri <= 0 and self.on and on is None:
                self.on = False
                state['on'] = False
            if bri >= 1 and not self.on and on is None:
                self.on = True
                state['on'] = True

        data = json.dumps(state)
        try:
            endpoint = 'http://{}/api/{}/lights/{}/state'.format(
                self.bridge_ip, self.username, self.light_id)
            self.session.put(endpoint, data)
        except Exception:
            pass

    def restore_initial_state(self, transition_time=0):
        self.set_state(
            self.init_hue,
            self.init_sat,
            self.init_bri,
            self.init_on,
            transition_time
        )

    def save_state_as_initial(self):
        self.init_hue = self.hue
        self.init_sat = self.sat
        self.init_bri = self.bri
        self.init_on = self.on

    def __repr__(self):
        return ('<Light({}) {} hue: {}, sat: {}, bri: {}, on: {}>'.format(
            self.name, self.light_id, self.hue, self.sat, self.bri, self.on))


class Controller(object):

    def __init__(self, lights, settings):
        self.lights = lights
        self.settings = settings

    def on_playback_start(self):
        raise NotImplementedError(
            'on_playback_start must be implemented in the controller'
        )

    def on_playback_pause(self):
        raise NotImplementedError(
            'on_playback_pause must be implemented in the controller'
        )

    def on_playback_stop(self):
        raise NotImplementedError(
            'on_playback_stop must be implemented in the controller'
        )

    def set_state(self, hue=None, sat=None, bri=None, on=None,
                  transition_time=None, lights=None, force_on=True):
        xbmclog(
            'Kodi Hue: In {}.set_state(hue={}, sat={}, bri={}, '
            'on={}, transition_time={}, lights={}, force_on={})'.format(
                self.__class__.__name__, hue, sat, bri, on, transition_time,
                lights, force_on
            )
        )

        for light in self._calculate_subgroup(lights):
            if not force_on and not light.init_on:
                continue
            if bri:
                if self.settings.proportional_dim_time:
                    transition_time = self._transition_time(light, bri)
                else:
                    transition_time = self.settings.dim_time

            light.set_state(
                hue=hue, sat=sat, bri=bri, on=on,
                transition_time=transition_time
            )

    def restore_initial_state(self, lights=None, force_on=True):
        xbmclog(
            'Kodi Hue: In {}.restore_initial_state(lights={})'
            .format(self.__class__.__name__, lights)
        )

        for light in self._calculate_subgroup(lights):
            if not force_on and not light.init_on:
                continue
            transition_time = self.settings.dim_time
            if self.settings.proportional_dim_time:
                transition_time = self._transition_time(light, light.init_bri)

            light.restore_initial_state(
                transition_time
            )

    def save_state_as_initial(self, lights=None):
        xbmclog(
            'Kodi Hue: In {}.save_state_as_initial(lights={})'
            .format(self.__class__.__name__, lights)
        )

        for light in self._calculate_subgroup(lights):
            light.save_state_as_initial()

    def flash_lights(self):
        xbmclog(
            'Kodi Hue: In {} flash_lights())'
            .format(self.__class__.__name__)
        )
        self.set_state(
            on=False,
            force_on=self.settings.force_light_on,
        )

        self.restore_initial_state(
            force_on=self.settings.force_light_on,
        )

    def _calculate_subgroup(self, lights=None):
        if lights is None:
            ret = self.lights.values()
        else:
            ret = [light for light in
                   self.lights.values() if light.light_id in lights]

        xbmclog(
            'Kodi Hue: In {}._calculate_subgroup'
            '(lights={}) returning {}'.format(
                self.__class__.__name__, lights, ret)
        )
        return ret

    def _transition_time(self, light, bri):
        time = 0

        difference = abs(float(bri) - light.bri)
        total = float(light.init_bri) - self.settings.theater_start_bri
        if total == 0:
            return self.settings.dim_time
        proportion = difference / total
        time = int(round(proportion * self.settings.dim_time))

        return time

    def __repr__(self):
        return ('<{} {}>'.format(self.__class__.__name__, self.lights))

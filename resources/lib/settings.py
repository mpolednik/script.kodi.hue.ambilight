import sys

import xbmcaddon

__addon__ = sys.modules["__main__"].__addon__


class Settings():
    def __init__(self, *args, **kwargs):
        self.readxml()

    def readxml(self):
        global __addon__
        __addon__ = xbmcaddon.Addon()

        self.bridge_ip = __addon__.getSetting("bridge_ip")
        self.bridge_user = __addon__.getSetting("bridge_user")

        self.connected = __addon__.getSetting("connected") == "true"
        self.ambilight_group = __addon__.getSetting("ambilight_group")
        self.theater_group = __addon__.getSetting("theater_group")
        self.theater_subgroup = __addon__.getSetting("theater_subgroup")
        self.static_group = __addon__.getSetting("static_group")

        self.dim_time = int(float(__addon__.getSetting("dim_time"))*10)
        self.proportional_dim_time = __addon__.getSetting("proportional_dim_time") == "true"

        self.theater_start_bri_override = __addon__.getSetting("theater_start_bri_override") == "true"
        self.theater_start_bri = int(__addon__.getSetting("theater_start_bri").split(".")[0])

        self.theater_pause_dim_subgroup = __addon__.getSetting("theater_pause_dim_subgroup") == "true"
        self.theater_pause_bri_override = __addon__.getSetting("theater_pause_bri_override") == "true"
        self.theater_pause_bri = int(__addon__.getSetting("theater_pause_bri").split(".")[0])

        self.theater_stop_bri_override = __addon__.getSetting("theater_stop_bri_override") == "true"
        self.theater_stop_bri = int(__addon__.getSetting("theater_stop_bri").split(".")[0])

        self.ambilight_min = int(__addon__.getSetting("ambilight_min").split(".")[0])
        self.ambilight_max = int(__addon__.getSetting("ambilight_max").split(".")[0])

        self.ambilight_threshold_value = int(__addon__.getSetting("ambilight_threshold_value").split(".")[0])
        self.ambilight_threshold_saturation = int(__addon__.getSetting("ambilight_threshold_saturation").split(".")[0])

        self.color_bias = int(__addon__.getSetting("color_bias").split(".")[0])

        self.ambilight_start_dim_enable = __addon__.getSetting("ambilight_start_dim_enable") == "true"
        self.ambilight_start_dim_override = __addon__.getSetting("ambilight_start_dim_override") == "true"
        self.ambilight_start_dim = int(__addon__.getSetting("ambilight_start_dim").split(".")[0])

        self.ambilight_pause_bri_override = __addon__.getSetting("ambilight_pause_bri_override") == "true"
        self.ambilight_pause_bri = int(__addon__.getSetting("ambilight_pause_bri").split(".")[0])

        self.ambilight_stop_bri_override = __addon__.getSetting("ambilight_stop_bri_override") == "true"
        self.ambilight_stop_bri = int(__addon__.getSetting("ambilight_stop_bri").split(".")[0])

        self.static_start_random = __addon__.getSetting("static_start_random") == "true"
        self.static_start_hue_override = __addon__.getSetting("static_start_hue_override") == "true"
        self.static_start_hue = int(__addon__.getSetting("static_start_hue").split(".")[0])
        self.static_start_sat_override = __addon__.getSetting("static_start_sat_override") == "true"
        self.static_start_sat = int(__addon__.getSetting("static_start_sat").split(".")[0])
        self.static_start_bri_override = __addon__.getSetting("static_start_bri_override") == "true"
        self.static_start_bri = int(__addon__.getSetting("static_start_bri").split(".")[0])

        self.misc_initialflash = __addon__.getSetting("misc_initialflash") == "true"
        self.misc_disableshort = __addon__.getSetting("misc_disableshort") == "true"
        self.misc_disableshort_threshold = int(__addon__.getSetting("misc_disableshort_threshold"))
        self.force_light_on = __addon__.getSetting("force_light_on") == "true"

        if self.ambilight_min > self.ambilight_max:
            self.update(ambilight_min=self.ambilight_max)

    def update(self, **kwargs):
        self.__dict__.update(**kwargs)
        for k, v in kwargs.items():
            __addon__.setSetting(k, str(v))

    def __repr__(self):
        return '<Settings\n{}\n>'.format('\n'.join(['{}={}'.format(key, value) for key, value in self.__dict__.items()]))

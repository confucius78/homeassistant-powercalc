from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol


class PowercalcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 1

    async def async_step_user(self, user_input):
        if user_input is not None:
            return self.async_create_entry(
                title="Title of the entry",
                data={
                    "something_special": user_input["password"]
                },
            )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )
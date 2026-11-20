"""Stand-ins for the game and ModsSettings API 1.7.1 objects the mod talks to.

Behaviour mirrors the sources pinned in docs/DECOMPILED_REFERENCE.md.
"""

import types

ACCURACY_STACKS = "accuracyStacks"
BATTLE_FURY = "battleFury"
CONCENTRATION_MODE = "concentrationMode"
OVERHEAT_GUN = "overheatGun"
OVERHEAT_STACKS = "overheatStacks"
PILLBOX_SIEGE_MODE = "pillboxSiegeMode"


class Event(list):
    """Same semantics as the game's common/Event.py."""

    def __iadd__(self, delegate):
        if delegate not in self:
            self.append(delegate)
        return self

    def __isub__(self, delegate):
        if delegate in self:
            self.remove(delegate)
        return self

    def __call__(self, *args):
        for delegate in self[:]:
            delegate(*args)


class FakeFlashObject:
    def __init__(self):
        self.decor_crosshairs = []

    def as_addDecorCrosshair(self, type):
        self.decor_crosshairs.append(type)


def make_panel_classes():
    """Fresh copies of the panel classes, shaped like 2.4.1_EU."""

    class VehicleMechanicsPanel:
        _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {}

        def __init__(self, gameface_mechanics=()):
            self.flashObject = FakeFlashObject()
            self.gameface_mechanics = set(gameface_mechanics)

        def _isDAAPIInited(self):
            return True

        def onTrackedMechanicsUpdate(self, mechanics):
            mechanicsAS = (m for m in mechanics if m not in self.gameface_mechanics)
            componentsMap = self._VEHICLE_MECHANIC_UI_COMPONENTS_MAP
            for mechanicComponents in (
                componentsMap[m] for m in mechanicsAS if m in componentsMap
            ):
                self._addMechanicUIComponents(mechanicComponents)

        def _addMechanicUIComponents(self, mechanicComponents):
            raise NotImplementedError

    class DecorativeCrosshairPanelMeta(VehicleMechanicsPanel):
        def as_addDecorCrosshairS(self, type):
            return (
                self.flashObject.as_addDecorCrosshair(type)
                if self._isDAAPIInited()
                else None
            )

    class DecorativeCrosshairPanel(DecorativeCrosshairPanelMeta):
        _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {
            ACCURACY_STACKS: ("accuracy",),
            BATTLE_FURY: ("fury",),
            CONCENTRATION_MODE: ("concentration",),
            OVERHEAT_GUN: ("temperatureGunOverheat",),
            OVERHEAT_STACKS: ("overheat",),
            PILLBOX_SIEGE_MODE: ("pillboxSiege",),
        }

        def _addMechanicUIComponents(self, mechanicComponents):
            for componentName in mechanicComponents:
                self.as_addDecorCrosshairS(componentName)

    return DecorativeCrosshairPanel


class FakeModsSettingsApi:
    """The parts of ModsSettings API 1.7.1 (api.py) the mod relies on."""

    def __init__(self):
        self.state = {"settings": {}, "templates": {}}
        self.activeMods = set()
        self.onSettingsChanged = Event()
        self.onButtonClicked = Event()

    def setModTemplate(self, linkage, template, callback, buttonHandler=None):
        self.activeMods.add(linkage)
        current = self.state["templates"].get(linkage)
        if not current or self.compareTemplates(template, current):
            self.state["templates"][linkage] = template
            self.state["settings"][linkage] = self.getSettingsFromTemplate(template)
        self.onSettingsChanged += callback
        if buttonHandler is not None:
            self.onButtonClicked += buttonHandler
        return self.getModSettings(linkage, self.state["templates"][linkage])

    def getModSettings(self, linkage, template):
        current = self.state["templates"].get(linkage)
        if template and current:
            self.activeMods.add(linkage)
            if not self.compareTemplates(template, current):
                return self.state["settings"].get(linkage)
        return None

    def registerCallback(self, linkage, callback, buttonHandler=None):
        self.activeMods.add(linkage)
        self.onSettingsChanged += callback
        if buttonHandler is not None:
            self.onButtonClicked += buttonHandler

    def updateModSettings(self, linkage, newSettings):
        self.state["settings"][linkage] = newSettings
        self.onSettingsChanged(linkage, newSettings)

    def compareTemplates(self, newTemplate, oldTemplate):
        return newTemplate["settingsVersion"] > oldTemplate["settingsVersion"]

    def getSettingsFromTemplate(self, template):
        result = {}
        if "enabled" in template:
            result["enabled"] = template["enabled"]
        for column in ("column1", "column2"):
            for component in template.get(column, []):
                if "varName" in component and "value" in component:
                    result[component["varName"]] = component["value"]
        return result

    def apply(self, linkage, settings):
        self.updateModSettings(linkage, settings)


def _create_label(text, tooltip=None):
    return {"type": "Label", "text": text}


def _create_checkbox(text, varName, value, tooltip=None):
    return {"type": "CheckBox", "text": text, "varName": varName, "value": value}


def make_templates_module():
    module = types.ModuleType("gui.modsSettingsApi.templates")
    module.__dict__.update(createLabel=_create_label, createCheckbox=_create_checkbox)
    return module

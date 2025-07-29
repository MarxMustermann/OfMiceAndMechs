import re
from functools import partial

import src
import src.popups
import src.statusEffects


class AddedStatusEffect(src.popups.Popup):
    def __init__(self, effect):
        self.effect = effect
        super().__init__()

    def subscribedEvent(self):
        return "added status effect"

    def text(self):
        status_name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", self.effect.type)
        instance = self.effect()
        short_name = instance.getShortCode()
        description = instance.getLoreDescription()

        return f"you gained a new status effect: {status_name}({short_name})\n\n{description}"

    def conditionMet(self, params) -> bool:
        return self.character.statusEffects[-1].type == self.effect.type


for _, type in src.statusEffects.statusEffectMap.items():
    src.popups.popupsArray.append(partial(AddedStatusEffect, type))

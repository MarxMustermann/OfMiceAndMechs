from functools import partial

import src
import src.popups
import src.statusEffects


class AddedStatusEffect(src.popups.Popup):
    def __init__(self, effectType, message):
        self.effectType = effectType
        self.message = message
        super().__init__()

    def subscribedEvent(self):
        return "added status effect"

    def text(self):
        return self.message

    def conditionMet(self, params) -> bool:
        return self.character.statusEffects[-1].type == self.effectType


statusEffect_message = [(key, e().getLoreDescription()) for (key, e) in src.statusEffects.statusEffectMap.items()]

for type, message in statusEffect_message:
    src.popups.popupsArray.append(partial(AddedStatusEffect, type, message))

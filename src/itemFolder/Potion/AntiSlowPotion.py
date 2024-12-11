import src


class AntiSlowPotion(src.items.itemMap["Potion"]):
    type = "AntiSlowPotion"
    description = "removes \"slowed\" effect"
    name = "Anti Slow Potion"

    def apply(self, character):
        for effect in character.statusEffects[:]:
            if issubclass(type(effect),src.statusEffectFolder.slowed.Slowed):
                character.statusEffects.remove(effect)
                character.addMessage("the potion remove a \"slowed\" debuff")
        super().apply(character)

    def getLongInfo(self):
        return f"This Potion removes \"slowed\" effect from you"

src.items.addType(AntiSlowPotion,potion=True)

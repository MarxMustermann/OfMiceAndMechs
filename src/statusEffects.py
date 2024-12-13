from abc import ABC, abstractmethod


class StatusEffect:
    def __init__(self, ticks = None):
        self.ticks = ticks

    def advance(self):
        if self.ticks is not None:
            self.ticks -= 1

    def is_done(self):
        return self.ticks is not None and self.ticks <= 0

    def getShortCode(self):
        return self.type

    def getDescription(self):
        return "This Description is missing, feel free to report that as a bug. thx"

class DamageBuff(StatusEffect, ABC):
    @abstractmethod
    def modDamage(self, attacker, attacked, bonus, damage): ...


class ProtectionBuff(StatusEffect, ABC):
    @abstractmethod
    def ModProtection(self, attacker, attacked, bonus, damage): ...


class MovementBuff(StatusEffect, ABC):
    @abstractmethod
    def ModMovement(self, speed): ...

class AttackSpeedEffect(StatusEffect, ABC):
    @abstractmethod
    def modAttackSpeed(self,speed): ...

class HealthBuff(StatusEffect, ABC):
    @abstractmethod
    def ModHealth(self, health): ...


class HealthRegenBuff(StatusEffect, ABC):
    @abstractmethod
    def ModHealthRegen(self, healthRegen): ...


def addType(toRegister):
    statusEffectMap[toRegister.type] = toRegister


# mapping from strings to all items
# should be extendable
statusEffectMap = {
}

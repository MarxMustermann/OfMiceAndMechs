from abc import ABC, abstractmethod


class StatusEffect:
    def __init__(self, duration = None, reason = None):
        self.duration = duration
        self.reason = reason

    def advance(self):
        try:
            self.duration
        except:
            self.duration = 10

        if self.duration is not None:
            self.duration -= 1

    def is_done(self):
        return self.duration is not None and self.duration <= 0

    def getShortCode(self):
        return self.type

    def getLoreDescription(self):
        return "This Description is missing, feel free to report that as a bug. thx"

    def buildStatListDescription(self,description = ""):
        if self.reason:
            description += f"reason: {self.reason}\n"
        if self.duration:
            description += f"duration: {self.duration} ticks\n"
        return description

    def getDescription(self):
        result = []
        result.append(self.getLoreDescription())
        result.append("\n\n")
        result.append(self.buildStatListDescription())
        return result

class DamageBuff(StatusEffect, ABC):
    @abstractmethod
    def modDamage(self, attacker, attacked, bonus, damage): ...


class ProtectionBuff(StatusEffect, ABC):
    @abstractmethod
    def modProtection(self, attacker, attacked, bonus, damage): ...

class MovementBuff(StatusEffect, ABC):
    @abstractmethod
    def modMovement(self, speed): ...

class AttackSpeedEffect(StatusEffect, ABC):
    @abstractmethod
    def modAttackSpeed(self,speed): ...

class HealthBuff(StatusEffect, ABC):
    @abstractmethod
    def modHealth(self, health): ...


class HealthRegenBuff(StatusEffect, ABC):
    @abstractmethod
    def modHealthRegen(self, healthRegen): ...


def addType(toRegister):
    statusEffectMap[toRegister.type] = toRegister


# mapping from strings to all items
# should be extendable
statusEffectMap = {
}

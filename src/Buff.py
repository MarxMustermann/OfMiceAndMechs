from abc import ABC, abstractmethod


class Buff:
    def __init__(self, ticks = None):
        self.ticks = ticks

    def advance(self):
        if self.ticks is not None:
            self.ticks -= 1

    def is_done(self):
        return self.ticks is not None and self.ticks <= 0


class DamageBuff(Buff, ABC):
    @abstractmethod
    def ModDamage(self, attacker, attacked, bonus, damage): ...


class ProtectionBuff(Buff, ABC):
    @abstractmethod
    def ModProtection(self, attacker, attacked, bonus, damage): ...


class MovementBuff(Buff, ABC):
    @abstractmethod
    def ModMovement(self, speed): ...

def addType(toRegister):
    buffMap[toRegister.type] = toRegister


# mapping from strings to all items
# should be extendable
buffMap = {"Buff": Buff, "DamageBuff": DamageBuff, "ProtectionBuff": ProtectionBuff, "MovementBuff": MovementBuff}

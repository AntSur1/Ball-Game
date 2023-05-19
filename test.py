class Enemy(object):
    def __init__(self) -> None:
        self.maxHp = 2
        self.hp = self.maxHp


class Enemy_type_1(Enemy):
    def __init__(self) -> None:
        super().__init__()
        
        self.maxHp = 3
        self.hp = self.maxHp
        

        print(self.hp)


Enemy_type_1()
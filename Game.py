import random
import os
import time
import json

class Game:
    def __init__(self):
        self.running = True
        self.player = Player()
        self.state = Menu(self)
        self.start_time = time.time()

    def run(self):
        while self.running:
            self.update_effects()
            self.state.display()
            self.state.handle_input()

    def update_effects(self):
        self.player.update_effects()

class State:
    def __init__(self, game):
        self.game = game

    def display(self):
        pass

    def handle_input(self):
        pass

class Menu(State):
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== MAIN MENU ===")
        print("1. Start Game")
        print("2. Load Game")
        print("3. Cheat Menu")
        print("4. Quit")

    def handle_input(self):
        choice = input("> ")
        if choice == '1':
            self.game.state = Map(self.game)
        elif choice == '2':
            self.game.player.load()
            self.game.state = Map(self.game)
        elif choice == '3':
            self.game.state = CheatMenu(self.game)
        elif choice == '4':
            self.game.running = False

class CheatMenu(State):
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== CHEAT MENU ===")
        print("1. Set HP")
        print("2. Set Gold")
        print("3. Back to Menu")

    def handle_input(self):
        player = self.game.player
        choice = input("> ")
        if choice == '1':
            value = input("Enter new HP: ")
            if value.isdigit():
                player.hp = int(value)
                print("HP updated.")
            else:
                print("Invalid input.")
        elif choice == '2':
            value = input("Enter new Gold: ")
            if value.isdigit():
                player.gold = int(value)
                print("Gold updated.")
            else:
                print("Invalid input.")
        elif choice == '3':
            self.game.state = Menu(self.game)
        else:
            print("Invalid choice.")
        input("Press Enter to continue...")

class Map(State):
    def __init__(self, game):
        super().__init__(game)
        self.events = [Battle, Treasure, Trap, GatherMaterials]

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        player = self.game.player
        print(f"You are at position {player.position}.")
        print("1. Move Forward")
        print("2. Check Status")
        print("3. Save Game")
        print("4. Return to Menu")
        print("5. Visit Shop")
        print("6. Use Instant Heal Potion")
        print("7. Craft Gear")
        print("8. Potion Menu")

    def handle_input(self):
        player = self.game.player
        choice = input("> ")
        if choice == '1':
            player.position += 1
            event = random.choice(self.events)
            self.game.state = event(self.game)
        elif choice == '2':
            print(player.status())
            print(f"Inventory: {player.inventory}")
            print(f"Materials: {player.materials}")
            print(f"Potions: {player.potions}")
            print(f"Active Effects: {list(player.effects.keys())}")
            input("Press Enter to continue...")
        elif choice == '3':
            player.save()
            print("Game Saved.")
            input("Press Enter to continue...")
        elif choice == '4':
            self.game.state = Menu(self.game)
        elif choice == '5':
            self.game.state = Shop(self.game)
        elif choice == '6':
            if player.use_instant_potion():
                print("You used an Instant Heal potion and restored 30 HP.")
            else:
                print("No Instant Heal potions available.")
            input("Press Enter to continue...")
        elif choice == '7':
            self.game.state = Crafting(self.game)
        elif choice == '8':
            self.game.state = PotionMenu(self.game)

class Player:
    def __init__(self):
        self.hp = 100
        self.gold = 0
        self.position = 0
        self.inventory = []
        self.weapon = None
        self.armor = None
        self.materials = {"Iron": 0, "Wood": 0, "Crystal": 0}
        self.potions = {"Regen": 0, "Luck": 0, "Instant Heal": 0}
        self.effects = {}

    def status(self):
        return (f"HP: {self.hp}, Gold: {self.gold}, Position: {self.position}, Weapon: {self.weapon}, Armor: {self.armor}")

    def save(self):
        data = {
            'hp': self.hp,
            'gold': self.gold,
            'position': self.position,
            'inventory': self.inventory,
            'weapon': self.weapon,
            'armor': self.armor,
            'materials': self.materials,
            'potions': self.potions,
            'effects': self.effects
        }
        with open('savegame.json', 'w') as f:
            json.dump(data, f)

    def load(self):
        try:
            with open('savegame.json', 'r') as f:
                data = json.load(f)
                self.hp = data['hp']
                self.gold = data['gold']
                self.position = data['position']
                self.inventory = data['inventory']
                self.weapon = data.get('weapon')
                self.armor = data.get('armor')
                self.materials = data.get('materials', {"Iron":0, "Wood":0, "Crystal":0})
                self.potions = data.get('potions', {"Regen": 0, "Luck": 0, "Instant Heal":0})
                self.effects = data.get('effects', {})
        except FileNotFoundError:
            print("No save file found.")
            input("Press Enter to continue...")

    def weapon_bonus(self):
        bonuses = {
            "Wood Sword": 5,
            "Stone Sword": 10,
            "Iron Sword": 15,
            "Crafted Blade": 25,
            "Upgraded Blade": 35
        }
        return bonuses.get(self.weapon, 0)

    def armor_bonus(self):
        reductions = {
            "Wood Armor": 2,
            "Stone Armor": 5,
            "Iron Armor": 8,
            "Crafted Plate": 12,
            "Upgraded Plate": 18
        }
        return reductions.get(self.armor, 0)

    def use_instant_potion(self):
        if self.potions["Instant Heal"] > 0:
            self.hp = min(100, self.hp + 30)
            self.potions["Instant Heal"] -= 1
            return True
        return False

    def update_effects(self):
        expired = []
        for effect, data in self.effects.items():
            if time.time() >= data['end']:
                expired.append(effect)
            elif effect == "Regen":
                self.hp = min(100, self.hp + 1)
        for effect in expired:
            del self.effects[effect]

class Battle(State):
    def __init__(self, game):
        super().__init__(game)
        self.enemy_hp = random.randint(20, 50)

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You encountered an enemy!")
        print(f"Enemy HP: {self.enemy_hp}")
        print("1. Attack")
        print("2. Run")

    def handle_input(self):
        player = self.game.player
        choice = input("> ")
        if choice == '1':
            base_damage = random.randint(10, 30)
            total_damage = base_damage + player.weapon_bonus()
            self.enemy_hp -= total_damage
            print(f"You dealt {total_damage} damage!")
            if self.enemy_hp <= 0:
                print("Enemy defeated!")
                gold_earned = random.randint(5, 20)
                if "Luck" in player.effects:
                    gold_earned = int(gold_earned * 1.5)
                player.gold += gold_earned
                self.game.state = Map(self.game)
            else:
                enemy_damage = random.randint(5, 15)
                reduced_damage = max(0, enemy_damage - player.armor_bonus())
                player.hp -= reduced_damage
                print(f"Enemy dealt {reduced_damage} damage!")
                if player.hp <= 0:
                    print("You died!")
                    self.game.running = False
        elif choice == '2':
            if random.random() < 0.5:
                print("You escaped!")
                self.game.state = Map(self.game)
            else:
                print("Failed to escape!")
                enemy_damage = random.randint(5, 15)
                reduced_damage = max(0, enemy_damage - player.armor_bonus())
                player.hp -= reduced_damage
                print(f"Enemy dealt {reduced_damage} damage!")
                if player.hp <= 0:
                    print("You died!")
                    self.game.running = False
        input("Press Enter to continue...")

class Treasure(State):
    def __init__(self, game):
        super().__init__(game)
        self.gold = random.randint(10, 50)

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"You found a treasure chest with {self.gold} gold!")

    def handle_input(self):
        player = self.game.player
        gold_found = self.gold
        if "Luck" in player.effects:
            gold_found = int(gold_found * 1.5)
        player.gold += gold_found
        input("Press Enter to continue...")
        self.game.state = Map(self.game)

class Trap(State):
    def __init__(self, game):
        super().__init__(game)
        self.damage = random.randint(10, 25)

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You fell into a trap!")
        print(f"You took {self.damage} damage!")

    def handle_input(self):
        player = self.game.player
        reduced_damage = max(0, self.damage - player.armor_bonus())
        player.hp -= reduced_damage
        if player.hp <= 0:
            print("You died!")
            self.game.running = False
        input("Press Enter to continue...")
        if self.game.running:
            self.game.state = Map(self.game)

class Shop(State):
    def __init__(self, game):
        super().__init__(game)
        self.items = {
            "Instant Heal Potion": 20,
            "Regen Potion": 50,
            "Luck Potion": 60,
            "Wood Sword": 30,
            "Stone Sword": 60,
            "Iron Sword": 100,
            "Wood Armor": 25,
            "Stone Armor": 55,
            "Iron Armor": 90
        }

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to the Shop!")
        print("Your Gold:", self.game.player.gold)
        for i, (item, cost) in enumerate(self.items.items(), 1):
            print(f"{i}. {item} - {cost} Gold")
        print(f"{len(self.items) + 1}. Exit Shop")

    def handle_input(self):
        choice = input("> ")
        keys = list(self.items.keys())
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(keys):
                item = keys[index]
                cost = self.items[item]
                player = self.game.player
                if player.gold >= cost:
                    player.gold -= cost
                    if "Sword" in item or "Armor" in item:
                        if "Sword" in item:
                            player.weapon = item
                        else:
                            player.armor = item
                    elif "Potion" in item:
                        if "Instant Heal" in item:
                            player.potions["Instant Heal"] += 1
                        elif "Regen" in item:
                            player.potions["Regen"] += 1
                        elif "Luck" in item:
                            player.potions["Luck"] += 1
                    print(f"Bought {item}!")
                else:
                    print("Not enough gold!")
            elif index == len(keys):
                self.game.state = Map(self.game)
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")
        input("Press Enter to continue...")

class GatherMaterials(State):
    def __init__(self, game):
        super().__init__(game)
        self.material = random.choice(["Iron", "Wood", "Crystal"])
        self.amount = random.randint(1, 3)

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"You gathered {self.amount} {self.material}.")

    def handle_input(self):
        player = self.game.player
        player.materials[self.material] = player.materials.get(self.material, 0) + self.amount
        input("Press Enter to continue...")
        self.game.state = Map(self.game)

class PotionMenu(State):
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        player = self.game.player
        print("=== Potion Menu ===")
        print(f"1. Use Regeneration Potion (You have {player.potions['Regen']})")
        print(f"2. Use Luck Potion (You have {player.potions['Luck']})")
        print("3. Back")

    def handle_input(self):
        player = self.game.player
        choice = input("> ")
        if choice == '1':
            if player.potions["Regen"] > 0:
                player.effects["Regen"] = {'end': time.time() + 300}  # 5 minutes
                player.potions["Regen"] -= 1
                print("Regen effect activated for 5 minutes.")
            else:
                print("No Regen potions.")
        elif choice == '2':
            if player.potions["Luck"] > 0:
                player.effects["Luck"] = {'end': time.time() + 300}
                player.potions["Luck"] -= 1
                print("Luck effect activated for 5 minutes.")
            else:
                print("No Luck potions.")
        elif choice == '3':
            self.game.state = Map(self.game)
            return
        else:
            print("Invalid choice.")
        input("Press Enter to continue...")

class Crafting(State):
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        player = self.game.player
        print("=== Crafting Menu ===")
        print(f"Materials: Iron({player.materials.get('Iron',0)}), Wood({player.materials.get('Wood',0)}), Crystal({player.materials.get('Crystal',0)})")
        print(f"1. Craft Crafted Blade (Requires 5 Iron, 2 Crystal)")
        print(f"2. Craft Crafted Plate (Requires 5 Iron, 3 Wood)")
        print(f"3. Upgrade Blade to Upgraded Blade (Requires Crafted Blade + 3 Crystal)")
        print(f"4. Upgrade Plate to Upgraded Plate (Requires Crafted Plate + 3 Crystal)")
        print("5. Back")
    def handle_input(self):
        player = self.game.player
        choice = input("> ")
        if choice == '1':
            if player.materials.get("Iron", 0) >= 5 and player.materials.get("Crystal", 0) >= 2:
                player.materials["Iron"] -= 5
                player.materials["Crystal"] -= 2
                player.weapon = "Crafted Blade"
                print("You crafted a Crafted Blade!")
            else:
                print("Not enough materials.")
        elif choice == '2':
            if player.materials.get("Iron", 0) >= 5 and player.materials.get("Wood", 0) >= 3:
                player.materials["Iron"] -= 5
                player.materials["Wood"] -= 3
                player.armor = "Crafted Plate"
                print("You crafted a Crafted Plate!")
            else:
                print("Not enough materials.")
        elif choice == '3':
            if player.weapon == "Crafted Blade" and player.materials.get("Crystal", 0) >= 3:
                player.materials["Crystal"] -= 3
                player.weapon = "Upgraded Blade"
                print("You upgraded your blade to Upgraded Blade!")
            else:
                print("Requirements not met for upgrading blade.")
        elif choice == '4':
            if player.armor == "Crafted Plate" and player.materials.get("Crystal", 0) >= 3:
                player.materials["Crystal"] -= 3
                player.armor = "Upgraded Plate"
                print("You upgraded your plate to Upgraded Plate!")
            else:
                print("Requirements not met for upgrading plate.")
        elif choice == '5':
            self.game.state = Map(self.game)
            return
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    game = Game()
    game.run()
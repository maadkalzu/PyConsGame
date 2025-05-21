import random
import os
import time
import json

class Game:
    def __init__(self):
        self.running = True
        self.player = Player()
        self.state = Menu(self)

    def run(self):
        while self.running:
            self.state.display()
            self.state.handle_input()

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

class Map(State):
    def __init__(self, game):
        super().__init__(game)
        self.events = [Battle, Treasure, Trap, Shop]

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        player = self.game.player
        print(f"You are at position {player.position}.")
        print("1. Move Forward")
        print("2. Check Status")
        print("3. Save Game")
        print("4. Return to Menu")
        print("5. Visit Shop")

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
            input("Press Enter to continue...")
        elif choice == '3':
            player.save()
            print("Game Saved.")
            input("Press Enter to continue...")
        elif choice == '4':
            self.game.state = Menu(self.game)
        elif choice == '5':
            self.game.state = Shop(self.game)

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

class Player:
    def __init__(self):
        self.hp = 100
        self.gold = 0
        self.position = 0
        self.inventory = []
        self.weapon = None
        self.armor = None

    def status(self):
        return f"HP: {self.hp}, Gold: {self.gold}, Position: {self.position}, Weapon: {self.weapon}, Armor: {self.armor}"

    def save(self):
        data = {
            'hp': self.hp,
            'gold': self.gold,
            'position': self.position,
            'inventory': self.inventory,
            'weapon': self.weapon,
            'armor': self.armor
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
        except FileNotFoundError:
            print("No save file found.")
            input("Press Enter to continue...")

    def weapon_bonus(self):
        bonuses = {"Wood Sword": 5, "Stone Sword": 10, "Iron Sword": 15}
        return bonuses.get(self.weapon, 0)

    def armor_bonus(self):
        reductions = {"Wood Armor": 2, "Stone Armor": 5, "Iron Armor": 8}
        return reductions.get(self.armor, 0)

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
                player.gold += random.randint(5, 20)
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
        self.game.player.gold += self.gold
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
            "Potion": 20,
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
                if self.game.player.gold >= cost:
                    self.game.player.gold -= cost
                    if "Sword" in item:
                        self.game.player.weapon = item
                    elif "Armor" in item:
                        self.game.player.armor = item
                    else:
                        self.game.player.inventory.append(item)
                    print(f"You bought a {item}!")
                else:
                    print("Not enough gold!")
            elif index == len(keys):
                self.game.state = Map(self.game)
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")
        input("Press Enter to continue...")

if __name__ == '__main__':
    g = Game()
    g.run()

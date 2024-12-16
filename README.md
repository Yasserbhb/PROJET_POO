# PROJET_POO

# League on Budget

Welcome to **League on Budget**, a 2D turn-based combat game inspired by the popular 5v5 game **League of Legends**. We've brought the action to a **grid-based system**, making it both strategic and fun to play.

---

## **Key Features**
- **Vision System**: Limited sight range based on your allies and terrain mechanics.
- **Turn-Based Combat**: Engage in 2v2 battles on a **21x21 grid**.
- **Unique Champions**: Each character comes with distinct abilities and stats.
- **Interactive Grid**: Includes terrain types (grass, bushes, water, and rocks) that influence gameplay.
- **Strategic Elements**: Collect potions, defeat monsters, and break barriers to win.

---

## **How to Play**

### **Main Screen**
- **Press `Enter`**: Start the game.
- **Press `Esc`**: Quit the game.

---

### **Champion Selection**
- Teams take turns selecting champions:
  - **Blue team selects first**, followed by the **Red team**.
  - Use **keys `1` to `5` (above the letters)** to select a champion.
    - **Note**: The keys on the **side of the keyboard** (numpad) are **not supported**.
  - **Press `Enter`** to lock in your champion.

Once all champions are selected, the game begins!

---

### **Gameplay Phases**
Each character has three phases during their turn:

1. **Move Phase**:
LINK 
   - Use the **arrow keys** to move your character.
   - **Press `Space`** to lock in your position and switch to the attack phase.

2. **Attack Phase**:
LINK to baisc and abilities side by side
   - Choose between **basic attacks** and **abilities**:
     - **Basic Attack**: Default attack with a red range indicator.
     - **Abilities**:
       - **Press `1`, `2`, or `3`** to select an ability.
       - **Press `C`** to switch back to basic attack mode.
     - **Press `Space`** to confirm your attack or action.
   - Abilities can target:
     - **Allies** for buffs and healing.
     - **Enemies** for debuffs and damage.
   - If out of mana or no valid targets are present, press `C` to perform a basic attack (no mana cost).

3. **Wait Phase**:
   - Watch the results of your actions (damage, buffs, or heals).
   - **Press `R`** to end your turn and switch to the next player.

---

### **Game Elements**


#### **Grid Terrain**
![Alt Text](hhttps://i.imgur.com/VDZQzXV.png)
The grid features four tile types:
- **Grass**: Standard movement.
- **Bushes**: Hide units from enemy vision unless they are in the same bush.
- **Rocks**: Impassable terrain.
- **Water**: Slows movement but is traversable.

---

#### **Vision System**
Link to vision + and -
The game features a **fog of war** mechanic where visibility is limited:
- **Sight Range**: You can see within a certain range of your character and any allies.
- **Hidden Areas**: Any grid spaces outside your sight range or behind terrain obstacles (e.g., rocks) are hidden.
- **Bush Mechanic**: Units inside bushes (from the enemy team) are invisible .
- **Allies**: You share vision with your teammates, so you can always see what an ally sees.

This system adds an extra layer of strategy, encouraging players to stay close to their team while exploring.

---

#### **Damage and Defense**
There are two types of damage and corresponding defenses:
1. **Physical Damage**:
   - Reduced by the target's **Physical Defense**.
   - Displayed in **red numbers** during the game.
Link to red number
2. **Magical Damage**:
   - Reduced by the target's **Magical Defense**.
   - Displayed in **purple numbers** during the game.
Link to purple number
3. **Healing**:
   - Restores health points (HP) to the target.
   - Displayed in **green numbers with a "+" sign**.
Link to green number
---

#### **Monsters**
Link photo of the 3
Three types of neutral monsters appear on the grid:
- **Blue Buff**: Increases attack damage and max health.
- **Red Buff**: Increases attack damage and max health.
- **Big Buff**: Bigger Increases to both health and damage.

Monsters may also drop **keys** after a certain number of rounds. Attacking monsters will make them retaliate!

---

#### **Potions**
Link photo of the 5
Potions spawn randomly on **grass** and **water** tiles. Collect them to gain powerful bonuses:
- **Red Potion**: Restores health.
- **Green Potion**: Increases max HP.
- **Blue Potion**: Restores mana.
- **Golden Potion**: Reduces ability cooldowns.
- **Black Potion**: Boosts critical hit chance.

Potions have varying rarities, so plan carefully to maximize their effects.

---

#### **Keys and Barriers**
Key system
- **Goal**: Collect 3 keys of the **enemy team's color** to break their barrier and attack their Nexus.
- Each team starts with:
  - 2 keys of their own color.
  - Blue team needs **Red keys**, and Red team needs **Blue keys**.
- **How to collect keys**:
  - Kill enemy players to steal all their keys.
  - Defeat monsters that drop keys after certain rounds.
- **Barrier Mechanics**:
  - Once the barrier is broken, it stays down even if keys are lost later.
- **Victory Condition**:
  - Destroy the enemy Nexus after breaking their barrier to win the game.

---

### **Visual Indicators**
Link to triangle
- **Buffs**: Green upward triangle.
- **Debuffs**: Red downward triangle.
- **Damage**: Red flash on the unit (besides the damage umbers)
- **Healing**: Green flash on the unit (besides the green numbers with a "+" sign.)

---

## **Controls Overview**

| **Action**               | **Key**                |
|--------------------------|------------------------|
| Quit Game (Main Screen)  | `Esc`                 |
| Start Game (Main Screen) | `Enter`               |
| Select Champion          | `1-5` (above letters) |
| Lock Champion            | `Enter`               |
| Move Character           | Arrow Keys            |
| Confirm Position         | `Space`               |
| Confirm Attack           | `Space`               |
| Select Ability           | `1`, `2`, `3`         |
| Switch to Basic Attack   | `C`                   |
| End Turn                 | `R`                   |

---

## **Additional Notes**

- Only the **number keys above the letters** work for champion selection or ability selection.
- The **side numpad keys** are **not supported**.

---

Enjoy strategizing and battling in **League on Budget**!

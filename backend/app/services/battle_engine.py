

from app.dtos.battles import Pokemon
from app.services.prompt_engine import choose_ai_move, generate_battle_narration


def take_turn(pokemon: Pokemon, opponent: Pokemon):
    move = choose_ai_move(pokemon, opponent)

    damage = calculate_damage(pokemon, opponent, move)

    opponent.hp -= damage

    battle_text = generate_battle_narration(pokemon, opponent, move)

    return battle_text


def calculate_damage(pokemon: Pokemon, opponent: Pokemon, move: str):
    return 100
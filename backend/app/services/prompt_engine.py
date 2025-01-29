import random
from app.dtos.battles import Pokemon
from openai import OpenAI
from app.settings import settings

print(settings.OPENAI_API_KEY)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def choose_ai_move(pokemon: Pokemon, opponent: Pokemon):
    prompt = f"""
    You are an expert Pokémon battle strategist. Choose the most effective move for {pokemon.name} against {opponent.name}.
    - {pokemon.name} has the following moves: {", ".join(pokemon.moves)}
    - {pokemon.name} has {pokemon.hp} HP
    - Opponent {opponent.name} has {opponent.hp} HP
    Choose the most effective move considering type advantages, HP, and move effectiveness.
    Return ONLY the move name.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    chosen_move = response.choices[0].message.content.strip()

    return chosen_move or random.choice(pokemon.moves)


def generate_battle_narration(pokemon1: Pokemon, pokemon2: Pokemon, move: str):
    prompt = f"""
    You are a battle announcer for a Pokemon battle.
    Provide an exciting and concise description of this turn:
      - {pokemon1.name} (HP: {pokemon1.hp})
      - {pokemon2.name} (HP: {pokemon2.hp})
    {pokemon1.name} used {move}.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

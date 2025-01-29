from pydantic import BaseModel

class Pokemon(BaseModel):
    name: str
    moves: list[str]

class StartBattleDTO(BaseModel):
    pokemon1: Pokemon
    pokemon2: Pokemon
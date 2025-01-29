from pydantic import BaseModel, Field

class Pokemon(BaseModel):
    name: str
    moves: list[str]
    hp: int = Field(default=100)

class StartBattleDTO(BaseModel):
    pokemon1: Pokemon
    pokemon2: Pokemon
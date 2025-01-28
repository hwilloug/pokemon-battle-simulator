from pydantic import BaseModel


class Pokemon(BaseModel):
    name: str
    level: int
    type: str
    moves: list[str]


class Team(BaseModel):
    name: str
    pokemon: list[Pokemon]


class BattleInput(BaseModel):
    team1: Team
    team2: Team


class BattleLog(BaseModel):
    logs: list[str]
    winner: str

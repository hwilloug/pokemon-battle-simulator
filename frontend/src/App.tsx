import { useEffect, useMemo, useState } from 'react'
import { Pokemon, PokemonDetail, useAllPokemon, useQueryApi } from './server/useAllPokemon';
import capitalize from './utils/capitalize';

interface BattleLog {
  type: 'BATTLE_START' | 'TURN' | 'BATTLE_END' | 'ERROR';
  status?: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  turn_number?: number;
  action?: string;
  timestamp: string;
  pokemon1?: any;
  pokemon2?: any;
  winner?: string;
  message?: string;
}

interface WebSocketMessage {
  type: 'BATTLE_UPDATE';
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  data: BattleLog | { error: string };
}

function App() {
  const { data: pokemon } = useAllPokemon()

  const [taskId, setTaskId] = useState('')
  const [messages, setMessages] = useState<BattleLog[]>([])
  const [status, setStatus] = useState<string>('')
  const [selectedPokemon1, setSelectedPokemon1] = useState<Pokemon | undefined>()
  const [selectedPokemon2, setSelectedPokemon2] = useState<Pokemon | undefined>()
  const [selectedMoves1, setSelectedMoves1] = useState({
    0: '',
    1: '',
    2: '',
    3: ''
  })
  const [selectedMoves2, setSelectedMoves2] = useState({
    0: '',
    1: '',
    2: '',
    3: ''
  })

  useEffect(() => {
    if (taskId) {
      const socket = new WebSocket(`ws://localhost:8000/ws/${taskId}`)

      socket.onopen = () => {
        console.log('WebSocket connected')
      }

      socket.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('Received message:', message);

        if (message.status === 'IN_PROGRESS') {
          setMessages((prevMessages) => [...prevMessages, message.data as BattleLog]);
        } else if (message.status === 'COMPLETED') {
          setStatus('COMPLETED');
          // Debug the complete message structure
          console.log('Completed message:', message);
          console.log('Message data:', message.data);
          
          const result = message.data as BattleLog;
          setMessages((prevMessages) => [...prevMessages, result]);
          socket.close();
        } else if (message.status === 'FAILED') {
          setStatus('FAILED');
          const error = message.data as { error: string };
          console.error('Battle failed:', error.error);
        }
      }

      socket.onclose = () => {
        console.log('WebSocket disconnected')
      }

      return () => {
        socket.close()
      }
    }
  }, [taskId])

  const handleStartBattle = () => {
    setMessages([]) // Clear previous messages
    setStatus('') // Reset status
    fetch(`http://localhost:8000/battles/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        pokemon1: {
          name: selectedPokemon1?.name,
          moves: Object.values(selectedMoves1)
        },
        pokemon2: {
          name: selectedPokemon2?.name,
          moves: Object.values(selectedMoves2)
        }
      })
    })
      .then((response) => response.json())
      .then((data) => setTaskId(data.task_id))
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-2xl font-bold m-4">Pokemon Battle Simulator</h1>
      <div className="grid grid-cols-2 m-4 space-x-4">
        <div>
          <select className="w-full text-center" onChange={(e) => setSelectedPokemon1(pokemon?.results.find(p => p.name === e.target.value))}>
            {pokemon?.results.map(p => <option key={p.name} value={p.name}>{capitalize(p.name)}</option>)}
          </select>
          {selectedPokemon1 && <PokemonBuilder pokemon={selectedPokemon1} selectedMoves={selectedMoves1} setSelectedMoves={setSelectedMoves1} />}
        </div>
        <div>
          <select className="w-full text-center" onChange={(e) => setSelectedPokemon2(pokemon?.results.find(p => p.name === e.target.value))}>
            {pokemon?.results.map(p => <option key={p.name} value={p.name}>{capitalize(p.name)}</option>)}
          </select>
          {selectedPokemon2 && <PokemonBuilder pokemon={selectedPokemon2} selectedMoves={selectedMoves2} setSelectedMoves={setSelectedMoves2} />}
        </div>
      </div>
        <button
          className="bg-purple-500 text-white px-4 py-2 rounded-md disabled:opacity-50"
          onClick={handleStartBattle}
          disabled={!selectedPokemon1 || !selectedPokemon2 || !selectedMoves1 || !selectedMoves2}
      >
        Start Battle
      </button>
      <hr className="w-full border-gray-700 my-4" />
      <h2 className="text-lg font-bold">Status: {status}</h2>
      <h2 className="text-lg font-bold">Battle Log</h2>
      <div className="mt-4 space-y-2">
        {messages.map((message, index) => (
          <div key={index} className="p-2 bg-gray-100 rounded">
            {message.type === 'BATTLE_START' && (
              <p>Battle started between {message.pokemon1} and {message.pokemon2}</p>
            )}
            {message.type === 'TURN' && (
              <p>Turn {message.turn_number}: {message.action}</p>
            )}
            {message.status === 'COMPLETED' && (
              <p>Battle ended! Winner: {message.winner}</p>
            )}
            {message.type === 'ERROR' && (
              <p className="text-red-500">Error: {message.message}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

const PokemonBuilder = ({ pokemon, selectedMoves, setSelectedMoves }: { pokemon: Pokemon, selectedMoves: any, setSelectedMoves: any }) => {
  const { data: pokemonDetail, isLoading } = useQueryApi(pokemon.url)

  const moves = useMemo(() => {
    return Array.from(new Set(pokemonDetail?.moves.map((move: any) => move.move.name)))
  }, [pokemonDetail])

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="bg-gray-100 p-4 rounded-md">
      <div className="flex flex-row items-center">
        <img src={pokemonDetail?.sprites.front_default} alt={pokemonDetail?.name} />
        <h1>{capitalize(pokemonDetail?.name)}</h1>
      </div>
      <div>
        <h2>Moves</h2>
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <select key={i} className="w-full p-2 border border-gray-300 rounded-md" onChange={(e) => setSelectedMoves((prevMoves) => ({ ...prevMoves, [i]: e.target.value }))} value={selectedMoves[i]}>
              {moves.map((move) => (
                <option key={move} value={move}>
                  {capitalize(move.split('-').join(' '))}
                </option>
              ))}
            </select>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App

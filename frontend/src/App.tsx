import { useEffect, useState } from 'react'

interface BattleLog {
  type: 'BATTLE_START' | 'TURN' | 'BATTLE_END' | 'ERROR';
  status?: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  turn_number?: number;
  action?: string;
  timestamp: string;
  team1?: any;
  team2?: any;
  winner?: string;
  message?: string;
}

interface WebSocketMessage {
  type: 'BATTLE_UPDATE';
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  data: BattleLog | { error: string };
}

function App() {
  const [taskId, setTaskId] = useState('')
  const [messages, setMessages] = useState<BattleLog[]>([])
  const [status, setStatus] = useState<string>('')

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
    fetch(`http://localhost:8000/battles/start`)
      .then((response) => response.json())
      .then((data) => setTaskId(data.task_id))
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-2xl font-bold m-4">Pokemon Battle Simulator</h1>
      <button
        className="bg-purple-500 text-white px-4 py-2 rounded-md"
        onClick={handleStartBattle}
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
              <p>Battle started between {message.team1?.pokemon[0]} and {message.team2?.pokemon[0]}</p>
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

export default App

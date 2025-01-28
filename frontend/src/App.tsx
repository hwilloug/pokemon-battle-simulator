import { useEffect, useState } from 'react'

function App() {
  const [taskId, setTaskId] = useState('')

  const [messages, setMessages] = useState<string[]>([])
  const [status, setStatus] = useState<string>('')
  useEffect(() => {
    if (taskId) {
      const socket = new WebSocket(`ws://localhost:8000/ws/${taskId}`)

      socket.onopen = () => {
        console.log('WebSocket connected')
      }

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setMessages((prevMessages) => [...prevMessages, data.message])
        setStatus(data.status)
      }

      socket.onclose = () => {
        console.log('WebSocket disconnected')
      }
    }
  }, [taskId])

  const handleStartBattle = () => {
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
      <h2 className="text-lg font-bold">Messages</h2>
      {messages.map((message, index) => (
        <p key={index}>{message}</p>
      ))}
    </div>
  )
}

export default App

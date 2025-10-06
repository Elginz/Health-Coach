import { useState } from 'react';
import './App.css';

function App() {
  const [goalSet, setGoalSet] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  // Handler for the initial goal form submission
  const handleGoalSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const profile = {
      age: parseInt(formData.get('age')),
      sex: 'F', // Hardcoded for simplicity
      height_cm: parseInt(formData.get('height')),
      weight_kg: parseFloat(formData.get('currentWeight')),
      target_weight_kg: parseFloat(formData.get('targetWeight')),
      activity: 'light', // Hardcoded for simplicity
    };

    // Call the backend /api/goal endpoint
    const response = await fetch('/api/goal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'demo', profile }),
    });
    const data = await response.json();

    setMessages([{ from: 'ava', text: data.text }]);
    setGoalSet(true);
  };

  // Handler for sending a chat message
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newMessages = [...messages, { from: 'user', text: userInput }];
    setMessages(newMessages);
    setUserInput('');

    // Call the backend /api/chat endpoint
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'demo', message: userInput }),
    });
    const data = await response.json();

    setMessages([...newMessages, { from: 'ava', text: data.text }]);
  };

  // --- Render logic ---
  if (!goalSet) {
    return <GoalForm onSubmit={handleGoalSubmit} />;
  }

  return (
    <div className="chat-container">
      <h1>Chat with AVA</h1>
      <div className="message-list">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.from}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleChatSubmit} className="message-form">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ask AVA something..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

// Simple GoalForm component
const GoalForm = ({ onSubmit }) => (
  <div className="form-container">
    <h2>Set Your Goal</h2>
    <form onSubmit={onSubmit}>
      <label>Age: <input name="age" type="number" defaultValue="61" /></label>
      <label>Height (cm): <input name="height" type="number" defaultValue="158" /></label>
      <label>Current Weight (kg): <input name="currentWeight" type="number" step="0.1" defaultValue="72" /></label>
      <label>Target Weight (kg): <input name="targetWeight" type="number" step="0.1" defaultValue="62" /></label>
      <button type="submit">Start My Plan</button>
    </form>
  </div>
);

export default App;
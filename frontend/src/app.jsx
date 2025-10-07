import React, { useState, useEffect } from 'react';

// CSS is embedded directly to avoid import/build issues.
const styles = `
:root {
  --primary-color: #007bff;
  --background-color: #f4f7f6;
  --font-color: #333;
  --bot-bubble-color: #e9e9eb;
  --user-bubble-color: #007bff;
  --card-color: #ffffff;
  --border-radius: 12px;
}
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--background-color);
  color: var(--font-color);
}
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  border-left: 1px solid #ddd;
  border-right: 1px solid #ddd;
  background-color: #fff;
}
header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
}
.content {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.goal-view, .chat-view {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 1rem;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form label {
  display: flex;
  flex-direction: column;
  font-weight: bold;
  font-size: 0.9rem;
}
.form input, .form select {
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: var(--border-radius);
  margin-top: 0.25rem;
  font-size: 1rem;
}
.form button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: var(--border-radius);
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}
.chat-window {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.msg {
  display: flex;
  flex-direction: column;
}
.msg.bot {
  align-items: flex-start;
}
.msg.user {
  align-items: flex-end;
}
.text-bubble {
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius);
  max-width: 80%;
  line-height: 1.4;
}
.msg.bot .text-bubble {
  background-color: var(--bot-bubble-color);
  color: var(--font-color);
}
.msg.user .text-bubble {
  background-color: var(--user-bubble-color);
  color: white;
}
.card-bubble {
  background-color: var(--card-color);
  border: 1px solid #eee;
  padding: 1rem;
  border-radius: var(--border-radius);
  max-width: 90%;
  overflow-x: auto;
  margin-top: 0.5rem;
}
pre {
  margin: 0;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.input-form {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}
.input-form input {
  flex-grow: 1;
  border: 1px solid #ccc;
  padding: 0.8rem;
  border-radius: var(--border-radius);
  font-size: 1rem;
}
.input-form button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.8rem 1.2rem;
  border-radius: var(--border-radius);
  font-size: 1rem;
  cursor: pointer;
}
footer {
  padding: 1rem;
  background-color: #f1f1f1;
  text-align: center;
  font-size: 0.9rem;
  color: #555;
  cursor: pointer;
  border-top: 1px solid #ddd;
}
`;

function App() {
  const [view, setView] = useState("goal");
  const [profile, setProfile] = useState({
    age: 61, sex: "F", height_cm: 158, weight_kg: 72, 
    target_weight_kg: 62,
    activity: "light", conditions: ["type2_diabetes"], diet: "no_pork"
  });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const userId = "demo";

  useEffect(() => {
    const styleElement = document.createElement("style");
    styleElement.innerHTML = styles;
    document.head.appendChild(styleElement);
    return () => {
      document.head.removeChild(styleElement);
    };
  }, []);

  async function submitGoal(e) {
    e && e.preventDefault();
    const res = await fetch("/api/goal", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({user_id: userId, profile})
    });

    if (!res.ok) {
        const err = await res.json();
        const errorText = err.detail ? JSON.stringify(err.detail) : "An unknown error occurred.";
        setMessages(prev => [...prev, {role:"bot", text: `Error: ${res.status} - ${errorText}`}]);
        return;
    }

    const j = await res.json();
    setMessages(prev => [...prev, {role:"bot", text: j.text}, ...(j.cards || []).map(c => ({role:"bot", card:c}))]);
    setView("chat");
  }

  async function sendMessage(e) {
    e && e.preventDefault();
    if(!input) return;
    const userInput = input;
    setInput("");
    setMessages(prev => [...prev, {role:"user", text: userInput}]);
    const res = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({user_id: userId, message: userInput})
    });
    const j = await res.json();
    setMessages(prev => [...prev, {role:"bot", text: j.text}, ...(j.cards || []).map(c=>({role:"bot", card:c}))]);
  }

  return (
    <div className="app">
      <header><h1>AVA — Health Coach</h1></header>
      <div className="content">
        {view === "goal" && (
          <main className="goal-view">
            <h2>Set Your Goal</h2>
            <form onSubmit={submitGoal} className="form">
              <label>Age <input type="number" value={profile.age} onChange={e=>setProfile({...profile, age:+e.target.value})} /></label>
              <label>Sex <select value={profile.sex} onChange={e=>setProfile({...profile, sex:e.target.value})}><option value="F">Female</option><option value="M">Male</option></select></label>
              <label>Height (cm) <input type="number" value={profile.height_cm} onChange={e=>setProfile({...profile, height_cm:+e.target.value})} /></label>
              <label>Current Weight (kg) <input type="number" value={profile.weight_kg} onChange={e=>setProfile({...profile, weight_kg:+e.target.value})} /></label>
              <label>Target Weight (kg) <input type="number" value={profile.target_weight_kg} onChange={e=>setProfile({...profile, target_weight_kg:+e.target.value})} /></label>
              <label>Activity Level
                <select value={profile.activity} onChange={e=>setProfile({...profile, activity:e.target.value})}>
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="active">Active</option>
                </select>
              </label>
              <button type="submit">Create My Plan</button>
            </form>
          </main>
        )}

        {view === "chat" && (
          <main className="chat-view">
            <section className="chat-window">
              {messages.map((m, i) => (
                <div key={i} className={`msg ${m.role}`}>
                  {m.text && <div className="text-bubble">{m.text}</div>}
                  {m.card && <div className="card-bubble"><pre>{JSON.stringify(m.card, null, 2)}</pre></div>}
                </div>
              ))}
            </section>
            <form onSubmit={sendMessage} className="input-form">
              <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask a follow-up question..." />
              <button type="submit">Send</button>
            </form>
          </main>
        )}
      </div>
      <footer onClick={() => setView(view === 'goal' ? 'chat' : 'goal')}>
          Switch to {view === 'goal' ? 'Chat' : 'Goal'} View
      </footer>
    </div>
  );
}

export default App;


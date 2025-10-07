// frontend/src/app.jsx
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import "./app.css";

function App() {
  const [view, setView] = useState("goal");
  const [profile, setProfile] = useState({
    age: 61, sex: "F", height_cm: 158, weight_kg: 72, target_weight: 62, activity: "light", conditions: ["type2_diabetes"], diet: "no_pork"
  });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const userId = "demo";

  async function submitGoal(e) {
    e && e.preventDefault();
    const res = await fetch("/api/goal", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({user_id: userId, profile})
    });
    const j = await res.json();
    setMessages(prev => [...prev, {role:"bot", text: j.text}, ...(j.cards || []).map(c => ({role:"bot", card:c}))]);
    setView("chat");
  }

  async function sendMessage(e) {
    e && e.preventDefault();
    if(!input) return;
    setMessages(prev => [...prev, {role:"user", text: input}]);
    const res = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({user_id: userId, message: input})
    });
    const j = await res.json();
    setMessages(prev => [...prev, {role:"bot", text: j.text}, ...(j.cards || []).map(c=>({role:"bot", card:c}))]);
    setInput("");
  }

  return (
    <div className="app">
      <header><h1>Company A — Weight Coach</h1></header>
      <nav>
        <button onClick={()=>setView("goal")}>Set Goal</button>
        <button onClick={()=>setView("chat")}>Chat</button>
      </nav>

      {view === "goal" && (
        <main>
          <form onSubmit={submitGoal} className="form">
            <label>Age <input type="number" value={profile.age} onChange={e=>setProfile({...profile, age:+e.target.value})} /></label>
            <label>Sex <select value={profile.sex} onChange={e=>setProfile({...profile, sex:e.target.value})}><option>F</option><option>M</option></select></label>
            <label>Height (cm) <input type="number" value={profile.height_cm} onChange={e=>setProfile({...profile, height_cm:+e.target.value})} /></label>
            <label>Weight (kg) <input type="number" value={profile.weight_kg} onChange={e=>setProfile({...profile, weight_kg:+e.target.value})} /></label>
            <label>Target weight (kg) <input type="number" value={profile.target_weight} onChange={e=>setProfile({...profile, target_weight:+e.target.value})} /></label>
            <label>Activity
              <select value={profile.activity} onChange={e=>setProfile({...profile, activity:e.target.value})}>
                <option value="sedentary">Sedentary</option>
                <option value="light">Light</option>
                <option value="moderate">Moderate</option>
                <option value="active">Active</option>
              </select>
            </label>
            <button type="submit">Set Goal</button>
          </form>
        </main>
      )}

      {view === "chat" && (
        <main>
          <section className="chat">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                {m.text && <div className="text">{m.text}</div>}
                {m.card && <pre className="card">{JSON.stringify(m.card, null, 2)}</pre>}
              </div>
            ))}
          </section>
          <form onSubmit={sendMessage} className="input">
            <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Say something..." />
            <button type="submit">Send</button>
          </form>
        </main>
      )}
      <footer>Today Card: Nudges will appear here. — Example: 30 min walk, drink 2L water.</footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

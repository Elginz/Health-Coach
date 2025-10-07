import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [goalSet, setGoalSet] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [todayCard, setTodayCard] = useState(null);
  const [weights, setWeights] = useState([]);

  useEffect(() => {
    if (goalSet) {
      fetchTodayCard();
      fetchWeights();
    }
  }, [goalSet]);

  const handleGoalSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const profile = {
      age: parseInt(formData.get("age")),
      sex: formData.get("sex") || "F",
      height_cm: parseInt(formData.get("height")),
      weight_kg: parseFloat(formData.get("currentWeight")),
      target_weight_kg: parseFloat(formData.get("targetWeight")),
      activity: formData.get("activity") || "light",
    };

    const resp = await fetch("/api/goal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "demo", profile }),
    });
    const data = await resp.json();
    setMessages([{ from: "ava", text: data.text }]);
    setGoalSet(true);
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    const userMsg = { from: "user", text: userInput };
    setMessages((m) => [...m, userMsg]);
    setUserInput("");

    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "demo", message: userInput }),
    });
    const data = await resp.json();
    setMessages((m) => [...m, { from: "ava", text: data.text }]);
  };

  const fetchTodayCard = async () => {
    try {
      const resp = await fetch("/api/today");
      if (!resp.ok) return;
      const d = await resp.json();
      setTodayCard(d);
    } catch (e) {
      // ignore
    }
  };

  const fetchWeights = async () => {
    try {
      const resp = await fetch("/api/logs?user_id=demo");
      if (!resp.ok) return;
      const d = await resp.json();
      setWeights(d || []);
    } catch (e) {}
  };

  // quick log weight
  const quickLog = async (weight) => {
    const date = new Date().toISOString().slice(0, 10);
    await fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "demo", date, weight_kg: weight }),
    });
    fetchWeights();
  };

  if (!goalSet) {
    return <GoalForm onSubmit={handleGoalSubmit} />;
  }

  return (
    <div className="chat-container">
      <h1>Chat with AVA</h1>

      {todayCard && <TodayCard card={todayCard} onQuickLog={() => quickLog(weights.length ? weights[weights.length - 1].weight_kg : 0)} />}

      <div className="message-list">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.from}`}>
            {msg.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleChatSubmit} className="message-form">
        <input value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="Ask AVA something..." />
        <button type="submit">Send</button>
      </form>

      <ProgressWidget weights={weights} onLog={(w) => quickLog(w)} />
    </div>
  );
}

function GoalForm({ onSubmit }) {
  return (
    <div className="form-container">
      <h2>Set Your Goal</h2>
      <form onSubmit={onSubmit}>
        <label>
          Age: <input name="age" type="number" defaultValue="61" />
        </label>
        <label>
          Sex:
          <select name="sex" defaultValue="F">
            <option value="F">Female</option>
            <option value="M">Male</option>
          </select>
        </label>
        <label>
          Height (cm): <input name="height" type="number" defaultValue="158" />
        </label>
        <label>
          Current Weight (kg): <input name="currentWeight" type="number" step="0.1" defaultValue="72" />
        </label>
        <label>
          Target Weight (kg): <input name="targetWeight" type="number" step="0.1" defaultValue="62" />
        </label>
        <label>
          Activity:
          <select name="activity" defaultValue="light">
            <option value="sedentary">Sedentary</option>
            <option value="light">Light</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
          </select>
        </label>
        <button type="submit">Start My Plan</button>
      </form>
    </div>
  );
}

function TodayCard({ card = {}, onQuickLog }) {
  // card could be { text, cards: [...], actions: [...] } from /api/today
  const title = card.title || "Today";
  const body = card.body || card.text || "Keep to your calorie target. Move for 30 minutes.";
  return (
    <div className="today-card">
      <h3>{title}</h3>
      <p>{body}</p>
      <div className="today-actions">
        <button onClick={() => onQuickLog()}>Quick Log</button>
      </div>
    </div>
  );
}

function ProgressWidget({ weights = [], onLog }) {
  // Simple textual progress + mini sparkline (ASCII-style)
  const last = weights.length ? weights[weights.length - 1].weight_kg : null;
  const first = weights.length ? weights[0].weight_kg : null;
  const delta = last && first ? (last - first).toFixed(1) : null;

  return (
    <div className="progress-widget">
      <h4>Progress</h4>
      {weights.length === 0 ? (
        <p>No logs yet.</p>
      ) : (
        <>
          <p>
            Latest: {last} kg {delta ? `(${delta} kg since first)` : ""}
          </p>
          <div className="weights-list">
            {weights.map((w, i) => (
              <div key={i} className="weight-item">
                <small>{w.date}</small>
                <div>{w.weight_kg} kg</div>
              </div>
            ))}
          </div>
          <div className="progress-actions">
            <button onClick={() => onLog(Math.round((last - 0.1) * 10) / 10)}>Log -0.1kg (test)</button>
            <button onClick={() => onLog(Math.round((last + 0.1) * 10) / 10)}>Log +0.1kg (test)</button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;

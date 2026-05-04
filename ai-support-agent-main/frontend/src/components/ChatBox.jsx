import { useState, useEffect, useRef } from "react";
import { sendMessage } from "../services/api";
import Message from "./Message";
import MemoryTimeline from "./MemoryTimeline";

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [memory, setMemory] = useState([]);
  const chatEndRef = useRef(null);

  const handleSend = async () => {
    if (!input) return;

    const userMsg = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMsg]);

    const res = await sendMessage({
      user_id: "user1",
      message: input,
    });

    if (res) {
      const botMsg = { text: res.response, sender: "bot" };

      setMessages((prev) => [...prev, botMsg]);
      setMemory(res.memory_used || []);
    }

    setInput("");
  };

  // auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div style={{
      maxWidth: "700px",
      margin: "40px auto",
      padding: "20px",
      borderRadius: "15px",
      boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
      background: "#f9f9f9"
    }}>
      <h2 style={{ textAlign: "center" }}>🤖 AI Support Agent</h2>

      {/* Chat Window */}
      <div style={{
        height: "350px",
        overflowY: "auto",
        padding: "10px",
        borderRadius: "10px",
        background: "#fff",
        border: "1px solid #ddd"
      }}>
        {messages.map((msg, i) => (
          <Message key={i} text={msg.text} sender={msg.sender} />
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* Input Box */}
      <div style={{ display: "flex", marginTop: "10px" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: "12px",
            borderRadius: "10px",
            border: "1px solid #ccc",
            outline: "none"
          }}
        />

        <button
          onClick={handleSend}
          style={{
            marginLeft: "10px",
            padding: "12px 20px",
            borderRadius: "10px",
            border: "none",
            background: "#4CAF50",
            color: "#fff",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          Send
        </button>
      </div>

      {/* Memory Section */}
      <MemoryTimeline memory={memory} />
    </div>
  );
};

export default ChatBox;
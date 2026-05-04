const Message = ({ text, sender }) => {
  const isUser = sender === "user";

  return (
    <div style={{
      display: "flex",
      justifyContent: isUser ? "flex-end" : "flex-start",
      margin: "8px 0"
    }}>
      <div style={{
        maxWidth: "70%",
        padding: "12px",
        borderRadius: "15px",
        background: isUser ? "#4CAF50" : "#e5e5ea",
        color: isUser ? "#fff" : "#000",
        boxShadow: "0 2px 5px rgba(0,0,0,0.1)"
      }}>
        {text}
      </div>
    </div>
  );
};

export default Message;